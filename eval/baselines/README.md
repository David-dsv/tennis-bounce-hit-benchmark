# eval/baselines/ — external reference rows

Frozen predictions of the external systems scored in the paper's section *External
Reference Rows* (and its leave-one-clip-out fine-tuning), one directory per row:

| Row directory | System | Training data seen | Decision rule | Pooled dev (B / H) | Pooled test (B / H) | Test spurious / confusions |
|---|---|---|---|---|---|---|
| `../preds/` (RallyArb) | RallyArb, training-free arbitration (this release) | none; constants fixed on dev | — | 0.852 / 0.646 | 0.621 / 0.459 | 26 / 8 |
| `e2e_spot_rny008/` | E2E-Spot, RegNetY-008 + GRU, published tennis weights (Hong et al., CVPR 2022) | ~9 000 broadcast events (US Open / Wimbledon), none of our clips | softmax threshold 0.5, fixed a priori; bounce classes → B, swing/serve → H | 0.557 / 0.522 | 0.776 / 0.905 | 0 / 0 |
| `tdeed_small/` | T-DEED small, published tennis weights (Xarles et al., CVPRW 2024) | same corpus | threshold 0.3, fixed a priori; same class mapping | 0.494 / 0.507 | 0.752 / 0.859 | 6 / 0 |
| `vlm_gemini-3.8-flash/` | Gemini 3.8 Flash via OpenRouter, zero-shot (API dated October 2026) | — | 50-frame windows at ~12 fps, frame index burned into each image, one fixed prompt, ±3-frame merge | 0.519 / 0.523 | 0.406 / 0.593 | 59 / 9 |
| `vlm_qwen3-vl-235b/` | Qwen3-VL-235B-A22B Instruct via OpenRouter, zero-shot (open weights; API dated October 2026) | — | 32-frame windows at ~12 fps (provider limit: 32 images per request), stride 20, same prompt and burned frame index, no reasoning budget, ±3-frame merge | 0.135 / 0.217 | 0.190 / 0.257 | 256 / 28 |
| `camera_rule/` | selection by camera type | — | broadcast or fixed elevated → `e2e_spot_rny008`; phone / court-level → RallyArb | 0.854 / 0.721 | 0.846 / 0.896 | 4 / 1 |
| `e2e_spot_rny002_loco_imagenet/` | control: the identical leave-one-clip-out protocol started from ImageNet weights (timm `regnety_002`, fresh 3-way head) instead of the tennis weights | the 7 *other* clips' ground truth, per fold; no broadcast pre-training | same settings, one run per fold, threshold 0.5 | 0.000 / 0.000 | 0.000 / 0.000 | 0 / 0 (no prediction on any fold; max class probability 0.18) |
| `rallyarb_plus_e2e_bounces/` | RallyArb with the bounce frames of zero-shot E2E-Spot rny008 admitted into its candidate pool (same firewall, same decoder; `PROTOCOL.md` in the directory) | RallyArb's dev-fixed constants only; the spotter learned nothing from our clips | fusion variant chosen on dev among six (bounce votes only), test scored once | 0.883 / 0.667 | 0.704 / 0.459 | 26 / 9 |
| `e2e_spot_rny002_loco/` | E2E-Spot RegNetY-002, fine-tuned leave-one-clip-out on this release's events | the 7 *other* clips' ground truth, per fold | AdamW 1e-4, 10 epochs × 256 windows, last epoch, threshold 0.5, all fixed before the first fold | 0.753 / 0.684 | 0.846 / 0.941 | 7 / 0 |

All numbers are the paper's rally-only view (`--exclude-tags serve,toss,far,dead,offscreen,replay`,
tolerance `round(0.15·fps)`), reproduced **bit-identically** by this harness on these files; the
reports are in `expected/<row>_<split>_rally_only.json` and `expected/summary.json`.

```bash
# from release/benchmark/
for row in e2e_spot_rny008 tdeed_small vlm_gemini-3.8-flash vlm_qwen3-vl-235b camera_rule e2e_spot_rny002_loco e2e_spot_rny002_loco_imagenet rallyarb_plus_e2e_bounces; do
  for split in dev test; do
    python eval/eval_multiclip.py --manifest eval/baselines/$row/manifest.json --split $split \
        --exclude-tags serve,toss,far,dead,offscreen,replay
  done
done
```

## What every reader should know before comparing rows

- **Single executions.** Every prediction file is the output of one run, scored once; no row was
  re-run to pick a better score. The written protocol, fixed before the test split was scored, is
  `PROTOCOL.md`. The paper's own live re-run of RallyArb on test (0.632 / 0.450 vs the frozen
  0.621 / 0.459) is archived in the main repository and was *not* substituted.
- **Information regimes differ, by design.** RallyArb's constants were fixed on the dev split and
  never saw test. The two supervised spotters and the VLM learned nothing from any of our clips.
  The LOCO row learned from the ground truth of the seven other clips — so its cells on a test
  clip were trained on the labels of the *other* test clips. Its eight models measure
  *learnability* of the viewpoints from a corpus this size, not one deployable detector.
- **The camera rule was formalized after its component rows had been scored on test**, from the
  one bit of metadata a fixed installation knows (camera type); it is the assignment the dev split
  dictates. Price it accordingly.
- **Pooled numbers invert with split composition** (dev: 3 of 4 clips non-broadcast; test: two
  broadcast clips carry 72 of 140 rally events). Read the rows per camera type, as the paper does.
- **Weights, code and model outputs of the upstream systems are not included** (their licences
  apply; see their repositories). Only the event predictions on our eight clips are released here,
  as data under `LICENSE-DATA`. The `.pred.json` files were stripped to the fields the harness
  reads plus a short `_provenance` block; the raw model outputs (VLM transcripts, per-frame
  score tensors) stay in the main repository.

## Prediction files

`<row>/preds/<clip>.pred.json`, layout 1 of `../README.md` (`{"fps", "events": [{"frame", "label"}]}`),
except `camera_rule/preds/*` whose RallyArb clips use layout 2 (`bounces` / `shots`). Frame indices
are in the fixture / annotation window frame of reference, like everything else in this release.
