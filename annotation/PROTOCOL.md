# Double-annotation protocol (blind second annotator, policy v2)

Goal: measure how reproducible the ground truth is. A second annotator (A2) re-annotates
three clips from scratch, blind, under the **frozen** policy v2 (`../data/POLICY.md`).
The agreement between A2 and the released sidecars (A1) is then computed with the same
matching semantics as the benchmark evaluator (`agreement.py`). Those numbers are the
ceiling any system can be expected to reach on this benchmark.

## 1. What is frozen

- **Policy v2** (`data/POLICY.md`, `policy_version: 2`). It is not discussed, amended or
  re-interpreted during the pass. Ambiguities are resolved *by the annotator alone* and
  written down in the sidecar's `notes` field, so they can be read afterwards.
- **Tolerance**: agreement is scored at `round(0.15 * fps)` frames, exactly like the
  evaluator. The annotator still aims for the exact frame (policy: *first* frame of contact).
- **Tag vocabulary**: `serve, toss, net_cord, let, out, far, dead, offscreen, replay`
  (one tag per event, as the tool writes it). `player` (near/far) is mandatory on hits,
  `stroke` recommended.

## 2. Blindness — what A2 must NOT see

Before and during annotation A2 must not open:

- any `*.events_gt.json` of the clip (A1's annotation), nor `data/fixtures/<clip>*`;
- any system output: `eval/preds/*`, `*_annotated_stats.json`, annotated videos, radar
  overlays, event lists, score tables;
- the paper's per-clip result tables and discussion of specific frames.

A2 works from the **raw source video only** (the same file and the same time window
the fixture was built from, see `data/fixtures/<clip>.meta.json` and `SOURCES.md`).
The policy document and this protocol are the only text allowed. A2 does not discuss
individual events with A1 until the sidecar is delivered.

## 3. The three clips (one per regime)

| Clip | Split | Regime | Why this one |
|---|---|---|---|
| `clay_am_40s` | dev | amateur, fixed indoor camera, full policy | the dev clip whose GT was most edited during tuning (3 retimed frames, category-A holes filled), so it is where annotator drift is most plausible |
| `grass_am_40s` | test | amateur, low angle, **near-only** (`far` tag) | the only regime where the policy itself admits ±3-frame best-effort events; agreement on *which* events get the `far` tag is the open question |
| `clay_pro_40s` | test | professional broadcast, 25 fps, full policy | the lowest frame rate (tolerance ±4 frames) makes frame-exactness hardest; the regime the paper reports the weakest transfer on |

Together they cover the three settings of the corpus (amateur fixed camera, amateur
low angle near-only, pro broadcast), both splits, and the two extreme frame rates
(25 and 60 fps).

## 4. Running the annotation tool

The tool lives in the CourtSide-CV repository: `tools/annotate_events.py` (OpenCV only;
it needs the repo's `tools/events_gt_io.py` and `utils/video_utils.py`). Its own
docstring is the reference; the essentials:

```bash
# from the repo root, with the project's Python environment
python tools/annotate_events.py path/to/<clip>.mp4 \
    --annotator "<A2 name>" \
    -o <deliverable dir>/<clip>.events_gt.A2.json
```

- Annotate the **whole clip** as cut (the 40 s stream-copy cut, or the 22 s cut for
  `grass_pro_40s` if ever added). Do not pass `-s/-d/-e` for these clips: frames must stay
  in the fixture's reference (frame 0 = first frame of the cut), with `frame_offset: 0`.
- Keys: `LEFT/RIGHT` step ±1 frame, `UP/DOWN` ±10, `[`/`]` ±100, `SPACE` play/pause,
  `g` go to frame, `z` + click = 2× zoom (use it on the far ball),
  `b` = BOUNCE at the current frame, `h` = HIT (then `n`/`f` for near/far, then
  `f`/`b`/`v`/`s`/`m` for FH/BH/volley/serve/smash, ENTER to skip the stroke),
  `t` = cycle the tag of the nearest event, `x` = delete nearest, `u` = undo,
  `s` = save, `q` = save + quit, `ESC` = quit without saving.
- Re-running on an existing `-o` sidecar resumes it. Save often (`s`).
- Workflow per contact: play to the contact, step **backwards** until the contact just
  disappears, step forward one frame: that is the frame to mark (first frame of touch;
  on a 2-frame motion blur, the first one).
- Expect roughly 20–30 min per 40 s clip at policy-v2 completeness (every off-rally
  contact tagged, not skipped).

## 5. Deliverable

For each clip, one file: `<clip>.events_gt.A2.json`, same schema as A1
(`video, fps, n_frames, width, height, frame_offset, annotator, created,
policy_version: 2, notes, events[]`). Fill `annotator`; put any policy ambiguity you had
to resolve in `notes`. Deliver all three at once, before any discussion with A1.

## 6. Scoring the agreement

```bash
python annotation/agreement.py data/gt/<clip>.events_gt.json <clip>.events_gt.A2.json \
    --json agreement_<clip>.json
```

`agreement.py` runs the evaluator's matcher with A2 as "predictions" and A1 as
"ground truth" at `round(0.15*fps)` and reports, for the *all* view (every event) and
the *untagged* view (events tagged by either annotator removed post-hoc, i.e. the
rally-only view the paper scores):

- per-class precision / recall / F1 of A2 vs A1 (F1 is symmetric under swapping A1/A2);
- Cohen's kappa on the B/H label of matched pairs, and the two confusion counts;
- events only in A1 / only in A2 (lists of frames);
- frame-offset statistics of matched pairs (mean |d|, exact-frame rate, histogram);
- tag agreement on matched pairs; player and stroke agreement on matched hits.

Self-check performed on release: a sidecar against itself gives F1 1.000 / kappa 1.000
/ 0 only-in-either; a synthetic perturbation of `clay_am_40s` (5 events shifted +2,
1 shifted −4, 1 shifted +15 i.e. beyond ±9, 2 dropped, 1 label flipped, 1 added, 1 untagged)
gives 37/40 matched, 3 only-in-A1, 2 only-in-A2, 1 B→H disagreement, kappa 0.945,
|d| histogram {0: 31, 2: 5, 4: 1} — each perturbation lands where it should.

## 7. Adjudication (after scoring, not before)

Disagreements are reviewed jointly only after the agreement numbers are recorded and
published. Any change to the released GT that results from adjudication is a new GT
version (date + commit), and the test split is then re-scored **once** for each system
version, never iteratively.
