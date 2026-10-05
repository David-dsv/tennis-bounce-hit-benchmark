"""
MULTI-CLIP bounce/hit arbitration evaluator — pooled scoring across a corpus.

The paper (docs/paper/rallyarb.tex §IV) evaluates on ONE clip (demo3) with the
joint bounce/hit cross matcher of tools/event_eval/event_eval.py. This harness
scales that to N clips WITHOUT touching the matcher: per-clip scoring reuses
`match_events` + `scores` from event_eval.py UNCHANGED, so every number stays
directly comparable with the paper and with tests/test_event_confusion_regression.py
(greedy 1-1 over BOTH GTs at once, tolerance round(0.15*fps), nearest-first,
same-class-first tie-break, confusion doubly penalized: FP for the predicted
class AND FN for the GT class).

NOTE (latent, inherited AS-IS for comparability — see
tests/test_event_eval.py::test_tie_break_documented_behavior): in the canonical
matcher the §5.2 same-class tie-break never actually fires (pred labels
"BOUNCE"/"HIT" are compared to gt classes "bounce"/"shot"); exact-distance ties
fall through to the stable (frame, uid) order. Never observed on real GT.

MANIFEST FORMAT (JSON) — the single input of the CLI:

    {
      "clips": [
        {
          "clip":  "tennis_demo3",              // display name (required)
          "pred":  "preds/tennis_demo3.json",   // predictions JSON (required)
          "gt":    "gt/tennis_demo3.events_gt.json",  // ground truth (required)
          "gt_shots": "gt/tennis_demo3.shots.json",   // OPTIONAL: legacy shots
                       // sidecar, only meaningful when "gt" is a bounces-only
                       // file (tests/fixtures/bounces schema)
          "split": "dev",                       // "dev" | "test" (default "dev")
          "fps":   50.0,                        // OPTIONAL override; otherwise
                                                // read from gt, then pred
          "notes": "...", "camera": "oblique"   // any extra keys = free-form
                                                // annotations, echoed in --json
        },
        ...
      ]
    }

Relative paths are resolved against the manifest file's directory.

GT FORMATS accepted for "gt":
  1. Events sidecar `<video>.events_gt.json`:
       {video, fps, events: [{frame, label: "B"|"H", tag?, player?, stroke?}]}
     `label` also accepts "BOUNCE"/"HIT" (any case). `tag` may be a string or a
     list of strings (e.g. "serve", "toss"); an optional `tags` list is merged.
  2. Legacy bounces-only fixture (tests/fixtures/bounces schema):
       {video, fps, bounces: [{frame, x, y, ...}]}
     Optionally paired with a shots fixture via the manifest key "gt_shots":
       {fps, shots: [{frame, x, y, type}]}

PRED FORMAT: same as event_eval.load_pred_events —
  {fps?, events:[{frame, label}]} or separate {bounces:[...], shots:[...]}
  arrays; labels "B"/"H" are accepted and normalized.

TAG EXCLUSION (--exclude-tags serve,toss — default: everything included):
  Matching always runs with the FULL GT pool (excluded events included), then
  exclusion is applied post-hoc:
    - an excluded GT event counts neither as TP nor as FN;
    - a prediction matched to an excluded GT event is IGNORED (removed from the
      pool entirely — it is NOT spurious and NOT an FP).
  This is the "with/without off-policy events (serve, toss)" scoring mode.

OUTPUT: aligned per-clip table + POOLED micro-average (sums of TP/FP/FN over
all events of all clips) + confusion totals + a bootstrap 95% CI on the pooled
F1s (resampling CLIPS, not events — clips are the correlation unit; 10000
iterations, fixed seed). `--json` emits the whole report as JSON.

Usage:
    python eval/eval_multiclip.py --manifest eval/manifest.json \
        [--split dev|test|all] [--exclude-tags serve,toss] [--json] \
        [--bootstrap-iters 10000] [--seed 20260901] [--tolerance-frames N]
"""

import argparse
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

# Self-contained release copy: the matcher lives next to this file (eval/event_eval.py).
_HERE = str(Path(__file__).resolve().parent)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

# The canonical §IV matcher — reused UNCHANGED for comparability.
from event_eval import (  # noqa: E402
    BOUNCE, HIT, match_events, scores, load_pred_events)

DEFAULT_SEED = 20260901
DEFAULT_ITERS = 10000
MIN_CLIPS_FOR_CI = 4

_LABELS = {
    "B": BOUNCE, "BOUNCE": BOUNCE,
    "H": HIT, "HIT": HIT, "S": HIT, "SHOT": HIT,
}


def normalize_label(lab):
    """Map "B"/"H"/"bounce"/"hit"/... to the matcher's BOUNCE/HIT constants."""
    key = str(lab).strip().upper()
    if key not in _LABELS:
        raise ValueError(f"unknown event label {lab!r} (expected B/H/BOUNCE/HIT)")
    return _LABELS[key]


def _tags_of(ev):
    """Collect the tag set of a GT event: 'tag' (str or list) + 'tags' (list)."""
    out = set()
    t = ev.get("tag")
    if isinstance(t, str) and t:
        out.add(t.strip().lower())
    elif isinstance(t, (list, tuple)):
        out.update(str(x).strip().lower() for x in t if x)
    for x in ev.get("tags", []) or []:
        out.add(str(x).strip().lower())
    return out


def load_gt(gt_path, gt_shots_path=None):
    """Load a GT file in either supported format.

    Returns (fps_or_None, gt_bounces, gt_hits) where each GT event is
    {"frame": int, "tags": set[str]}.
    """
    doc = json.loads(Path(gt_path).read_text())
    if "events" in doc:  # events_gt sidecar
        gt_b, gt_h = [], []
        for e in doc["events"]:
            lab = normalize_label(e["label"])
            rec = {"frame": int(e["frame"]), "tags": _tags_of(e)}
            (gt_b if lab == BOUNCE else gt_h).append(rec)
        return doc.get("fps"), gt_b, gt_h
    if "bounces" not in doc:
        raise ValueError(f"{gt_path}: neither 'events' nor 'bounces' key — unknown GT format")
    # legacy bounces-only fixture (tests/fixtures/bounces schema)
    fps = doc.get("fps")
    gt_b = [{"frame": int(b["frame"]), "tags": _tags_of(b)} for b in doc["bounces"]]
    gt_h = []
    if gt_shots_path:
        sd = json.loads(Path(gt_shots_path).read_text())
        fps = fps if fps is not None else sd.get("fps")
        gt_h = [{"frame": int(s["frame"]), "tags": _tags_of(s)} for s in sd["shots"]]
    return fps, gt_b, gt_h


def load_predictions(pred_path):
    """load_pred_events + label normalization ("B"/"H" accepted)."""
    doc, events = load_pred_events(pred_path)
    return doc, [{"frame": int(e["frame"]), "label": normalize_label(e["label"])}
                 for e in events]


def apply_tag_exclusions(res, excl_b_frames, excl_h_frames):
    """Post-filter a match_events result to remove tag-excluded GT events.

    Matching ran with the FULL GT pool, so predictions could be absorbed by
    excluded events; here:
      - a matched pair whose GT event is excluded is dropped AND its prediction
        is ignored entirely (not spurious, not FP);
      - an excluded GT event left unmatched is removed from the FN list;
      - n_gt_* are reduced accordingly.
    Frame multisets (Counter) handle duplicate GT frames; when an excluded and
    an included GT event share the same class+frame, the excluded one is
    consumed by the matched pair first (conservative, deterministic).
    Returns a NEW result dict with the same shape as match_events (so
    event_eval.scores applies unchanged) + an "ignored_preds" list.
    """
    excl = {"bounce": Counter(excl_b_frames), "shot": Counter(excl_h_frames)}
    kept_pairs, ignored = [], []
    for p in res["pairs"]:
        c = excl[p["gt_class"]]
        if c[p["gt_frame"]] > 0:
            c[p["gt_frame"]] -= 1
            ignored.append((p["pred_frame"], p["pred_label"]))
        else:
            kept_pairs.append(p)
    fn_b, fn_h = [], []
    for f in res["FN_b"]:
        if excl["bounce"][f] > 0:
            excl["bounce"][f] -= 1
        else:
            fn_b.append(f)
    for f in res["FN_h"]:
        if excl["shot"][f] > 0:
            excl["shot"][f] -= 1
        else:
            fn_h.append(f)
    # re-tally the confusion counts exactly as match_events does
    m = {"TP_b": 0, "TP_h": 0, "conf_BtoH": 0, "conf_HtoB": 0}
    for p in kept_pairs:
        if p["gt_class"] == "bounce":
            m["TP_b" if p["pred_label"] == BOUNCE else "conf_BtoH"] += 1
        else:
            m["TP_h" if p["pred_label"] == HIT else "conf_HtoB"] += 1
    return {
        "pairs": kept_pairs,
        "TP_b": m["TP_b"],
        "TP_h": m["TP_h"],
        "conf_BtoH": m["conf_BtoH"],
        "conf_HtoB": m["conf_HtoB"],
        "FN_b": fn_b,
        "FN_h": fn_h,
        "spurious": res["spurious"],  # unmatched preds are unaffected
        "n_gt_b": res["n_gt_b"] - len(excl_b_frames),
        "n_gt_h": res["n_gt_h"] - len(excl_h_frames),
        "ignored_preds": ignored,
    }


def score_clip(pred_events, gt_b, gt_h, fps, exclude_tags=(), tolerance=None):
    """Score one clip with the canonical matcher + tag exclusion.

    gt_b / gt_h: lists of {"frame": int, "tags": set[str]} (from load_gt).
    Returns (res, scores_dict, tol).
    """
    tol = tolerance if tolerance is not None else round(0.15 * float(fps))
    res = match_events(
        pred_events,
        [g["frame"] for g in gt_b],
        [g["frame"] for g in gt_h],
        tol,
    )
    ex = {str(t).strip().lower() for t in exclude_tags if str(t).strip()}
    excl_b = [g["frame"] for g in gt_b if g["tags"] & ex] if ex else []
    excl_h = [g["frame"] for g in gt_h if g["tags"] & ex] if ex else []
    res = apply_tag_exclusions(res, excl_b, excl_h)
    return res, scores(res), tol


def clip_counts(res, s):
    """The 8 micro-average counters of one clip (bootstrap resampling unit)."""
    return {
        "b_tp": s["bounce"]["tp"], "b_fp": s["bounce"]["fp"], "b_fn": s["bounce"]["fn"],
        "h_tp": s["hit"]["tp"], "h_fp": s["hit"]["fp"], "h_fn": s["hit"]["fn"],
        "conf_HtoB": res["conf_HtoB"], "conf_BtoH": res["conf_BtoH"],
        "spurious": len(res["spurious"]),
        "ignored": len(res.get("ignored_preds", [])),
        "n_gt_b": res["n_gt_b"], "n_gt_h": res["n_gt_h"],
    }


def _prf(tp, fp, fn):
    # provenance: tools/event_eval/event_eval.py::_prf (private there; copied
    # verbatim so pooled math is IDENTICAL to per-clip math).
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * p * r / (p + r)) if (p + r) else 0.0
    return p, r, f1


def pool_counts(counts_list):
    """Micro-average: sum the counters over clips, recompute P/R/F1."""
    tot = Counter()
    for c in counts_list:
        tot.update(c)
    bp, br, bf1 = _prf(tot["b_tp"], tot["b_fp"], tot["b_fn"])
    hp, hr, hf1 = _prf(tot["h_tp"], tot["h_fp"], tot["h_fn"])
    return {
        "bounce": {"tp": tot["b_tp"], "fp": tot["b_fp"], "fn": tot["b_fn"],
                   "P": bp, "R": br, "F1": bf1},
        "hit": {"tp": tot["h_tp"], "fp": tot["h_fp"], "fn": tot["h_fn"],
                "P": hp, "R": hr, "F1": hf1},
        "conf_HtoB": tot["conf_HtoB"], "conf_BtoH": tot["conf_BtoH"],
        "spurious": tot["spurious"], "ignored": tot["ignored"],
        "n_gt_b": tot["n_gt_b"], "n_gt_h": tot["n_gt_h"],
    }


def _percentile(sorted_vals, q):
    if not sorted_vals:
        return 0.0
    idx = q * (len(sorted_vals) - 1)
    lo, hi = int(math.floor(idx)), int(math.ceil(idx))
    frac = idx - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


def bootstrap_ci(counts_list, n_iters=DEFAULT_ITERS, seed=DEFAULT_SEED):
    """Bootstrap 95% CI on the POOLED bounce/hit F1.

    Resamples CLIPS with replacement (clips are the correlation unit — events
    within a clip are not independent), n_iters iterations, fixed seed for
    determinism. Returns {"bounce_f1": (lo, hi), "hit_f1": (lo, hi),
    "n_clips": N, "n_iters": ..., "seed": ..., "narrow_valid": bool}.
    """
    n = len(counts_list)
    rng = random.Random(seed)
    bf1s, hf1s = [], []
    for _ in range(n_iters):
        sample = [counts_list[rng.randrange(n)] for _ in range(n)]
        p = pool_counts(sample)
        bf1s.append(p["bounce"]["F1"])
        hf1s.append(p["hit"]["F1"])
    bf1s.sort()
    hf1s.sort()
    return {
        "bounce_f1": (_percentile(bf1s, 0.025), _percentile(bf1s, 0.975)),
        "hit_f1": (_percentile(hf1s, 0.025), _percentile(hf1s, 0.975)),
        "n_clips": n,
        "n_iters": n_iters,
        "seed": seed,
        "narrow_valid": n >= MIN_CLIPS_FOR_CI,
    }


def load_manifest(manifest_path):
    """Load a manifest; resolve relative paths against the manifest's dir."""
    mp = Path(manifest_path)
    doc = json.loads(mp.read_text())
    base = mp.resolve().parent
    clips = []
    for i, c in enumerate(doc.get("clips", [])):
        if "clip" not in c or "pred" not in c or "gt" not in c:
            raise ValueError(f"manifest clip #{i}: 'clip', 'pred' and 'gt' are required")
        entry = dict(c)
        for key in ("pred", "gt", "gt_shots"):
            if entry.get(key):
                p = Path(entry[key])
                entry[key] = str(p if p.is_absolute() else base / p)
        entry.setdefault("split", "dev")
        if entry["split"] not in ("dev", "test"):
            raise ValueError(f"manifest clip {entry['clip']}: split must be dev|test")
        clips.append(entry)
    if not clips:
        raise ValueError(f"{manifest_path}: empty manifest (no 'clips')")
    return clips


def evaluate_manifest(clips, split="all", exclude_tags=(), tolerance=None,
                      bootstrap_iters=DEFAULT_ITERS, seed=DEFAULT_SEED):
    """Full evaluation: per-clip results + pooled micro-average + bootstrap CI.

    Returns a JSON-serializable report dict.
    """
    selected = [c for c in clips if split == "all" or c["split"] == split]
    if not selected:
        raise ValueError(f"no clip matches split={split!r}")
    per_clip = []
    counts_list = []
    for c in selected:
        fps_gt, gt_b, gt_h = load_gt(c["gt"], c.get("gt_shots"))
        pred_doc, pred_events = load_predictions(c["pred"])
        fps = c.get("fps") or fps_gt or pred_doc.get("fps")
        if not fps:
            raise ValueError(f"clip {c['clip']}: fps not found (manifest/gt/pred)")
        res, s, tol = score_clip(pred_events, gt_b, gt_h, fps,
                                 exclude_tags=exclude_tags, tolerance=tolerance)
        cc = clip_counts(res, s)
        counts_list.append(cc)
        extra = {k: v for k, v in c.items()
                 if k not in ("clip", "pred", "gt", "gt_shots", "split", "fps")}
        per_clip.append({
            "clip": c["clip"], "split": c["split"], "fps": float(fps), "tol": tol,
            "counts": cc,
            "bounce": s["bounce"], "hit": s["hit"],
            "conf_HtoB": res["conf_HtoB"], "conf_BtoH": res["conf_BtoH"],
            "spurious": [list(x) for x in res["spurious"]],
            "ignored_preds": [list(x) for x in res.get("ignored_preds", [])],
            "FN_b": res["FN_b"], "FN_h": res["FN_h"],
            "annotations": extra,
        })
    pooled = pool_counts(counts_list)
    boot = bootstrap_ci(counts_list, n_iters=bootstrap_iters, seed=seed)
    return {
        "split": split,
        "exclude_tags": sorted({str(t).strip().lower() for t in exclude_tags
                                if str(t).strip()}),
        "tolerance_policy": ("fixed" if tolerance is not None
                             else "round(0.15*fps)"),
        "clips": per_clip,
        "pooled": pooled,
        "bootstrap": boot,
    }


def _fmt_prf(d):
    return f"{d['P']:5.3f} {d['R']:5.3f} {d['F1']:5.3f}"


def print_report(report):
    ex = ",".join(report["exclude_tags"]) or "-"
    print(f"== MULTI-CLIP EVENT EVAL == split={report['split']}  "
          f"exclude_tags={ex}  tol={report['tolerance_policy']}")
    name_w = max(4, max(len(c["clip"]) for c in report["clips"]))
    hdr = (f"{'clip':<{name_w}}  {'split':<5} {'tol':>3} {'nB':>3} {'nH':>3} | "
           f"{'bounce P':>8} {'R':>5} {'F1':>5} | {'hit P':>6} {'R':>5} {'F1':>5} | "
           f"{'H>B':>3} {'B>H':>3} {'spur':>4} {'ign':>3}")
    print(hdr)
    print("-" * len(hdr))
    for c in report["clips"]:
        b, h = c["bounce"], c["hit"]
        print(f"{c['clip']:<{name_w}}  {c['split']:<5} {c['tol']:>3} "
              f"{c['counts']['n_gt_b']:>3} {c['counts']['n_gt_h']:>3} | "
              f"{_fmt_prf(b):>20} | {_fmt_prf(h):>18} | "
              f"{c['conf_HtoB']:>3} {c['conf_BtoH']:>3} "
              f"{c['counts']['spurious']:>4} {c['counts']['ignored']:>3}")
    p = report["pooled"]
    print("-" * len(hdr))
    print(f"{'POOLED (micro)':<{name_w}}  {'':<5} {'':>3} "
          f"{p['n_gt_b']:>3} {p['n_gt_h']:>3} | "
          f"{_fmt_prf(p['bounce']):>20} | {_fmt_prf(p['hit']):>18} | "
          f"{p['conf_HtoB']:>3} {p['conf_BtoH']:>3} "
          f"{p['spurious']:>4} {p['ignored']:>3}")
    boot = report["bootstrap"]
    blo, bhi = boot["bounce_f1"]
    hlo, hhi = boot["hit_f1"]
    print(f"bootstrap 95% CI ({boot['n_iters']} iters, seed {boot['seed']}, "
          f"clip-level resampling, n_clips={boot['n_clips']}):")
    print(f"  bounce F1 in [{blo:.3f}, {bhi:.3f}]")
    print(f"  hit    F1 in [{hlo:.3f}, {hhi:.3f}]")
    if not boot["narrow_valid"]:
        print(f"  WARNING: only {boot['n_clips']} clip(s) < {MIN_CLIPS_FOR_CI} — "
              f"the CI is degenerate/very wide; interpret with caution.")


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="Multi-clip bounce/hit arbitration evaluator "
                    "(pooled micro-average + bootstrap CI). See the module "
                    "docstring for the manifest format.")
    p.add_argument("--manifest", required=True, help="Manifest JSON (see docstring).")
    p.add_argument("--split", choices=("dev", "test", "all"), default="all")
    p.add_argument("--exclude-tags", default="",
                   help="Comma-separated GT tags to exclude (e.g. serve,toss). "
                        "Default: everything included.")
    p.add_argument("--tolerance-frames", type=int, default=None,
                   help="Fixed match window; default = round(0.15*fps) per clip.")
    p.add_argument("--bootstrap-iters", type=int, default=DEFAULT_ITERS)
    p.add_argument("--seed", type=int, default=DEFAULT_SEED)
    p.add_argument("--json", action="store_true", help="Emit the report as JSON.")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    tags = [t for t in args.exclude_tags.split(",") if t.strip()]
    clips = load_manifest(args.manifest)
    report = evaluate_manifest(
        clips, split=args.split, exclude_tags=tags,
        tolerance=args.tolerance_frames,
        bootstrap_iters=args.bootstrap_iters, seed=args.seed)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_report(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
