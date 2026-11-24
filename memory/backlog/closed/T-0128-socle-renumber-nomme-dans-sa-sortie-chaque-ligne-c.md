<!-- socle: couche=backlog zone=publique -->
# T-0128 — socle renumber nomme dans sa sortie chaque ligne changée depuis le dernier push où il reporte le numéro nouveau, pour qu'on la vérifie

> statut : abandonné · origine : J-2026-11-21-Q · besoin : B-0315 · lu : backlog@6c894b15 · ref : D-0168

Un commit : dans une collision née d'un cherry-pick, `socle renumber` (`_remplacer_dans_l_ajoute`, `engine/socle/identifiers.py`) dit, fichier et ligne, chaque ligne changée depuis le dernier commit poussé où il a reporté le numéro nouveau, celle que la branche a retouchée et qui citait l'entrée poussée comprise ; ou il la départage par l'empreinte que porte sa citation, quand elle en porte une ; le guide s'il décrit la sortie ; une note de version. Aucune valeur attendue ne change : les tests de `tests/test_identifiants.py` ne lisent que les premières lignes de la sortie (cherché à la création, D-0141).

T-0128 s'abandonne le 24 novembre 2026 par D-0168 avec son besoin B-0315, sous « X2 — imaginé par un relecteur, jamais vu, rattrapé ou bénin » du tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`).

## Fait quand

- [ ] après un cherry-pick, une ligne retouchée depuis le push qui citait l'entrée poussée la cite encore après `socle renumber`, ou sa sortie la nomme, et un test le montre
