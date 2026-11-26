<!-- socle: couche=backlog zone=publique -->
# B-0366 — Le prompt de la prochaine mise à jour de chess redit les 37 points que chess a déjà reçus le 26 novembre

> statut : ouvert · origine : J-2026-11-26-AH · ref : D-0215, L-0047 · lu : backlog@edb88ba9

Chess a suivi le 26 novembre la version de
`docs/fabrication/chess/prompt-mise-a-jour.md` récrite par thème (T-0186),
et reçu toutes les notes de version jusqu'à `2026-11-26-c`. Le prompt
garde ses 37 points et dit encore « Ta version date du 13 novembre » : la
mise à jour suivante les redonnerait, avec des étapes de migration déjà
faites. L-0046 l'a récrit (commit `a8b8411f`), mais un test,
`test_le_guide_montre_les_deux_formats_et_une_note_de_version_le_dit`,
exige encore son point 17 : la réécriture attend D-0215.

## Satisfait quand

- [ ] le prompt de la prochaine mise à jour de chess ne dit que ce qui change depuis la version du 26 novembre, chaque note d'après elle dans un point
