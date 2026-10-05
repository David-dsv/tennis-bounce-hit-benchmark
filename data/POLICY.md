# GT multi-clips — politique d'annotation (policy_version=2)

Politique figée AVANT annotation. Toute déviation = nouvelle policy_version.

**v2 (2026-09-05)** — après le census des spurious dev (docs/research/
dev-spurious-census.md) : le tag `toss` couvre désormais TOUT rituel
balle-en-main hors échange (release du lancer, apex du lancer, dribble
pré-service et son rebond) ; demo3 rejoint le format sidecar
(`tennis_demo3.events_gt.json`, serve f44 + toss f11 annotés-tagués — les
fixtures legacy bounces/shots restent inchangées pour le test de régression
historique) ; 3 frames GT retimées (felix H1159→1167, clay_am H1506→1521,
H2230→2241) et les trous catégorie A comblés (@890507c + ce commit).
Outil : `tools/annotate_events.py` (sidecar `<video>.events_gt.json`).

## Règles générales

- **Frame exacte** = PREMIÈRE frame où la balle touche (sol pour B, cordage pour H).
  Flou de mouvement sur 2 frames → prendre la première.
- **Tout événement réel est annoté**, y compris hors-échange, avec un tag :
  `serve` (frappe de service), `toss` (apex du lancer, si marqué), `net_cord`,
  `let`, `out` (rebond hors des limites), `far` (voir ci-dessous).
  Le scoring inclut/exclut par tag (`eval_multiclip.py --exclude-tags …`) —
  aucun événement n'est "silencieusement" omis.
- Pour les H : `player` (near/far) obligatoire, `stroke` (FH/BH/volley/smash/serve)
  recommandé.
- Les transitions caméra / replays (compilations broadcast) ne portent aucun
  événement — ne rien annoter pendant les cutaways.

## Tag `dead` — rebonds multiples de fin de point

Sur coup gagnant ou faute, la balle rebondit plusieurs fois sans être jouée.
Tous ces rebonds sont réels et annotés ; le **premier** (celui du coup qui
termine le point) reste in-rally (non tagué), les suivants portent `dead`.
Motif : le décodeur d'alternance interdit les répétitions same-class — il
supprimera structurellement les 2e+ rebonds. `--exclude-tags dead` donne la
vue rally-only (comparable demo3) ; sans exclusion on mesure le détecteur
brut. Auto-taggable : dans toute suite de B consécutifs (sans H entre),
tout B après le premier est `dead`.

## Tag `offscreen` — contact hors champ

Quand le joueur (souvent near, en court-level) sort du cadre, sa frappe est
réelle mais inobservable. L'annoter à la frame où **la trajectoire de la
balle s'inverse** (±3 frames acceptées), tag `offscreen`. Exclu du scoring
strict comme `far` (pred qui matche = ignorée). Concerne surtout
`hard_pro_40s`.

## Tag `replay` — ralentis de compilation

Une compilation broadcast peut rejouer un point (ralenti/replay) : les
contacts y sont visibles et le pipeline les détectera, mais ils dupliquent
un point déjà annoté. Annoter chaque contact du replay (frame de contact,
±3 frames en ralenti) avec le tag `replay` → exclu du scoring
(`--exclude-tags replay`), les preds qui matchent sont ignorées.

## Tag `far` — clips à angle bas (near-only)

Sur un clip filmé au niveau du court, le demi-terrain lointain est illisible
(balle sub-pixel, contacts invisibles). Politique :

- Les événements du demi-terrain **proche** sont annotés normalement.
- Les événements du demi-terrain **lointain** sont annotés *best-effort*
  (précision ±3 frames acceptée) et tagués `far`.
- Scoring : `--exclude-tags far` → ces événements ne comptent ni TP ni FN, et
  une prédiction qui les matche est ignorée (pas spurious). On mesure donc le
  near-court sans punir le pipeline pour le far invisible.

## Politique par clip (data/gt_clips/*.mp4, coupes stream-copy 40 s)

| Clip | fps | Politique | Notes |
|---|---|---|---|
| `clay_pro_40s` | 25 | complète | RG 2025, broadcast ; 2+ points |
| `clay_am_40s` | 60 | complète | terre indoor, caméra fixe (calibrable 4 coins) |
| `clay_am2_40s` | 59.94 | complète | terre outdoor, caméra fixe élevée, rally 32 coups |
| `grass_pro_40s` | 60 | complète | compilation multi-matchs : rien pendant les cutaways |
| `grass_am_40s` | 60 | **near-only** (`far` sur le demi-terrain lointain) | angle bas |
| `hard_pro_40s` | 60 | **near-only** (`far` sur le demi-terrain lointain) | court-level practice |
| felix (hits à ajouter) | 60 | complète (GT bounces existante inchangée) | grazing |
| demo3 (existante) | 50 | inchangée (serve/toss non annotés = legacy) | broadcast |

## Split

- **dev** (tuning autorisé) : demo3, felix, clay_am_40s, hard_pro_40s
- **test** (GELÉ, scoré en dernier) : clay_pro_40s, clay_am2_40s,
  grass_pro_40s, grass_am_40s
