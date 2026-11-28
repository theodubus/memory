<!-- socle: couche=backlog zone=publique -->
# T-0229 — Le prompt de mise à jour de chess repart de la note 2026-11-27-l et porte la note de B-0386 ; MOTEUR_DE_CHESS avance à la fusion de la pull request #118

> statut : fait · origine : J-2026-11-28-B · besoin : B-0386 · lu : backlog@2b83126f · ref : ce commit

Un commit. Chess a reçu, le 28 novembre, toutes les notes jusqu'à
`2026-11-27-l` (`docs/fabrication/chess/mise-a-jour-2026-11-28.md`) ; le
prompt de mise à jour repart de là, et le premier lot qui change ensuite
`engine/` avance la constante du test qui rejoue sa mise à jour (le skill
`delegate-lot`, J-2026-11-28-A).

## Fait quand

- [x] `tests/test_mise_a_jour_rejouee.py` passe avec `MOTEUR_DE_CHESS` à la fusion de la pull request #118
- [x] `docs/fabrication/chess/prompt-mise-a-jour.md` ne porte que les notes d'après `2026-11-27-l`, chacune dans un point de son thème
