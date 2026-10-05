# MANIFEST

Benchmark release built 2026-10-05 from the CourtSide-CV repository (branch `feat/accuracy-overhaul`).
**47 files, 32.0 MB total** (31,953,891 bytes). Nothing in this directory is a video or an image.

## Contents

| Component | What | Files | Size |
|---|---|---|---|
| `data/gt/` | ground-truth sidecars (8 clips, 345 events) | 8 | 0.03 MB |
| `data/fixtures/` | replay fixtures (ball centres + poses + is_real) and meta headers | 16 | 31.79 MB |
| `eval/preds/` | frozen reference predictions (stripped to event fields) | 8 | 0.03 MB |
| `eval/expected/` | harness reports on eval/preds (4 views) | 4 | 0.03 MB |
| `eval/` | harness code + manifest + README (excluding preds/expected) | 4 | 0.03 MB |
| `annotation/` | double-annotation kit | 2 | 0.02 MB |
| `./` | top-level docs + licenses | 4 | 0.02 MB |

Not included (size / scope): `tests/fixtures/events/<clip>/<clip>_pose.json` (the shot-detector cache: spline-smoothed ball centres + the SAME poses as `_event.json`, ~31 MB more, derivable from `_event.json`), the raw detection dumps, the paper's figures. The full `_annotated_stats.json` outputs (per-frame tracks, speeds, movement) were stripped to the event fields the evaluator reads; the sha256 of each original is in the pred file's `_provenance`.

## Reproduction commands (run from this directory)

```bash
python eval/eval_multiclip.py --manifest eval/manifest.json --split test --exclude-tags serve,toss,far,dead,offscreen,replay
#   -> pooled bounce F1 0.621 / hit F1 0.459, H>B 4, B>H 4, spurious 26, ignored 11  (== eval/expected/test_rally_only.json)
python eval/eval_multiclip.py --manifest eval/manifest.json --split dev  --exclude-tags serve,toss,far,dead,offscreen,replay
#   -> pooled bounce F1 0.852 / hit F1 0.646, H>B 1, B>H 4, spurious 16  (== eval/expected/dev_rally_only.json)
python annotation/agreement.py data/gt/clay_am_40s.events_gt.json data/gt/clay_am_40s.events_gt.json
#   -> F1 1.000 / 1.000, kappa 1.000, 0 only-in-either (self-test)
```

## Files (sha256)

| File | Bytes | sha256 |
|---|---|---|
| `LICENSE-CODE` | 1,408 | `df15c5cd9a9e080706eb317ef3d7defc533bbf8d2295441f56234930e6777d22` |
| `LICENSE-DATA` | 2,332 | `0f4d10d6a8c752c1de81d44f4cf05c5d3ee8b6864969ddca930eec13764e2bad` |
| `README.md` | 10,752 | `de417b67c408d48e6369049351716bebfbd511b963394e44c167e22a08da5bb5` |
| `SOURCES.md` | 4,893 | `23f0509f2c771f8ec51ecef73b984957a26f5613398feda6e6ada32471376254` |
| `annotation/PROTOCOL.md` | 6,254 | `8c1ad867cd7952349f3a97e97d904393063cb4730a4d66ad580e84915b91c8fb` |
| `annotation/agreement.py` | 14,689 | `f8a6fb3b30e356ac3a3052671c718f6aaba505f6ba2ddf3d91c2c9b53f44c953` |
| `data/POLICY.md` | 4,559 | `282d43e6605abba9186875acc1a582bcca2a6667403ddfdef7f43a116751c3ef` |
| `data/fixtures/clay_am2_40s.meta.json` | 777 | `fdf81c6133bd3e99a07b09a66064994d8a49d57e8131b82401bd30f4583b6ee9` |
| `data/fixtures/clay_am2_40s_event.json` | 5,949,464 | `09f88d87020ff9b95f9425878e0547ee3b5017b9dc0359fce59fb7e223cd2b14` |
| `data/fixtures/clay_am_40s.meta.json` | 777 | `e30bc8a9198f7c7bd7c350eb4ee83eaee4583381be918117ed3529560037524f` |
| `data/fixtures/clay_am_40s_event.json` | 5,634,861 | `136e225b7eba127b702273080912f36824653b5b6f6ea98cb1bfdeb96c6884e3` |
| `data/fixtures/clay_pro_40s.meta.json` | 779 | `a8aa3cffe48787807af4b8d19b6584a5bc6064108532e11bf24616433a2c5a75` |
| `data/fixtures/clay_pro_40s_event.json` | 1,972,223 | `5d3f6210caff0f9ba1130920e06836b7cfab3fd24b09282d9bec70f0d91915e0` |
| `data/fixtures/felix.meta.json` | 758 | `db54f124ed5e501180d403f8bcfc61b1f0663f0d83ca50e24044be5d285afe7e` |
| `data/fixtures/felix_event.json` | 3,678,187 | `9c36918d53c599c22273ce0152e5c9a3ba67b29d3a22c5e1c03e599ba0144384` |
| `data/fixtures/grass_am_40s.meta.json` | 779 | `6ae48e21a7480ceaed9c9f3f8d7a5f914939262e0124dc97b742dd2c94571dd4` |
| `data/fixtures/grass_am_40s_event.json` | 5,382,915 | `f481d086bb7c0907b6e4a9ff1ef8bb1693cccfa389e777013746071114b2948b` |
| `data/fixtures/grass_pro_40s.meta.json` | 783 | `cd4936f03639d879871aed2a0044441b868dd57fe62a4b2972d1244b5ab1c941` |
| `data/fixtures/grass_pro_40s_event.json` | 2,458,776 | `e224a33f816f4484756d561fbca01b4dc38c87ba94f02684da9f232ddecc1968` |
| `data/fixtures/hard_pro_40s.meta.json` | 780 | `bd2f3d0129576af9bd8be19351dc1ef228283d5959f8a0c9db4360003128c17a` |
| `data/fixtures/hard_pro_40s_event.json` | 5,222,897 | `eea7ab2fe354422aec17dee150000d0fc56d047c66e3b2f940651edc1835fca6` |
| `data/fixtures/tennis_demo3.meta.json` | 523 | `5f7a8695cb68db413b8889518c025059156c6cb3f7e413ba9062c9e151e8bc3e` |
| `data/fixtures/tennis_demo3_event.json` | 1,480,644 | `0e7bc21b41a8cac728efd472c9567b44b175c19efb4409b203042c790e47dd1b` |
| `data/gt/clay_am2_40s.events_gt.json` | 5,210 | `9efb118a1ee351ea83b5db00938bf4cd2fbe4fb13bd7843cc55cf11226a1f27d` |
| `data/gt/clay_am_40s.events_gt.json` | 3,315 | `2f5edd814048c008f55a4387a95592b6c65a37ad188dd30098c09f2d36d1b34d` |
| `data/gt/clay_pro_40s.events_gt.json` | 5,080 | `80413fb8d5ddb862ab242ece839fdbf07d7ecd5dd020ed24dc2234d3dee5cf37` |
| `data/gt/felix.events_gt.json` | 3,452 | `366730b77a6d8dbdcc4cb8ffdc75ccc1d536418f397e318a1eaf158b460d7c53` |
| `data/gt/grass_am_40s.events_gt.json` | 5,663 | `a1b7f6621a1cb894e737cb97606e6ef482b295da5c4e1316f89177c34850e096` |
| `data/gt/grass_pro_40s.events_gt.json` | 2,742 | `64f643db296dc540f19cbbd4c22a2b20e2b229c21ca09a338213deac26da468f` |
| `data/gt/hard_pro_40s.events_gt.json` | 5,221 | `b154d2d6d9687b81c4f0aeb84054cd9a5b4805d05082a5c21e5b3f9ce960b5ea` |
| `data/gt/tennis_demo3.events_gt.json` | 1,909 | `5dc9f347dd80dc4c8333e3077748ead1f9ad01a58da843256cc41b6f41c338c1` |
| `eval/README.md` | 4,098 | `e257af340a067077b5028c3d592082e9f8c3a7deb392e1c5e77067e4e1302b01` |
| `eval/eval_multiclip.py` | 18,938 | `c98811eed4c78f729c57a4ee49fcdc0f25a0d48fe5157f01fd57e7b3058c51fd` |
| `eval/event_eval.py` | 9,605 | `94246c63a75ad04b4e275a188fe90d5d7ec03106bb51064667110948542603d8` |
| `eval/expected/dev_rally_only.json` | 7,227 | `9a418b0e5e90b2778c1cb83141818aadd8cc9350e86f49f6034f8b3472e1f764` |
| `eval/expected/dev_raw.json` | 6,013 | `877d9d1a06c5462bb47b844cef7f78feab756af4da6fad0191012964bdacc66d` |
| `eval/expected/test_rally_only.json` | 7,511 | `a78d5f7c983f0faeaf2bb5b7c42885aecf2fa7a26f5da4f62257bebc2d183625` |
| `eval/expected/test_raw.json` | 7,365 | `7e1abd9f64e0f3b8d841683afb8ba3aabe4fc7cee657405f6508fdcd8905b198` |
| `eval/manifest.json` | 1,757 | `9aa83676f928898c023d3a60fac4cf38ff2ad5f3e1980c7158ab31340f2670b4` |
| `eval/preds/clay_am2_40s.pred.json` | 3,696 | `3094b9b1ed78c1828227b5ba826dcc7b26fd9cbaa33ffb48a1521164d37ee8b5` |
| `eval/preds/clay_am_40s.pred.json` | 5,327 | `c76dd8e2dea63be0fe933006348b932d5decfc8fa42c1ffaf46e787499cf7ab4` |
| `eval/preds/clay_pro_40s.pred.json` | 3,569 | `8e0031a6d3a7bde564bcfa76b0369cd0714a086244d2f9f30fd59441b5ca7095` |
| `eval/preds/felix.pred.json` | 2,548 | `ad9cf22f1c1d73a76e75fffdec4895ef61c3197e4866ad45f0b1505d7e8f0e55` |
| `eval/preds/grass_am_40s.pred.json` | 3,222 | `e029fea1fcbef621a55a94ff1f0d8664642cca4449ad8de1cdbe30a7d0ff338f` |
| `eval/preds/grass_pro_40s.pred.json` | 3,253 | `1fcee1a64b811cb65fb7cf4245005ef3b1c50c742532dbabe522e3e83cce70ff` |
| `eval/preds/hard_pro_40s.pred.json` | 5,173 | `eeeb1a619e75ec2eef2b7a773bdc2a5d38c9f789d24b827a3e8dc962ed5be918` |
| `eval/preds/tennis_demo3.pred.json` | 1,187 | `2db128a2fa01e4465126adb180a307856babbc6c08e8f06d41447704610f6dde` |
