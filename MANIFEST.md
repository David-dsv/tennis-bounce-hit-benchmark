# MANIFEST

Benchmark release built 2026-10-05 from the CourtSide-CV repository (branch `feat/accuracy-overhaul`), **updated 2026-10-16/18 with the external baseline rows the pre-registered fusion row and the ImageNet-initialised LOCO control (2026-10-19)** (`eval/baselines/`).
**146 files, 32.3 MB total** (32,268,222 bytes), plus this manifest. Nothing in this directory is a video or an image.

## Contents

| Component | What | Files | Size |
|---|---|---|---|
| `data/gt/` | ground-truth sidecars (8 clips, 345 events) | 8 | 0.03 MB |
| `data/fixtures/` | replay fixtures (ball centres + poses + is_real) and meta headers | 16 | 31.79 MB |
| `data/ (policy)` | annotation policy | 1 | 0.00 MB |
| `eval/preds/` | frozen RallyArb reference predictions (stripped to event fields) | 8 | 0.03 MB |
| `eval/expected/` | harness reports on eval/preds (4 views) | 4 | 0.03 MB |
| `eval/` | harness code + manifest + README (excluding preds/expected/baselines) | 4 | 0.03 MB |
| `eval/baselines/` | external reference rows: 8 manifests + 64 stripped predictions + README + pre-registered PROTOCOL | 75 | 0.19 MB |
| `eval/baselines/expected/` | harness reports on the baseline rows (dev/test rally-only) + summary | 17 | 0.10 MB |
| `annotation/` | double-annotation kit + results (A2 sidecars, agreement reports, 2026-10-19) | 9 | 0.05 MB |
| `./` | top-level docs + licenses | 4 | 0.02 MB |

Not included (size / scope): `tests/fixtures/events/<clip>/<clip>_pose.json` (the shot-detector cache: spline-smoothed ball centres + the SAME poses as `_event.json`, ~31 MB more, derivable from `_event.json`), the raw detection dumps, the paper's figures, the upstream models' weights/code and raw outputs (VLM transcripts, per-frame score tensors). The full `_annotated_stats.json` outputs (per-frame tracks, speeds, movement) were stripped to the event fields the evaluator reads; the sha256 of each original is in the pred file's `_provenance`.

## Reproduction commands (run from this directory)

```bash
python eval/eval_multiclip.py --manifest eval/manifest.json --split test --exclude-tags serve,toss,far,dead,offscreen,replay
#   -> pooled bounce F1 0.621 / hit F1 0.459, H>B 4, B>H 4, spurious 26, ignored 11  (== eval/expected/test_rally_only.json)
python eval/eval_multiclip.py --manifest eval/manifest.json --split dev  --exclude-tags serve,toss,far,dead,offscreen,replay
#   -> pooled bounce F1 0.852 / hit F1 0.646, H>B 1, B>H 4, spurious 16  (== eval/expected/dev_rally_only.json)
python eval/eval_multiclip.py --manifest eval/baselines/e2e_spot_rny002_loco/manifest.json --split test --exclude-tags serve,toss,far,dead,offscreen,replay
#   -> pooled bounce F1 0.846 / hit F1 0.941, spurious 7, confusions 0  (== eval/baselines/expected/e2e_spot_rny002_loco_test_rally_only.json)
python annotation/agreement.py data/gt/clay_am_40s.events_gt.json data/gt/clay_am_40s.events_gt.json
#   -> F1 1.000 / 1.000, kappa 1.000, 0 only-in-either (self-test)
```

## Files (sha256)

| File | Bytes | sha256 |
|---|---|---|
| `LICENSE-CODE` | 1,408 | `df15c5cd9a9e080706eb317ef3d7defc533bbf8d2295441f56234930e6777d22` |
| `LICENSE-DATA` | 2,332 | `0f4d10d6a8c752c1de81d44f4cf05c5d3ee8b6864969ddca930eec13764e2bad` |
| `README.md` | 11,455 | `ec76747c311fa2331b24e46a1e0e4108c1bb5105acb2d47440d8d5b67048336f` |
| `SOURCES.md` | 4,893 | `23f0509f2c771f8ec51ecef73b984957a26f5613398feda6e6ada32471376254` |
| `annotation/PROTOCOL.md` | 7,070 | `ba7af15ed5688cf3f2506933dd0fd8e455ce965e7006736f5083c2464588e6e4` |
| `annotation/agreement.py` | 14,689 | `f8a6fb3b30e356ac3a3052671c718f6aaba505f6ba2ddf3d91c2c9b53f44c953` |
| `annotation/results/agreement_clay_am_40s.json` | 3,002 | `ac805dd0e6f775e723a0ad7ef306827f6c427a7c86dc2d9df99f7b98c9cebba1` |
| `annotation/results/agreement_clay_pro_40s.json` | 2,743 | `4034fa6fa24d45390704bc3028bd5647738737c47c1e3c77a9b52cae4cb5ce91` |
| `annotation/results/agreement_grass_am_40s.json` | 2,972 | `2e4b24b65226f7fd9693462d9aae44d39cfc6695ff542c513f4df0d5c69a49bb` |
| `annotation/results/clay_am_40s.events_gt.A2.json` | 4,106 | `e21059967860526c9dc0d1219e758f2dd0326c3ff824567c0dfdf2a6659a0995` |
| `annotation/results/clay_pro_40s.events_gt.A2.json` | 5,379 | `1cb94578822c668dae39b35bf3911b4fb7aac9ba48e958a305d9a1ed6307c3b2` |
| `annotation/results/grass_am_40s.events_gt.A2.json` | 5,280 | `355b559f6eb912d391d9c24c856cfcdff2a7ba3f36976f02b19551841913d944` |
| `annotation/results/pooled.json` | 418 | `536982f26032766221640258102e1ba82c38bbf9371600253b76cc81fe198630` |
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
| `eval/README.md` | 4,276 | `db991f886ef9399a5b2aa9e8b5a8e02a9259a81e17bfc0ca4006cfc5566dd776` |
| `eval/baselines/PROTOCOL.md` | 3,297 | `718b8045567c1a9511b0321e9b5d563ba2128d76787639796cd49953e83a8465` |
| `eval/baselines/README.md` | 5,617 | `70966462e8b4f5e2e103a9c9b84ce99ace882dbd807909ac906e08913d0a7cf4` |
| `eval/baselines/camera_rule/manifest.json` | 1,460 | `a359d957a86526f694cb25e6a5ec56b136324a31273236a126bcd5ae7d02e201` |
| `eval/baselines/camera_rule/preds/clay_am2_40s.pred.json` | 4,068 | `6aeb70299c7ed8f3197130b4c954617e538d1d4fbb27a95fd4c9c7e362d3aa03` |
| `eval/baselines/camera_rule/preds/clay_am_40s.pred.json` | 3,442 | `0e3775dba8756a1f15fe7de7bacc179881563dd6794bfe00aed277675b8d83b3` |
| `eval/baselines/camera_rule/preds/clay_pro_40s.pred.json` | 6,690 | `9991f661fddf337aa7841d7eed60d9666eaf7af95105757cba10772cf4ce5c1a` |
| `eval/baselines/camera_rule/preds/felix.pred.json` | 2,309 | `d90a97ad73ad6abf079f3b2d3c07e86b2a534f88dc821ecbfbdf558aa7af3395` |
| `eval/baselines/camera_rule/preds/grass_am_40s.pred.json` | 2,992 | `5a123dc8ab8016b3f4f1c004c6d4b35d86317c230cd45cf7bbb10f38d86abc95` |
| `eval/baselines/camera_rule/preds/grass_pro_40s.pred.json` | 3,543 | `f95ea0ba6282bd1fccb1b38dd4ac2a7f54e8e69ef61392c951837bf9f3a6198b` |
| `eval/baselines/camera_rule/preds/hard_pro_40s.pred.json` | 4,943 | `89519c9f817b6f35ec4d5f151fe4beec21c4914381398c87654176b6a27572c3` |
| `eval/baselines/camera_rule/preds/tennis_demo3.pred.json` | 2,804 | `3470061ea26d183f9eed9202a07127cb675e18a2b61049cfc38c8c4ed0c21070` |
| `eval/baselines/e2e_spot_rny002_loco/manifest.json` | 1,594 | `1bd83a919e81f2a4b0d22c4baea343870c5420ddd789c8878c31724183b51ef2` |
| `eval/baselines/e2e_spot_rny002_loco/preds/clay_am2_40s.pred.json` | 4,926 | `980d8f31d1e15f594ddfa05ad560ca9ec280c806bb17a8126a40d6579a207ce9` |
| `eval/baselines/e2e_spot_rny002_loco/preds/clay_am_40s.pred.json` | 3,810 | `38b45caa62992ecf6ed6e8ebea164b3cd1212baac15b509896851969a25d7065` |
| `eval/baselines/e2e_spot_rny002_loco/preds/clay_pro_40s.pred.json` | 6,306 | `48cd7c22d9d7a8c3af6d4d5876b1f5b025f8452dc9e2a1bfcea32e30a4d6d6b4` |
| `eval/baselines/e2e_spot_rny002_loco/preds/felix.pred.json` | 1,352 | `6785359d51b4884216db12f129898a597abdb96d71175c1369c53f7792aaedf6` |
| `eval/baselines/e2e_spot_rny002_loco/preds/grass_am_40s.pred.json` | 3,034 | `27d98e7bdccbe468afbbdc7bc2fb01b48689de941b4afe1404e27ca07ea81ea4` |
| `eval/baselines/e2e_spot_rny002_loco/preds/grass_pro_40s.pred.json` | 3,456 | `73e4a57c4c57e85a91a7c8316a385daaf170bdab126623ffa6c21d06f76293f5` |
| `eval/baselines/e2e_spot_rny002_loco/preds/hard_pro_40s.pred.json` | 4,342 | `534587e5425c7c49472ac3838007215bb3893c8838667e7efa059992f86ac8cc` |
| `eval/baselines/e2e_spot_rny002_loco/preds/tennis_demo3.pred.json` | 2,574 | `5175de225f50d80a83c6bcbba9cb71d81741ad9849a2f2d8c94c84658682b708` |
| `eval/baselines/e2e_spot_rny002_loco_imagenet/manifest.json` | 1,603 | `343f4fe5f58b940cd5fe2f3480b303aa2f45ad3f7af928fe975f21a1bac8cc80` |
| `eval/baselines/e2e_spot_rny002_loco_imagenet/preds/clay_am2_40s.pred.json` | 654 | `020686a936f2b7de92481652b4980b95e7675b52a601c7876a5912fcdffab5a4` |
| `eval/baselines/e2e_spot_rny002_loco_imagenet/preds/clay_am_40s.pred.json` | 624 | `e7622cc1773123c7e76152db8525b00824e18c22e55a2cd4bacfa859b95ed1a4` |
| `eval/baselines/e2e_spot_rny002_loco_imagenet/preds/clay_pro_40s.pred.json` | 635 | `307ae04891abcc77de94c5f326128a0b671c8c56e4bd0b580605b35dda2e47bb` |
| `eval/baselines/e2e_spot_rny002_loco_imagenet/preds/felix.pred.json` | 600 | `09b8d6a375e7fefd12bc73079364e3c11c1066b3e43ff3900601848d7fb710b5` |
| `eval/baselines/e2e_spot_rny002_loco_imagenet/preds/grass_am_40s.pred.json` | 628 | `640de9b8d45ba8c6ddc4d8aa4a09c6abc054a42ba8edef6b692c0692bc3a5f62` |
| `eval/baselines/e2e_spot_rny002_loco_imagenet/preds/grass_pro_40s.pred.json` | 632 | `2e917f64e2f9e0df7d81bffd579e9c34e71f51a1445cef5e0229969b8f1a2fd1` |
| `eval/baselines/e2e_spot_rny002_loco_imagenet/preds/hard_pro_40s.pred.json` | 628 | `d1f9d13d960c29f7b1233f405c16b45e7d316e0bd12027e5ed21c73fa2015a14` |
| `eval/baselines/e2e_spot_rny002_loco_imagenet/preds/tennis_demo3.pred.json` | 628 | `d59b4b2a09cd9686e9099bf0bfd2b9d7e72302491b021d73c0fab0eb382c62a6` |
| `eval/baselines/e2e_spot_rny008/manifest.json` | 1,577 | `6bbf1442016a20876ab1e63eef06faecadd425c11ce42c9a1a0901934c715372` |
| `eval/baselines/e2e_spot_rny008/preds/clay_am2_40s.pred.json` | 4,083 | `73c549b5e3c44d1d6b0397093fb4454bb4cea232a8f58aa196893409d5e24121` |
| `eval/baselines/e2e_spot_rny008/preds/clay_am_40s.pred.json` | 3,457 | `438429066f8b2d544646d8fd412c723b528a19120562274f131c7072039154ab` |
| `eval/baselines/e2e_spot_rny008/preds/clay_pro_40s.pred.json` | 6,705 | `c7e93c32d9731c8bd0d7f99825528990784ff6c14c626be5950f90e857e6a481` |
| `eval/baselines/e2e_spot_rny008/preds/felix.pred.json` | 752 | `0317bfbb812aa253e9988d33bb8546a5093d2e75bfefe4cd5af2b816ab30e8c1` |
| `eval/baselines/e2e_spot_rny008/preds/grass_am_40s.pred.json` | 1,264 | `290fe5155f04f2865c89f0bf516d9484f2e75314cfcd4fb39fb9ae782ea01d3d` |
| `eval/baselines/e2e_spot_rny008/preds/grass_pro_40s.pred.json` | 3,558 | `e3231c5ec155b3fcc16cebab63dc4bf63d3a5e4f88095b930ddcb4357d0f93d5` |
| `eval/baselines/e2e_spot_rny008/preds/hard_pro_40s.pred.json` | 901 | `b7ed4c84f0d3cc66d60249b95d598acfb2e2160d2d9d3c860771881097231cb4` |
| `eval/baselines/e2e_spot_rny008/preds/tennis_demo3.pred.json` | 2,819 | `3623ec68690a848a9bb7191b05bf4d91aa9feb5f43c9317ee9267fa878f26940` |
| `eval/baselines/expected/camera_rule_dev_rally_only.json` | 4,950 | `00fa720274ea76b4ef3f3e210c14259a735a49acce4554744c4a2d166330b0c2` |
| `eval/baselines/expected/camera_rule_test_rally_only.json` | 4,349 | `6942f787142264be871342263ac512697438e8f9988d0dc43b0c622d52f0d747` |
| `eval/baselines/expected/e2e_spot_rny002_loco_dev_rally_only.json` | 4,967 | `016857dd464c9d14f5117b916cada73e33a0bb607920478a39a516f1aa295dd1` |
| `eval/baselines/expected/e2e_spot_rny002_loco_imagenet_dev_rally_only.json` | 4,342 | `0969f3cbf2a39d9470ca13d67da5a9f8daac62b7887329e42ad7e20f095dbc27` |
| `eval/baselines/expected/e2e_spot_rny002_loco_imagenet_test_rally_only.json` | 4,674 | `15ff330a28ec29a1deacd647666b8a736a2b5f5fc03023cad9c48dc6702e2561` |
| `eval/baselines/expected/e2e_spot_rny002_loco_test_rally_only.json` | 4,668 | `ce0876e65ec17f3cdc88965370638b193f9d11fdd38684a2639c1ac357815dc7` |
| `eval/baselines/expected/e2e_spot_rny008_dev_rally_only.json` | 4,309 | `6a7d4142de9040046e112f2aa6324ebea20370121844adb6ef68c24cedc74136` |
| `eval/baselines/expected/e2e_spot_rny008_test_rally_only.json` | 4,092 | `e418e48c18bfa64950252bd70a089eaaa565f76c4a891a0506a0c2ddc2e8f030` |
| `eval/baselines/expected/rallyarb_plus_e2e_bounces_dev_rally_only.json` | 5,471 | `796fa0083cd2c146762164571250e0add10751f51fed65424c4af522be585995` |
| `eval/baselines/expected/rallyarb_plus_e2e_bounces_test_rally_only.json` | 5,572 | `03f190aab18dafbf1f86a254c519f569f72471ce516cb6c6f6ee255c908dc29d` |
| `eval/baselines/expected/summary.json` | 1,480 | `bcdae8c48e6abca3e3be0a9eb1e2cb8a45db7af0b43ac840bb2ec1761e7cb1cc` |
| `eval/baselines/expected/tdeed_small_dev_rally_only.json` | 4,448 | `5711ebecfd6104fe657095b196fd00ff6c772c8a96ce95436bbec3a168b4e054` |
| `eval/baselines/expected/tdeed_small_test_rally_only.json` | 4,350 | `79b1b9102961c8726128d3809052d1c722d8bd0fb512c50a148a80d5421b0a4d` |
| `eval/baselines/expected/vlm_gemini-3.8-flash_dev_rally_only.json` | 6,178 | `abb9747d9d8817a898ea76d1c7cb35276325ac5adad59fbb4d1ba0e8295ca771` |
| `eval/baselines/expected/vlm_gemini-3.8-flash_test_rally_only.json` | 6,855 | `ad9da8f54509673f4a3cceebfc92e1410c3f871586874bb44bc4894e587e9371` |
| `eval/baselines/expected/vlm_qwen3-vl-235b_dev_rally_only.json` | 11,905 | `fed723037802dfa5c6090b117c68aab80f5c7fedbe14cc10aded721012d40713` |
| `eval/baselines/expected/vlm_qwen3-vl-235b_test_rally_only.json` | 13,732 | `491c1496a572171622a461d778ca858a6b10fc7047378a153cceabc63191bc63` |
| `eval/baselines/rallyarb_plus_e2e_bounces/PROTOCOL.md` | 3,849 | `2f55cb7f9b31fbad7669004257e63a8e0c2d6524a9df0d9d99aed64c903475d6` |
| `eval/baselines/rallyarb_plus_e2e_bounces/manifest.json` | 1,458 | `3d73f3065aa243395716c4bf2ab224e61435e86d4cd4332af45909590a5203d3` |
| `eval/baselines/rallyarb_plus_e2e_bounces/preds/clay_am2_40s.pred.json` | 1,554 | `8fd41ee62670d25d814e0254b3e3e11d3eec203046ed3921648192c006891ea5` |
| `eval/baselines/rallyarb_plus_e2e_bounces/preds/clay_am_40s.pred.json` | 2,293 | `71e0c895a164fd99ffb8c975a96677c2e6c0f649034165a0e2d8cd257711150c` |
| `eval/baselines/rallyarb_plus_e2e_bounces/preds/clay_pro_40s.pred.json` | 1,902 | `8668e20c0b7605ab7573809245a20e146c0f6a33f5c31add782188db67b4ff35` |
| `eval/baselines/rallyarb_plus_e2e_bounces/preds/felix.pred.json` | 1,120 | `ea886def7ccfb6ea7cb973f51558922129d16422034c3ccc7c48e306b389400a` |
| `eval/baselines/rallyarb_plus_e2e_bounces/preds/grass_am_40s.pred.json` | 1,364 | `1067e2b8b95bed7767b16a870fc63ba3c1f0a7cf5c8adee93627b4765810908f` |
| `eval/baselines/rallyarb_plus_e2e_bounces/preds/grass_pro_40s.pred.json` | 1,442 | `4b0c2b75bd9ce860f66cffe5661c6ab8a3a3265a7eb8b3c8c3ba90db5056177c` |
| `eval/baselines/rallyarb_plus_e2e_bounces/preds/hard_pro_40s.pred.json` | 2,242 | `004961c446b3de1c7edda501cf2224f53ea5c641ddbfa7144c5ea112839dff76` |
| `eval/baselines/rallyarb_plus_e2e_bounces/preds/tennis_demo3.pred.json` | 1,026 | `d3a0098a91fbfe024a091337875834505047123e4e824e50dbe27754dbe4855b` |
| `eval/baselines/tdeed_small/manifest.json` | 1,573 | `a01abcfcddd479c7c3fe277c9d93034fcf070e499c3d2e4a1361f0c9c31e0467` |
| `eval/baselines/tdeed_small/preds/clay_am2_40s.pred.json` | 4,339 | `6a4b62e06d5be43affbda62d8164c3fa7d89de697bcf3061b2e712805edc0cb3` |
| `eval/baselines/tdeed_small/preds/clay_am_40s.pred.json` | 3,724 | `90969eb220ce14be7936730e059e52be135b6f68f65eb877bef7b8717d4c2a05` |
| `eval/baselines/tdeed_small/preds/clay_pro_40s.pred.json` | 6,846 | `df148cd76b5ff27e8772268d503fd988470699f90627dbb20c10827e3c1f1069` |
| `eval/baselines/tdeed_small/preds/felix.pred.json` | 657 | `ece19da229d737f744b1fb04e5449a8204f3a65cf684564d7cb64fbd99924828` |
| `eval/baselines/tdeed_small/preds/grass_am_40s.pred.json` | 678 | `192fb6a13277f9c933920bfb9715127c82c057ad989c34fcc0fe7ba5d74251fd` |
| `eval/baselines/tdeed_small/preds/grass_pro_40s.pred.json` | 3,941 | `0fcdcc0bea5bbb80f3f70aa23725a7ea769db0ea5ddc638766683f359a0afa72` |
| `eval/baselines/tdeed_small/preds/hard_pro_40s.pred.json` | 678 | `cadf49e52e13f9d51be5f696e9f09739625ac77d189a0c45cb7f0e79dfa0126a` |
| `eval/baselines/tdeed_small/preds/tennis_demo3.pred.json` | 2,965 | `0528099a5bbf16580bd72a36d58c6c35b67ac830a8c4421d3fd72f95443063e0` |
| `eval/baselines/vlm_gemini-3.8-flash/manifest.json` | 1,582 | `b548e48f03b2f3f41bc33fa4a3185167f4a46b7be703d2292821c711d9838e24` |
| `eval/baselines/vlm_gemini-3.8-flash/preds/clay_am2_40s.pred.json` | 2,238 | `83b077bea7aa4306e9981691a6ad3e45d1bb015b1d5b5d916650352d13471873` |
| `eval/baselines/vlm_gemini-3.8-flash/preds/clay_am_40s.pred.json` | 1,672 | `161c11482be94a6f9581a6f2074fe0430e7122f3b189a11c9bc0fbf9820b02b2` |
| `eval/baselines/vlm_gemini-3.8-flash/preds/clay_pro_40s.pred.json` | 2,150 | `40c1abe23d6b42582dc21b783a39599fa09c388ce9b9318cf50798fd5b635719` |
| `eval/baselines/vlm_gemini-3.8-flash/preds/felix.pred.json` | 1,442 | `7a2b41e2899d4b67d2769a9f44b4ff7bf1ce3e1135f8705ffa4b71e0a69218d5` |
| `eval/baselines/vlm_gemini-3.8-flash/preds/grass_am_40s.pred.json` | 1,549 | `aff4f6070752eb356425734378be9a6ff8ffc467e68435e5c358db950cfaeba4` |
| `eval/baselines/vlm_gemini-3.8-flash/preds/grass_pro_40s.pred.json` | 1,572 | `3e35ca49201f475713ff97274a6bd8bc633d7a91580d896713db28272464f7b1` |
| `eval/baselines/vlm_gemini-3.8-flash/preds/hard_pro_40s.pred.json` | 2,263 | `f58596a082d2e40809b4a379c202737bee798f3f3b085fe53b536e1c6dad6c38` |
| `eval/baselines/vlm_gemini-3.8-flash/preds/tennis_demo3.pred.json` | 937 | `650b9c49a36dab25f2af5a78ca13ee9e210a4a6426fc0be4559a3b1590f3ffdc` |
| `eval/baselines/vlm_qwen3-vl-235b/manifest.json` | 1,579 | `cdec4a254ddb93fd1aaa4d25f3c2286d7ab90c4b937fe24fc729ed324f63f20b` |
| `eval/baselines/vlm_qwen3-vl-235b/preds/clay_am2_40s.pred.json` | 3,088 | `551084bab69918c6f928aae1abb27d0bf652843618adc7f649f175fd6d470065` |
| `eval/baselines/vlm_qwen3-vl-235b/preds/clay_am_40s.pred.json` | 3,667 | `75c50924043c29601ae0c8aa4c6be29e9feff5569d4d89b4e79a4ba18f7e624f` |
| `eval/baselines/vlm_qwen3-vl-235b/preds/clay_pro_40s.pred.json` | 6,900 | `b75639fcdc6c4a39759635b9ddb9ea4364344919306335ad74ad9fd1b3137530` |
| `eval/baselines/vlm_qwen3-vl-235b/preds/felix.pred.json` | 1,354 | `40d81943fefefe1229240e8b0c281e6bf88a89641502f8e7dda7d0fb748abdc6` |
| `eval/baselines/vlm_qwen3-vl-235b/preds/grass_am_40s.pred.json` | 1,754 | `29d22fd2339f9bd9048341f6f4b46ce91f837ed1da2dc25378a96c0726af2603` |
| `eval/baselines/vlm_qwen3-vl-235b/preds/grass_pro_40s.pred.json` | 4,110 | `40b5a7ac0b89c131ee9d501df7087d7b6a76208276749289a52f761fe720396e` |
| `eval/baselines/vlm_qwen3-vl-235b/preds/hard_pro_40s.pred.json` | 4,171 | `f8b0292e639eea16f85b89c5c06b91de42509d934866e4339bd1305d697d5e6b` |
| `eval/baselines/vlm_qwen3-vl-235b/preds/tennis_demo3.pred.json` | 2,406 | `fb541bc214b71cda59208b5301eae0de398b17096aa73b7986bf3e4b628173ec` |
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
