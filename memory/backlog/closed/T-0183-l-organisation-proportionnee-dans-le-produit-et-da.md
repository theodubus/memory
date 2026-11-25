<!-- socle: couche=backlog zone=publique -->
# T-0183 — L'organisation proportionnée dans le produit et dans delegate-lot, selon docs/fabrication/organisation-proportionnee.md validée

> statut : fait · origine : J-2026-11-25-Q · besoin : B-0352 · ref : J-2026-11-25-T, D-0194, D-0193 · lu : backlog@1bd3d405

Un commit, dans L-0039 : les règles de
`docs/fabrication/organisation-proportionnee.md`, une fois que Théo l'a
validée, dans les gabarits des skills `socle-batch`, `socle-review`,
`socle-request`, `socle-handoff` et `socle-resume` (en français et en
anglais), la section du socle du gabarit d'`AGENTS.md`, le guide
(`HELP.md`, `HELP.en.md`) et le skill `delegate-lot` ; le ménage de leur
section 5, chaque règle retirée dite au récap avec sa raison ; la note de
version. Les tests qui lisent ces textes, dont
`test_il_dit_la_consommation_le_changement_de_session_et_l_apres_fusion`
(`tests/test_skills.py`, « Un lot par session »), changent sous la
demande qui remet les copies protégées de L-0039.

## Fait quand

- [x] les gabarits des skills, d'`AGENTS.md` et le guide disent les cinq sections de la page validée, et les tests qui les lisent le vérifient
- [x] chaque règle retirée au ménage est dite au récap, avec sa raison
- [x] la note de version le dit, en français et en anglais
