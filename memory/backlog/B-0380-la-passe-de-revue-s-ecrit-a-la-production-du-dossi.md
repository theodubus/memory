<!-- socle: couche=backlog zone=publique -->
# B-0380 — La passe de revue s'écrit à la production du dossier, avant le retour du relecteur : en session cloud, le lot part avant sa revue

> statut : ouvert · origine : J-2026-11-27-U · ref : D-0235 · lu : backlog@4d53be09 · réserve : D-0235, point 10 : rien ne se perd ni ne fusionne avant le retour du relecteur · trié : L-0056

Chez chess (`docs/fabrication/chess/cout-et-frictions-2026-11-26.md`, §6) : en session cloud, le hook de fin de tour
de l'environnement exige de pousser la passe que `socle review` vient
d'écrire ; le lot part avant sa revue, et la note « lot déjà poussé »
s'applique à tort. Confirmé (`docs/fabrication/chess/relecture-cout-et-frictions-2026-11-27.md`) : `ecrire_passe`
(`engine/socle/review.py`) écrit la passe à la production du dossier.

En réserve (D-0235, point 10) : rien ne fusionne avant la revue, et rien
ne se perd ; il revient s'il fausse une fusion ou une revue.

## Satisfait quand

- [ ] la passe d'une revue s'écrit à son retour, avec ses bloquants, et rien n'oblige à pousser le lot avant
