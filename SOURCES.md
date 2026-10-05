# SOURCES — provenance of the eight clips

The videos are **not** part of this release. What follows is everything the release
authors can state factually about each clip, taken from the repository's metadata
(`data/POLICY.md`, the GT sidecar headers, the fixture `meta.json` files, the paper's
corpus table). No URL, event name or rights holder is asserted when it is not recorded
in those files. Lines marked **TODO** must be settled before any timestamps / source
links are published.

All clips are 1920×1080. `n_frames` in a GT sidecar is the frame count of the file the
annotator opened; "fixture frames" is the length of the analysed window (= the replay
fixture).

| Clip | Type | fps | Fixture frames (s) | Cut / window | Provenance as recorded | Status |
|---|---|---|---|---|---|---|
| `tennis_demo3` | broadcast, professional rally | 50 | 650 (13.0 s) | window `-s 73 -d 13` of a longer file `tennis.mp4` (fixture frame 0 = source frame 3650) | `tennis.mp4` is described in repo notes as a *broadcast highlight with 20+ camera cuts* (i.e. a compilation); the 13 s window is one oblique-angle rally. Primary broadcaster / tournament / match not recorded. | **TODO: identify the primary source (match, broadcaster) before publishing the window timestamp.** |
| `felix` | amateur, static phone, grazing angle | 60 | 1860 (31.0 s) | frames 0–1859 of `felix.mp4` (the file is 14959 frames ≈ 249 s; only the first 31 s are annotated / in the fixture) | private amateur recording filmed from court level, near-parallel to a sideline. Filmer / players / location not recorded in the repo. | Private recording; consent for redistribution of the video not on file. Fixtures + GT only. |
| `clay_am_40s` | amateur, fixed camera, indoor clay | 60 | 2591 (43.2 s) | ~40 s stream-copy cut of `clay_am.mp4` (full file ≈ 292 MB) | indoor clay, fixed camera "calibratable with 4 corners" (POLICY.md). Origin of `clay_am.mp4` not recorded. | Private/unknown origin; fixtures + GT only. |
| `hard_pro_40s` | professional practice, court-level camera (near-only policy) | 60 | 2581 (43.0 s) | ~40 s stream-copy cut of `hard_pro.mp4` (≈ 150 MB) | "court-level practice" (POLICY.md); far half-court unreadable, hence `far` tags. Origin not recorded. | Origin unknown; fixtures + GT only. |
| `clay_pro_40s` | professional broadcast, clay | 25 | 1048 (41.9 s) | ~40 s stream-copy cut of `clay_pro.mp4` (≈ 279 MB) | POLICY.md notes "RG 2025, broadcast; 2+ points". Match, players and broadcaster not recorded. | Broadcast excerpt; not redistributable. **TODO: confirm the match / broadcaster before citing the event.** |
| `clay_am2_40s` | amateur, elevated fixed camera, outdoor clay | 59.94 | 2639 (44.0 s) | ~40 s stream-copy cut of `clay_am2.mp4` (≈ 25 MB) | outdoor clay, elevated fixed camera, one 32-stroke rally (POLICY.md). Origin not recorded. | Private/unknown origin; fixtures + GT only. |
| `grass_pro_40s` | professional broadcast **compilation**, grass | 60 | 1322 (22.0 s) | cut at 22 s of `grass_pro.mp4` (≈ 303 MB), ending after the first rally and before a slow-motion replay | "multi-match compilation: nothing annotated during cutaways" (POLICY.md). The underlying matches / broadcaster / compiler not recorded. | **TODO: identify the primary source(s) of the compilation (original match(es) and broadcaster) before publishing timestamps.** |
| `grass_am_40s` | amateur, low angle, grass (near-only policy) | 60 | 2553 (42.6 s) | ~40 s stream-copy cut of `grass_am.mp4` (≈ 950 MB) | low camera angle, far half-court unreadable (`far` tags). Origin not recorded. | Private/unknown origin; fixtures + GT only. |

## Notes

- "Stream-copy cut" means an ffmpeg `-c copy` cut of the longer file: no re-encoding, so
  the frame timing of the cut equals the source's. The repo's cut files are
  `data/gt_clips/<clip>_40s.mp4`; the cut start offsets inside the longer files are
  **not recorded** in the repository metadata and are therefore not stated here.
- The two broadcast *compilation* clips (`tennis_demo3`'s parent `tennis.mp4`, and
  `grass_pro_40s`) are the ones whose primary source must be identified before any
  timestamp into the original broadcast is published. `clay_pro_40s` is a single-match
  broadcast excerpt whose exact match is also unconfirmed.
- The amateur clips (`felix`, `clay_am_40s`, `clay_am2_40s`, `grass_am_40s`) and the
  practice clip (`hard_pro_40s`) have no provenance recorded beyond their description.
  Until the filmer and the filmed persons are identified and consent is on file, they
  travel as derived measurements only (ball centres, body keypoints, event frames).
- What *is* released for every clip is sufficient to score a system without the video:
  the ground-truth sidecar and the replay fixture (`data/fixtures/<clip>_event.json`).
  Re-creating the fixture from one's own copy of a video is described in `README.md`.
