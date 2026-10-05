#!/usr/bin/env python3
"""
Inter-annotator agreement between two event ground-truth sidecars.

Takes two `<clip>.events_gt.json` files (annotator A1 = reference, annotator
A2 = second blind pass) and measures how well they agree, using EXACTLY the
matching semantics of the benchmark evaluator (eval/event_eval.py):

  * one greedy 1-1 cross matcher over BOTH classes at once, nearest frame
    first, tolerance = round(0.15 * fps) frames (or --tolerance-frames);
  * A2 plays the role of "predictions", A1 the role of "ground truth", so the
    per-class precision/recall/F1 reported here are the numbers a system
    would get if it reproduced A2 perfectly — F1 is symmetric under swapping
    the two annotators (P and R swap), so it is a fair agreement figure;
  * a matched pair whose labels differ (A1 says B, A2 says H) is a label
    disagreement; it is counted in the Cohen-style kappa over matched pairs
    AND penalised in P/R/F1 exactly like a confusion in the evaluator.

Reported, for two views:
  "all"      every event of both files counts;
  "untagged" events carrying any tag (or the tags given with --exclude-tags)
             are removed post-hoc on BOTH sides (a matched pair is dropped if
             EITHER member is tagged; an unmatched tagged event is dropped),
             i.e. the rally-only view the paper scores on.

Per view:
  - per-class P/R/F1 of A2 vs A1 (bounce, hit) + the 2x3 confusion matrix;
  - Cohen's kappa on the B/H label of matched pairs (+ raw agreement rate);
  - counts of events only in A1 (missed by A2) and only in A2 (extra);
  - frame-offset statistics of matched pairs (mean |d|, max |d|, histogram);
  - tag agreement on matched pairs, and, for matched HITs, player and
    stroke agreement rates (informative only; not part of the matcher).

Usage:
    python annotation/agreement.py A1.events_gt.json A2.events_gt.json
    python annotation/agreement.py A1.json A2.json --json out.json
    python annotation/agreement.py A1.json A2.json --exclude-tags far,dead
    python annotation/agreement.py A1.json A2.json --tolerance-frames 6

Only the standard library + eval/event_eval.py are needed.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

_EVAL_DIR = Path(__file__).resolve().parents[1] / "eval"
if str(_EVAL_DIR) not in sys.path:
    sys.path.insert(0, str(_EVAL_DIR))

from event_eval import BOUNCE, HIT, match_events, scores  # noqa: E402

_LABELS = {"B": BOUNCE, "BOUNCE": BOUNCE, "H": HIT, "HIT": HIT, "S": HIT, "SHOT": HIT}
_CLASS_OF = {BOUNCE: "bounce", HIT: "shot"}


def _norm_label(lab):
    key = str(lab).strip().upper()
    if key not in _LABELS:
        raise ValueError(f"unknown label {lab!r} (expected B/H)")
    return _LABELS[key]


def _tags_of(ev):
    out = set()
    t = ev.get("tag")
    if isinstance(t, str) and t:
        out.add(t.strip().lower())
    elif isinstance(t, (list, tuple)):
        out.update(str(x).strip().lower() for x in t if x)
    for x in ev.get("tags", []) or []:
        out.add(str(x).strip().lower())
    return out


def load_sidecar(path):
    """Load an events_gt sidecar -> (header dict, list of normalized events).

    Each event: {"frame", "label" (BOUNCE/HIT), "tags": set, "player", "stroke"}.
    """
    doc = json.loads(Path(path).read_text())
    if "events" not in doc:
        raise ValueError(f"{path}: no 'events' key — not an events_gt sidecar")
    evs = []
    for e in doc["events"]:
        evs.append({
            "frame": int(e["frame"]),
            "label": _norm_label(e["label"]),
            "tags": _tags_of(e),
            "player": e.get("player"),
            "stroke": e.get("stroke"),
        })
    evs.sort(key=lambda e: (e["frame"], e["label"]))
    hdr = {k: v for k, v in doc.items() if k != "events"}
    return hdr, evs


def _kappa(pairs):
    """Cohen's kappa over the B/H labels of matched pairs (A1 label vs A2 label)."""
    n = len(pairs)
    if n == 0:
        return {"n": 0, "agreement": None, "kappa": None}
    a1 = [("bounce" if p["gt_class"] == "bounce" else "shot") for p in pairs]
    a2 = [_CLASS_OF[p["pred_label"]] for p in pairs]
    po = sum(x == y for x, y in zip(a1, a2)) / n
    c1, c2 = Counter(a1), Counter(a2)
    pe = sum((c1[k] / n) * (c2[k] / n) for k in ("bounce", "shot"))
    kappa = (po - pe) / (1.0 - pe) if pe < 1.0 else 1.0
    return {"n": n, "agreement": po, "kappa": kappa}


def _index_events(evs):
    """Map (class, frame) -> list of events, in order (duplicates kept)."""
    idx = {}
    for e in evs:
        idx.setdefault((_CLASS_OF[e["label"]], e["frame"]), []).append(e)
    return idx


def compare(a1, a2, fps, tolerance=None, exclude_tags=None):
    """Compare two event lists. A1 = reference ("GT"), A2 = second annotator ("pred").

    exclude_tags: None -> "all" view (nothing removed); a set of tags ->
    events of EITHER annotator carrying one of them are removed post-hoc
    (pairs dropped if either member is tagged). An empty set means "remove
    every tagged event".
    Returns a JSON-serializable dict.
    """
    tol = tolerance if tolerance is not None else round(0.15 * float(fps))
    gt_b = [e for e in a1 if e["label"] == BOUNCE]
    gt_h = [e for e in a1 if e["label"] == HIT]
    pred = [{"frame": e["frame"], "label": e["label"]} for e in a2]
    res = match_events(pred, [e["frame"] for e in gt_b], [e["frame"] for e in gt_h], tol)

    # Recover the full records behind each matched pair / unmatched event so
    # tags, player and stroke can be compared. Duplicate (class, frame) keys
    # are consumed in order — the matcher keeps duplicates distinct too.
    idx1 = _index_events(a1)
    idx2 = _index_events(a2)
    pairs = []
    for p in res["pairs"]:
        e1 = idx1[(p["gt_class"], p["gt_frame"])].pop(0)
        e2 = idx2[(_CLASS_OF[p["pred_label"]], p["pred_frame"])].pop(0)
        pairs.append((p, e1, e2))
    only_a1 = [e for lst in idx1.values() for e in lst]
    only_a2 = [e for lst in idx2.values() for e in lst]

    def _excluded(e):
        if exclude_tags is None:
            return False
        if not exclude_tags:
            return bool(e["tags"])
        return bool(e["tags"] & exclude_tags)

    kept_pairs = [(p, e1, e2) for p, e1, e2 in pairs if not (_excluded(e1) or _excluded(e2))]
    dropped_pairs = len(pairs) - len(kept_pairs)
    only_a1 = [e for e in only_a1 if not _excluded(e)]
    only_a2 = [e for e in only_a2 if not _excluded(e)]

    # Re-tally a match_events-shaped result so event_eval.scores applies unchanged.
    m = {"TP_b": 0, "TP_h": 0, "conf_BtoH": 0, "conf_HtoB": 0}
    for p, _, _ in kept_pairs:
        if p["gt_class"] == "bounce":
            m["TP_b" if p["pred_label"] == BOUNCE else "conf_BtoH"] += 1
        else:
            m["TP_h" if p["pred_label"] == HIT else "conf_HtoB"] += 1
    fn_b = sorted(e["frame"] for e in only_a1 if e["label"] == BOUNCE)
    fn_h = sorted(e["frame"] for e in only_a1 if e["label"] == HIT)
    spurious = sorted((e["frame"], e["label"]) for e in only_a2)
    n1 = len(kept_pairs) + len(only_a1)
    n2 = len(kept_pairs) + len(only_a2)
    shaped = {
        "pairs": [p for p, _, _ in kept_pairs],
        **m,
        "FN_b": fn_b, "FN_h": fn_h, "spurious": spurious,
        "n_gt_b": sum(1 for p, _, _ in kept_pairs if p["gt_class"] == "bounce") + len(fn_b),
        "n_gt_h": sum(1 for p, _, _ in kept_pairs if p["gt_class"] == "shot") + len(fn_h),
    }
    sc = scores(shaped)

    # offsets + attribute agreement on matched pairs
    dists = [p["dist"] for p, _, _ in kept_pairs]
    signed = [p["pred_frame"] - p["gt_frame"] for p, _, _ in kept_pairs]
    hist = Counter(dists)
    tag_eq = sum(1 for _, e1, e2 in kept_pairs if e1["tags"] == e2["tags"])
    hits = [(e1, e2) for p, e1, e2 in kept_pairs
            if e1["label"] == HIT and e2["label"] == HIT]
    player_eq = sum(1 for e1, e2 in hits if e1["player"] == e2["player"])
    stroke_both = [(e1, e2) for e1, e2 in hits if e1["stroke"] and e2["stroke"]]
    stroke_eq = sum(1 for e1, e2 in stroke_both if e1["stroke"] == e2["stroke"])

    return {
        "tolerance_frames": tol,
        "n_a1": n1, "n_a2": n2,
        "n_a1_bounce": shaped["n_gt_b"], "n_a1_hit": shaped["n_gt_h"],
        "n_a2_bounce": sum(1 for _, _, e2 in kept_pairs if e2["label"] == BOUNCE)
                       + sum(1 for e in only_a2 if e["label"] == BOUNCE),
        "n_a2_hit": sum(1 for _, _, e2 in kept_pairs if e2["label"] == HIT)
                    + sum(1 for e in only_a2 if e["label"] == HIT),
        "matched": len(kept_pairs),
        "pairs_dropped_by_tag": dropped_pairs,
        "confusion": {"TP_b": m["TP_b"], "TP_h": m["TP_h"],
                      "A1_B_as_A2_H": m["conf_BtoH"], "A1_H_as_A2_B": m["conf_HtoB"],
                      "only_in_A1_bounce": len(fn_b), "only_in_A1_hit": len(fn_h),
                      "only_in_A2_bounce": sum(1 for _, l in spurious if l == BOUNCE),
                      "only_in_A2_hit": sum(1 for _, l in spurious if l == HIT)},
        "bounce": sc["bounce"], "hit": sc["hit"],
        "label_kappa": _kappa([p for p, _, _ in kept_pairs]),
        "only_in_A1": {"bounce": fn_b, "hit": fn_h},
        "only_in_A2": [[f, l] for f, l in spurious],
        "offset": {
            "mean_abs": (sum(dists) / len(dists)) if dists else None,
            "max_abs": max(dists) if dists else None,
            "mean_signed_a2_minus_a1": (sum(signed) / len(signed)) if signed else None,
            "exact_frame_rate": (hist[0] / len(dists)) if dists else None,
            "hist_abs": {str(k): hist[k] for k in sorted(hist)},
        },
        "attributes_on_matched": {
            "tag_agreement": (tag_eq / len(kept_pairs)) if kept_pairs else None,
            "hit_pairs": len(hits),
            "player_agreement": (player_eq / len(hits)) if hits else None,
            "stroke_pairs_both_set": len(stroke_both),
            "stroke_agreement": (stroke_eq / len(stroke_both)) if stroke_both else None,
        },
    }


def _f(x, w=5):
    return f"{x:{w}.3f}" if isinstance(x, float) else f"{str(x):>{w}}"


def print_table(report):
    print(f"== INTER-ANNOTATOR AGREEMENT == clip={report['clip']}  fps={report['fps']}  "
          f"tol=±{report['views']['all']['tolerance_frames']}f")
    print(f"A1: {report['a1_file']}  ({report['a1_annotator'] or '?'})")
    print(f"A2: {report['a2_file']}  ({report['a2_annotator'] or '?'})")
    hdr = (f"{'view':<9} {'nA1':>4} {'nA2':>4} {'match':>5} | {'bounce P':>8} {'R':>5} {'F1':>5} | "
           f"{'hit P':>6} {'R':>5} {'F1':>5} | {'B/H':>4} {'kappa':>6} | {'onlyA1':>6} {'onlyA2':>6} | "
           f"{'|d| mean':>8} {'exact':>5}")
    print(hdr)
    print("-" * len(hdr))
    for name, v in report["views"].items():
        k = v["label_kappa"]
        o = v["offset"]
        conf = v["confusion"]["A1_B_as_A2_H"] + v["confusion"]["A1_H_as_A2_B"]
        print(f"{name:<9} {v['n_a1']:>4} {v['n_a2']:>4} {v['matched']:>5} | "
              f"{_f(v['bounce']['P'])} {_f(v['bounce']['R'])} {_f(v['bounce']['F1'])}    | "
              f"{_f(v['hit']['P'])} {_f(v['hit']['R'])} {_f(v['hit']['F1'])}  | "
              f"{conf:>4} {_f(k['kappa'], 6)} | "
              f"{len(v['only_in_A1']['bounce']) + len(v['only_in_A1']['hit']):>6} "
              f"{len(v['only_in_A2']):>6} | "
              f"{_f(o['mean_abs'], 8)} {_f(o['exact_frame_rate'], 5)}")
    v = report["views"]["all"]
    print(f"label disagreements (all): A1 B -> A2 H = {v['confusion']['A1_B_as_A2_H']}, "
          f"A1 H -> A2 B = {v['confusion']['A1_H_as_A2_B']}")
    if v["only_in_A1"]["bounce"] or v["only_in_A1"]["hit"]:
        print(f"only in A1 (all): B {v['only_in_A1']['bounce']}  H {v['only_in_A1']['hit']}")
    if v["only_in_A2"]:
        print(f"only in A2 (all): {v['only_in_A2']}")
    a = v["attributes_on_matched"]
    print(f"matched pairs: tag agreement {_f(a['tag_agreement'])}; hit pairs {a['hit_pairs']}: "
          f"player agreement {_f(a['player_agreement'])}, stroke agreement {_f(a['stroke_agreement'])} "
          f"(on {a['stroke_pairs_both_set']} pairs with both strokes set)")
    print(f"frame offset |d| histogram (all): {v['offset']['hist_abs']}  "
          f"(mean signed A2-A1 = {_f(v['offset']['mean_signed_a2_minus_a1'])})")


def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Inter-annotator agreement on event sidecars.")
    p.add_argument("a1", help="First annotator sidecar (reference).")
    p.add_argument("a2", help="Second annotator sidecar.")
    p.add_argument("--tolerance-frames", type=int, default=None,
                   help="Match window; default round(0.15*fps) read from A1 (then A2).")
    p.add_argument("--exclude-tags", default=None,
                   help="Comma-separated tags for the 'untagged' view (default: every tag).")
    p.add_argument("--json", default=None, help="Write the full report to this JSON path.")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    h1, a1 = load_sidecar(args.a1)
    h2, a2 = load_sidecar(args.a2)
    fps = h1.get("fps") or h2.get("fps")
    if not fps and args.tolerance_frames is None:
        raise SystemExit("fps missing from both sidecars; pass --tolerance-frames")
    if h1.get("fps") and h2.get("fps") and abs(float(h1["fps"]) - float(h2["fps"])) > 1e-6:
        print(f"WARNING: fps differs (A1 {h1['fps']} vs A2 {h2['fps']}); using A1's", file=sys.stderr)
    if h1.get("frame_offset", 0) != h2.get("frame_offset", 0):
        print(f"WARNING: frame_offset differs (A1 {h1.get('frame_offset')} vs "
              f"A2 {h2.get('frame_offset')}) — frames may not be comparable", file=sys.stderr)
    excl = (set(t.strip().lower() for t in args.exclude_tags.split(",") if t.strip())
            if args.exclude_tags is not None else set())
    report = {
        "clip": h1.get("video") or Path(args.a1).stem,
        "fps": fps,
        "a1_file": str(args.a1), "a2_file": str(args.a2),
        "a1_annotator": h1.get("annotator"), "a2_annotator": h2.get("annotator"),
        "a1_policy_version": h1.get("policy_version"), "a2_policy_version": h2.get("policy_version"),
        "exclude_tags_for_untagged_view": sorted(excl) if excl else "all tags",
        "views": {
            "all": compare(a1, a2, fps or 0, args.tolerance_frames, exclude_tags=None),
            "untagged": compare(a1, a2, fps or 0, args.tolerance_frames, exclude_tags=excl),
        },
    }
    print_table(report)
    if args.json:
        Path(args.json).write_text(json.dumps(report, indent=1) + "\n")
        print(f"report -> {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
