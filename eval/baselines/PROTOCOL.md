# Protocol — external reference rows (VLM, supervised spotters, camera-rule selection)

**Written:** 2026-10-15. Unlike `preregistration-test-baselines.md`, this document is written
*after* the development-split pilots and *at the time of* the single test-split pass; it records
exactly what was decided where, so that the reader can price it. Nothing in it was changed after
the test numbers were seen.

## Rows

1. **Gemini 3.8 Flash, zero-shot** (`tools/event_eval/vlm_baseline.py`, OpenRouter, model date
   2026-10-15). Frames burned with their absolute index, `step = round(fps/12.5)` (~12 fps), 640 px,
   windows of 50 frames / stride 38, one fixed prompt, temperature 0, `max_tokens` 6000,
   `reasoning.effort = low`, robust JSON reader, duplicate merge ±3 frames. The prompt was never
   edited after a result was read; two *protocol* defects found on dev were fixed before test
   (answer truncation at 1 200 tokens; a brittle JSON reader) and the dev row was re-run once.
   Dev also served to choose the model (six candidates on one clip; smaller models did not read
   the task) and the sampling rate (budget). Cost: 2.02 $ dev, 2.33 $ test.
2. **E2E-Spot** (Hong et al. 2022), published tennis weights `tennis_rny008gsm_gru_rgb`
   (checkpoint 041), zero-shot. Their recipe: 398×224 frames, 25–30 fps (1 frame in 2 for our
   50/60-fps clips, native for the 25-fps clip), centre crop 224. Classes `*_bounce → B`,
   `*_swing / *_serve → H`, softmax threshold 0.5 fixed before any result, NMS 0.15·fps.
   The smaller `rny002` model and a full-frame ablation were also run (dev + test) and are reported
   in `docs/research/learned-spotting/`.
3. **T-DEED** (Xarles et al. 2024), published `Tennis_small` weights, same inputs, threshold 0.3
   fixed a priori (`Tennis_big` also reported).
4. **Camera-type selection**: broadcast or fixed elevated camera → row 2; phone / court-level →
   RallyArb (released run). The rule uses the corpus's camera metadata only, never scores. It is
   the rule the development split dictates (demo3, clay-am → spotter; felix, hard-pro →
   RallyArb). Transparency: it was formalised and computed on 2026-10-15 *after* the component
   rows had been scored on test; the paper labels it accordingly.

## Scoring — identical to the paper

`eval_multiclip.py`, exclusion tags `dead,far,offscreen,replay,serve,toss`, tolerance
`round(0.15*fps)`, pooled micro-average, clip-level bootstrap 95 % CI (10 000 iterations, seed
20260901). Every row was scored **once** on the test split. The spotters' training corpus (US Open,
Wimbledon) does not contain any of our clips (demo3 is Acapulco; the others are amateur or
other broadcasts).

## Commitments

- Predictions, manifests and raw model answers are committed under `docs/research/vlm-baseline/`
  and `docs/research/learned-spotting/`; `tools/event_eval/external_baselines_report.py` formats
  them into `results_external_baselines.json`, `tables/tab_external_body.tex` and
  `external_macros.tex` without re-running anything.
- Thresholds, prompt, sampling and the selection rule are not modified after this date on this
  benchmark version. A leave-one-clip-out fine-tuning of E2E-Spot on our 345 events is a separate,
  later experiment (`docs/research/learned-spotting/loco/`).
