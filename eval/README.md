# eval/ — scoring harness

Self-contained: `event_eval.py` (the matcher) and `eval_multiclip.py` (manifest-driven
pooled scoring + bootstrap CI) import only each other and the Python standard library.
Python ≥ 3.9, no third-party packages.

```bash
# the paper's single test-split scoring (rally-only view)
python eval/eval_multiclip.py --manifest eval/manifest.json --split test \
    --exclude-tags serve,toss,far,dead,offscreen,replay

# development split, raw detector view (nothing excluded), JSON report
python eval/eval_multiclip.py --manifest eval/manifest.json --split dev --json > dev_raw.json

# one clip, one prediction file, against its sidecar converted to the legacy two-file GT
python eval/event_eval.py --pred preds/tennis_demo3.pred.json \
    --truth-bounces <bounces.json> --truth-shots <shots.json>
```

## Prediction JSON format

One file per clip, referenced by the manifest's `pred` key. Two layouts are accepted
(`event_eval.load_pred_events`); labels are normalised, so `B`/`H`, `BOUNCE`/`HIT`,
`bounce`/`hit`, `S`/`SHOT` all work.

Layout 1 — unified events list (preferred):

```json
{
  "fps": 50.0,
  "events": [
    {"frame": 44,  "label": "HIT"},
    {"frame": 63,  "label": "BOUNCE"}
  ]
}
```

Layout 2 — separate arrays (this is what the CourtSide pipeline's `_stats.json` emits;
`eval/preds/*.pred.json` for the 7 corpus clips use it):

```json
{
  "fps": 60.0,
  "bounces": [{"frame": 72, "x": 1138, "y": 368, "...": "any extra keys are ignored"}],
  "shots":   [{"frame": 5,  "x": 473,  "y": 829, "...": "..."}]
}
```

Rules:

- `frame` is an integer index in the **fixture / annotation window frame of reference**
  (frame 0 = first frame of the clip as described in `data/fixtures/<clip>.meta.json`;
  for every clip here the GT sidecar has `frame_offset: 0` in that same reference).
- Only `frame` and the label are read. Everything else is ignored.
- `fps` is optional in the prediction file: it is taken from the manifest, then the GT
  sidecar, then the prediction file, in that order.
- Emit **every** event your system believes in (serves, tosses, dead bounces included).
  The tag-exclusion mechanism handles off-rally events: a prediction that matches an
  excluded GT event is *ignored* (neither TP nor spurious), so you are never punished
  for detecting a real serve and never rewarded for it either.

## Manifest format

`eval/manifest.json`. Relative paths resolve against the manifest file. Required keys per
clip: `clip`, `pred`, `gt`, `split` (`dev`|`test`). Optional `fps` override; any other
key (e.g. `camera`) is echoed into the JSON report as an annotation. To score your own
system, copy the manifest and change only the `pred` paths.

## Matching semantics (unchanged from the paper)

- One greedy one-to-one matcher across BOTH classes at once, nearest frame first.
- Tolerance `round(0.15 * fps)` frames per clip (±4 at 25 fps, ±8 at 50 fps, ±9 at 60 fps).
- A predicted BOUNCE matched to a GT hit is a confusion (`H>B`): it counts as a bounce FP
  AND a hit FN. Symmetric for `B>H`. Confusion is therefore doubly penalised.
- Unmatched predictions are `spurious`; unmatched GT events are misses.
- Pooled numbers are micro-averages (sums of TP/FP/FN over all clips of the split).
- The 95% CI is a clip-level bootstrap (10 000 iterations, seed 20260901). With 4 clips
  per split it is wide by construction; it is reported, not relied upon.
- Known, inherited as-is for comparability: the documented same-class tie-break in
  `event_eval._tie_break_key` never fires (it compares `BOUNCE`/`HIT` to `bounce`/`shot`);
  exact-distance ties fall through to a stable frame order. Never observed on real GT.

## Expected output on the frozen predictions

`eval/expected/` holds the JSON reports produced by this very copy of the harness on
`eval/preds/` (see MANIFEST.md for the exact commands). Test split, rally-only view:
pooled bounce F1 **0.621** (P 0.800 / R 0.507), hit F1 **0.459** (P 0.528 / R 0.406),
confusion H>B 4 / B>H 4, 26 spurious, 11 ignored — identical to the paper's frozen
`results_multiclip_test.json`.
