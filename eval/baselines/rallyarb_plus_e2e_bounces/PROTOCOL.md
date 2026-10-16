# Fusion experiment — pre-registered protocol (written 2026-10-18, before any test scoring)

**Question** (reviewer's request, 2026-10-18): does a supervised spotter's output, admitted into
RallyArb's candidate pool *under the same firewall and decoder*, beat the best single rows on the
test split (fine-tuned spotter 0.846 / 0.941, camera rule 0.846 / 0.896), or lift the grazing phone
clip (felix) where neither the zero-shot nor the fine-tuned spotter works?

## What is fused, and how

RallyArb only relabels and filters the candidates it is given (`vision/events.py`,
`classify_events`). The fusion adds, to the released candidate pool of each clip (curve-fit
bounces, wrist-speed hits, image-height extrema, sharp turns, near-court knees):

- every frame the external spotter predicts as a **bounce** → one more `bounce_cands` entry
  (votes B), placed at the tracked ball position of that frame (nearest real/spline position
  within ±3 frames; if none, the candidate is dropped and counted);
- every frame it predicts as a **hit** → one more `hit_cands` entry (votes H), same position,
  with no wrist information (`anchor: external`).

Nothing else changes: same fixtures (`release/benchmark/data/fixtures/`), same generators,
same evidence (trajectory slopes read on real detections, contact distance at the ball), same
score-free firewall, same parity dynamic program, same constants. An external candidate survives
only if the arbitration's evidence lets it; a cluster that merges an external hit vote with floor
evidence is still forbidden the hit label, exactly as any native candidate.

## External sources

- `e2e` — E2E-Spot RegNetY-008, published tennis weights, zero-shot, threshold 0.5
  (`docs/research/learned-spotting/preds/e2e_rny008.t0.5.<clip>.pred.json`): learned nothing
  from our clips; cleanest information regime.
- `loco` — E2E-Spot RegNetY-002 fine-tuned leave-one-clip-out on the seven other clips
  (`docs/research/learned-spotting/loco/preds/loco_tennis.t0.5.<clip>.pred.json`): held-out
  per clip, but the test folds trained on the other test clips' labels (declared regime).

Both are frozen single runs already scored in the paper; neither is re-run.

## Configurations and selection (dev only)

Seven configurations on the four development clips: `baseline` (no injection, must reproduce
the released RallyArb replay), then {`e2e`, `loco`} × {bounces only `_B`, hits only `_H`,
both `_BH`}. **Selection rule, fixed now:** the configuration with the highest mean of pooled
bounce F1 and pooled hit F1 on dev (rally-only view, paper evaluator); ties broken by fewer
spurious markers. No other criterion, no per-clip cherry-picking, no constant is touched.

## Test (one execution)

The selected configuration is replayed **once** on the four test clips and scored by the paper
evaluator (`tools/event_eval/eval_multiclip.py`, tolerance round(0.15·fps), tags serve, toss, far,
dead, offscreen, replay excluded, clip-level bootstrap). The script refuses to score a test
configuration twice (`results.test.<config>.json` must not exist). The baseline replay is scored
alongside, for the reference only. Whatever the outcome, it is reported.

## Reading, decided in advance

- Pooled test above 0.846 / 0.941 **and** felix above RallyArb's 0.828 / 0.500 → "method plus
  benchmark": the arbitration adds value on top of the best learned row.
- Pooled test above the fine-tuned spotter but felix unchanged → the firewall prices the
  spotter's candidates correctly where they exist; the grazing angle still has no candidates.
- Pooled test at or below the fine-tuned spotter → the arbitration's evidence gates cost more
  than the spotter's candidates bring; the paper keeps its current reading.

Script: `tools/event_eval/fusion_candidates.py` (dev: all configs; test: `--config <selected>`).
