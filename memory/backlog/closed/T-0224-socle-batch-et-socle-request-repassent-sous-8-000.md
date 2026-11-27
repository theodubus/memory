<!-- socle: couche=backlog zone=publique -->
# T-0224 — socle-batch et socle-request repassent sous 8 000 octets, sans perdre de règle

> statut : fait · origine : J-2026-11-27-AP · besoin : B-0384 · lu : backlog@6bab526e · après : T-0221 · ref : ce commit

Les gabarits `engine/socle/templates/skills/socle-batch/SKILL.md`, avec
ce qu'y ajoute T-0221, et `socle-request` se resserrent sous 8 000
octets : des phrases plus courtes, aucune règle perdue ; leurs copies
protégées de `.claude/skills/` remises par l'installeur en mode amont.

## Fait quand

- [x] `tests/test_mise_a_jour_rejouee.py` passe
- [x] les tests qui lisent le texte de ces skills passent
