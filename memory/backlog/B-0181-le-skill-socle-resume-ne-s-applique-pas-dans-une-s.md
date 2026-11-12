<!-- socle: couche=backlog zone=publique -->
# B-0181 — Le skill socle-resume ne s'applique pas dans une session cloud qui n'a pas l'outil list_events

> statut : ouvert · origine : J-2026-11-12-A · priorité : haute · lu : backlog@9397d6c9

À l'installation sur chess (`docs/fabrication/chess/installation-2026-11-12.md`, point 2) : le skill `socle-resume` lit
l'heure de la remise à zéro par l'outil `list_events`. La session cloud de
chess ne l'a pas ; elle a `send_later`, `update_trigger`, `delete_trigger`,
`list_triggers` et `get_session`. Le skill ne s'y applique donc jamais, et
l'agent ne reprend pas seul après une limite d'usage. Piste : sans cet
outil, armer chaque réveil à la borne que le skill prévoit déjà, maintenant
plus cinq heures et cinq minutes, plus sept jours et cinq minutes.

## Fait quand

- [ ] sans l'outil `list_events`, le skill dit quoi faire, dans ses deux langues : l'agent arme ses réveils à leur borne et reprend seul après une limite
