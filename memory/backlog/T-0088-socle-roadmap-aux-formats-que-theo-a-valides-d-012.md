<!-- socle: couche=backlog zone=publique -->
# T-0088 — socle roadmap aux formats que Théo a validés (D-0127) : le format détaillé en un tableau par lot, l'état de chaque tâche et la priorité en symboles ; le compact aligné en colonnes

> statut : ouvert · origine : J-2026-11-18-N · besoin : B-0274 · priorité : haute · lu : backlog@65dfc703

Théo, le 18 novembre, devant la sortie de `socle roadmap --format
markdown` (J-2026-11-18-N) : « C'est illisible, le mode détaillé devait
être des tableaux dans ce que tu m'avais proposé et que j'avais validé ».
La proposition validée par D-0127, le 16 novembre, n'existait que dans la
conversation ; B-0274 l'a recopiée sans ses exemples, et T-0057 a suivi
ce texte. La voici, mot pour mot, dans la session de ce jour-là
(session_01Mr1cCeh1TqsE1LCTUWXGkH, 22 h 25 UTC). Les états : ✓ faite,
▶ en cours, ○ prête, ⏳ elle attend une autre entrée ou une réponse à une
demande, ✗ bloquée ; la priorité : ↑ haute, ↓ basse.

Format A, compact, une ligne par lot, pour un coup d'œil (terminal,
récap) :

```text
JA-0005  Fini avant les nouvelles fonctions          9/57 besoins clos
 ▶ L-0013  Structure du backlog, chantier en rond    2/3   en cours
   L-0012  Durée de la vérification                  0/2
   L-0014  Suite de la structure du backlog          0/5
   …  L-0006 à L-0010                                0/35
Hors lot : 30 besoins sans tâche · 1 bloqué (B-0179)
Ensuite : JA-0002 chess équipé (B-0126) · puis B-0101, B-0055
```

Format B, détaillé, les prochains lots tâche par tâche, en Markdown pour
la conversation et GitHub :

```text
### JA-0005 — Fini avant les nouvelles fonctions · 9/57 besoins clos

**1. L-0013 — Structure du backlog, chantier en rond** · en cours · 2/3
| | Tâche | Besoin | |
| ✓ | T-0046 | B-0265 | La structure en quatre formes |
| ○ | T-0048 | B-0270 | La forme exotique dans la liste du guide |

**2. L-0012 — Durée de la vérification** · 0/2
| ○ | T-0044 | B-0257 ↑ | La suite sur plusieurs cœurs |

… lots 3 à 10, une ligne chacun (--all pour tout le détail)
```

Lu par besoin (`--by need`) : chaque besoin, ses tâches et le lot de
chacune. Le livrable, un commit : `engine/socle/roadmap.py` rend ces deux
formats ; un tableau Markdown a sa ligne de séparation, sans laquelle
GitHub ne le dessine pas ; les titres longs se coupent ; ce qui est hors
des lots garde ses sections, en tableaux de même forme ; le contenu, les
options et les déclencheurs de B-0274 ne changent pas.

## Fait quand

- [ ] le format détaillé donne, sous la ligne de chaque lot détaillé (« **n. L-NNNN — titre** · état · closes/total »), un tableau Markdown d'une ligne par tâche : son état et sa priorité en symboles, son identifiant, son besoin et son titre, comme l'exemple validé, et un test de `tests/test_suite_du_projet.py` le lit
- [ ] lu par besoin, chaque besoin a de même le tableau de ses tâches, avec le lot de chacune, et un test le lit
- [ ] le format compact aligne en colonnes chaque jalon, ses lots et leur avancement, le lot en cours marqué ▶, et finit par les lignes « Hors lot » et « Ensuite », comme l'exemple validé, et un test le lit
- [ ] le guide et son anglais montrent les deux formats, une note de version le dit, et le prompt de mise à jour de chess le reprend
