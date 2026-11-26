<!-- socle: couche=backlog zone=publique -->
# B-0323 — La mise à jour de chess d'un coup, avec son prompt complété, puis les corrections du socle qu'elle montre

> statut : fait · origine : J-2026-11-21-B · ref : D-0198, D-0204, D-0206, T-0195, J-2026-11-26-AA · lu : backlog@ca2aee8f · après : B-0353, B-0161, B-0351, B-0355, B-0356

Théo, le 21 novembre (D-0151, J-2026-11-21-B) : finir de corriger et
stabiliser le socle avant chess, « puis le mettre à jour d'un coup,
éventuellement corriger le socle suite à la mise à jour et ensuite
reprendre le reste du développement qui relève davantage d'ajout de
features ». Chess n'a été mis à jour qu'une fois, le 13 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-13.md`) ; depuis, chaque lot
qui change ce que chess reçoit complète
`docs/fabrication/chess/prompt-mise-a-jour.md` (J-2026-11-13-L). La mise
à jour se fait dans la session de chess, sur son autre compte, quand
JA-0005 est clos ; ce qu'elle relève sur le socle s'ouvre au backlog et
rejoint ce jalon, JA-0006, avant les fonctions nouvelles.

Le 25 novembre, Théo place avant elle B-0161 et B-0351 (D-0198), après
B-0353 (D-0197).

## Satisfait quand

- [x] chess est mis à jour d'un coup sur la version publiée, avec le prompt complété, et le compte rendu de la mise à jour est dans `docs/fabrication/chess` — `docs/fabrication/chess/mise-a-jour-2026-11-26.md` (T-0195)
- [x] chaque gêne du socle que relève ce compte rendu a son entrée au backlog, dans JA-0006, ou la raison qui l'écarte — B-0357 à B-0361 dans JA-0006, les gênes 3 et 6 écartées avec leur raison (J-2026-11-26-AA)
