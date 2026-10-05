# CourtSide RallyArb event benchmark — release

Frame-exact **joint bounce + hit** ground truth for tennis video, with a versioned
annotation policy, the scoring harness, frozen reference predictions, and replay fixtures
so a third party can score a bounce/hit system **without the source videos**.

- **8 clips, 345 events** (165 bounces, 180 hits), clay / grass / hard, 25–60 fps,
  professional broadcast to amateur phone footage.
- **Licenses**: data CC BY 4.0 (`LICENSE-DATA`), code MIT (`LICENSE-CODE`). The source
  videos are **not** included and not licensed here (`SOURCES.md`).
- Described in the paper *RallyArb* (CourtSide-CV repository, `docs/paper/rallyarb.tex`);
  the numbers below are the paper's.

## Layout

```
README.md            this file
MANIFEST.md          file list, sizes, sha256
SOURCES.md           what is known about each clip's origin (+ TODOs before publishing)
LICENSE-DATA         CC BY 4.0 (data)      LICENSE-CODE  MIT (code)
data/
  POLICY.md          annotation policy v2 (frozen; French)
  gt/<clip>.events_gt.json         ground-truth sidecars (8)
  fixtures/<clip>_event.json       replay fixtures (8): per-frame ball centres + poses
  fixtures/<clip>.meta.json        fixture provenance headers (8)
eval/
  event_eval.py      the matcher (greedy 1-1, both classes at once)
  eval_multiclip.py  manifest-driven pooled scoring + clip-level bootstrap CI
  manifest.json      the 8 clips, dev/test split, pointing at data/gt and preds/
  preds/<clip>.pred.json           the paper's frozen system outputs
  expected/*.json    reports of this harness on preds/ (what you should reproduce)
  README.md          prediction / manifest formats, matching semantics
annotation/
  PROTOCOL.md        blind second-annotator protocol (3 clips)
  agreement.py       inter-annotator agreement with the evaluator's matching semantics
```

## The corpus

Counts are those of the sidecars in `data/gt/` (tagged events included). "Fixture frames"
is the length of the analysed window = the replay fixture; `data/fixtures/<clip>.meta.json`
has the per-fixture header.

| Clip | Split | Camera / setting | fps | Fixture frames | GT B | GT H | Events | Tags present | Policy |
|---|---|---|---|---|---|---|---|---|---|
| `tennis_demo3` | dev | broadcast oblique, pro rally | 50 | 650 | 10 | 9 | 19 | serve, toss | v2 |
| `felix` | dev | static phone, grazing angle, amateur | 60 | 1860 | 18 | 22 | 40 | serve, dead | v1 |
| `clay_am_40s` | dev | fixed camera, indoor clay, amateur | 60 | 2591 | 22 | 18 | 40 | serve, dead | v1 |
| `hard_pro_40s` | dev | court-level practice, pro (near-only) | 60 | 2581 | 27 | 34 | 61 | far, toss, dead, offscreen | v2 |
| `clay_pro_40s` | test | broadcast, clay, pro | 25 | 1048 | 27 | 25 | 52 | serve, dead | v1 |
| `clay_am2_40s` | test | elevated fixed camera, outdoor clay, amateur | 59.94 | 2639 | 25 | 27 | 52 | serve, toss | v2 |
| `grass_pro_40s` | test | broadcast compilation, grass, pro | 60 | 1322 | 12 | 14 | 26 | serve, dead | v2 |
| `grass_am_40s` | test | low-angle amateur, grass (near-only) | 60 | 2553 | 24 | 31 | 55 | far, serve, dead, toss | v2 |
| **Total** | | | | | **165** | **180** | **345** | | |

The "Policy" column is the `policy_version` recorded in each sidecar header. Policy v2
(2026-09-05) only *widened the `toss` tag* and added `offscreen`/`replay`; v1 sidecars
remain valid under v2 (`data/POLICY.md`). All sidecars have `frame_offset: 0`: frames are
indices into the fixture window (for `tennis_demo3`, frame 0 is absolute frame 3650 of
its parent file; see the meta file).

### Ground-truth sidecar format

```json
{
  "video": "clay_am_40s.mp4", "fps": 60.0, "n_frames": 2591, "width": 1920, "height": 1080,
  "frame_offset": 0, "annotator": "", "created": "2026-09-03T18:25:36",
  "policy_version": 1, "notes": "",
  "events": [
    {"frame": 14,  "label": "H", "tag": "serve", "player": "far", "stroke": "serve"},
    {"frame": 62,  "label": "B", "tag": null},
    {"frame": 81,  "label": "H", "tag": null, "player": "near", "stroke": "BH"}
  ]
}
```

`frame` = **first** frame where the ball touches the ground (B) or the strings (H).
`tag` ∈ `serve, toss, net_cord, let, out, far, dead, offscreen, replay` or `null`.
`player` (near/far) is mandatory on hits; `stroke` ∈ `FH, BH, volley, smash, serve` or null.
Full semantics of every tag: `data/POLICY.md` (§ "Tag …").

### Replay fixtures (`data/fixtures/<clip>_event.json`)

What the arbitration stage of the reference pipeline consumed, frozen from a live run,
so a method that works downstream of detection/tracking can be evaluated without video:

```
video, fps, width, height
kalman_centers[n_frames]    [x, y] pixel centre of the tracked ball per frame (raw, pre-spline)
kalman_is_real[n_frames]    true where the centre comes from a detection, false where predicted
wasb_centers / wasb_is_real null (no dense-heatmap track in the released fixtures)
players_per_frame[n_frames] [near, far] players, each {box:[x1,y1,x2,y2], kps_xy:[17×[x,y]], kps_conf:[17]}
                            (COCO-17 keypoints, gap-filled, identity-locked)
```

These are derived measurements (coordinates), not pixels. They describe the behaviour of
one detector/tracker stack (fine-tuned YOLO ball detector + Kalman + YOLOv8-pose, see the
paper) — they are a convenience for downstream work, not a definition of the benchmark.
The benchmark itself is the sidecars + the matcher; any front-end may be used by whoever
has the videos.

## Scoring

Python ≥ 3.9, standard library only.

```bash
cd release/benchmark
python eval/eval_multiclip.py --manifest eval/manifest.json --split test \
    --exclude-tags serve,toss,far,dead,offscreen,replay
```

gives, on the frozen predictions in `eval/preds/`:

```
clip           split tol  nB  nH | bounce P     R    F1 |  hit P     R    F1 | H>B B>H spur ign
clay_pro_40s   test    4  25  23 |    0.750 0.360 0.486 |  0.643 0.391 0.486 |   0   0    8   3
clay_am2_40s   test    9  24  25 |    0.750 0.375 0.500 |  0.471 0.320 0.381 |   1   3    8   0
grass_pro_40s  test    9  11  13 |    0.769 0.909 0.833 |  0.500 0.462 0.480 |   3   0    6   1
grass_am_40s   test    9  11   8 |    1.000 0.727 0.842 |  0.500 0.625 0.556 |   0   1    4   7
POOLED (micro)             71  69 |    0.800 0.507 0.621 |  0.528 0.406 0.459 |   4   4   26  11
```

Development split, same view: pooled bounce F1 0.852 / hit F1 0.646, confusion 1/4,
16 spurious. Raw view (no exclusion) on test: 0.576 / 0.413. All four reports are in
`eval/expected/`.

To score **your** system: write one prediction file per clip (format in `eval/README.md`;
only `frame` + label are read), copy `eval/manifest.json`, change the `pred` paths, run
the same command. Report the rally-only view (`--exclude-tags serve,toss,far,dead,offscreen,replay`)
as the headline and the raw view alongside it.

### Matching in one paragraph

One greedy one-to-one matcher over both classes at once, nearest frame first, tolerance
`round(0.15·fps)` frames. A predicted bounce landing on a GT hit is a *confusion*
(bounce FP **and** hit FN); unmatched predictions are *spurious*. Excluded tags are applied
**after** matching: an excluded GT event is neither TP nor FN, and a prediction that
matched it is *ignored* (not spurious). Pooled scores are micro-averages; the CI is a
clip-level bootstrap (10 000 iterations, seed 20260901) and is wide with 4 clips per split.

## The frozen split rule

- **dev** = `tennis_demo3, felix, clay_am_40s, hard_pro_40s` — tuning allowed, score as often
  as you like.
- **test** = `clay_pro_40s, clay_am2_40s, grass_pro_40s, grass_am_40s` — **scored once per
  system version**. The reference system was scored on test exactly once (2026-09-07),
  after development was closed; `eval/preds/` are those outputs, unchanged. Three
  pre-registered reference rows (detectors alone, naive pool, untuned arbitration) were
  run once afterwards under a committed protocol.
- If you iterate on a method, iterate on dev; when you score test, record the system
  version with the number and do not go back. A re-scored test is a new system version
  and should be reported as such.
- The policy and the GT are versioned too: a GT change is a dated version and invalidates
  nothing retroactively, but every test number must state the GT version it was scored on
  (here: sidecars as of 2026-09-07, policy v2).

## Rebuilding a fixture from your own copy of a video

The fixtures are snapshots of one stack. To rebuild them (or build new clips) you need the
CourtSide-CV repository (proprietary at the time of this release; the workflow is documented
in `scripts/rebuild_event_cache_from_dump.py`):

1. Run the pipeline on the original video with the methodo-inputs dump enabled:
   ```bash
   COURTSIDE_DUMP_METHODO_INPUTS=dumps/<clip>_methodo.json \
     python run_pipeline_8s.py <video> -s <start_s> -d <duration_s> --device <cpu|mps>
   ```
   Use the **original** file and the canonical `-s/-d` window (a re-encoded clip shifts the
   track; the repo measured a 4× hit-F1 change on demo3 from re-encoding alone).
2. Freeze the replay fixture from the dump:
   ```bash
   python scripts/rebuild_event_cache_from_dump.py --clip <clip> --dump dumps/<clip>_methodo.json --verify
   ```
   `--verify` replays the arbitration twice on the produced fixture to prove determinism.
   The `meta.json` records the dump's sha256, the git HEAD and coverage statistics.
3. Annotate the ground truth with `tools/annotate_events.py <video> -o <clip>.events_gt.json`
   (usage in `annotation/PROTOCOL.md` §4), and add the clip to a manifest.

A rebuilt fixture is **not** byte-identical to the released one unless the same weights,
code revision and device are used; the released `meta.json` files give the revision
(`git_head`) and the dump hash each one came from.

## Double annotation

`annotation/PROTOCOL.md` specifies a blind second pass on `clay_am_40s` (dev),
`grass_am_40s` (test, near-only) and `clay_pro_40s` (test, 25 fps broadcast), one per regime,
and `annotation/agreement.py` scores the two sidecars with the evaluator's own matcher
(per-class P/R/F1, Cohen's kappa on matched labels, only-in-A1 / only-in-A2, frame offsets,
tag/player/stroke agreement; with and without tagged events). No second annotation exists
yet; the kit is released so that the agreement can be measured and published.

## Citing

```
D. Soeiro-Vuong, "RallyArb: bounce/hit arbitration for amateur tennis video — an 8-clip,
345-event frame-exact benchmark", CourtSide-CV, 2026. Data CC BY 4.0, code MIT.
```

## Contact / integrity

Every file's sha256 is in `MANIFEST.md`. Questions about provenance: see `SOURCES.md`
first — if a fact is not there, it is not known to the release authors.
