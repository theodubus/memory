<!-- socle: couche=backlog zone=publique -->
# B-0315 — socle renumber, dans une collision née d'un cherry-pick, renumérote une mention de l'entrée poussée que la branche a retouchée depuis le push

> statut : abandonné · origine : J-2026-11-20-AK · lu : backlog@e7320a30 · ref : D-0168

La revue de L-0007, passe 1 (J-2026-11-20-AK), constat 1 pour le
backlog. Dans une collision née d'un cherry-pick (l'autre entrée poussée
sur la branche, pas sur la branche par défaut), `socle renumber` reporte
le numéro nouveau dans les lignes changées depuis le dernier commit
poussé (`_remplacer_dans_l_ajoute`, `engine/socle/identifiers.py`). Une
ligne qui citait l'entrée poussée et que la branche a retouchée depuis
(le chantier actif se récrit souvent) passe pour ajoutée : elle cite
désormais l'entrée locale. Aucun contrôle ne le voit, les deux
identifiants existant. C'est le défaut de J-2026-11-19-V, resté pour
cette ligne. Pistes : dire dans la sortie chaque ligne changée, ou
départager par l'empreinte qu'une citation porte.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X2 — imaginé par un relecteur, jamais vu, rattrapé ou bénin » : `socle renumber` après un cherry-pick, sur une ligne retouchée depuis le push. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] après un cherry-pick, une ligne retouchée depuis le push qui citait l'entrée poussée la cite encore après `socle renumber`, ou la sortie la nomme pour qu'on la vérifie
