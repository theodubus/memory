<!-- socle: couche=backlog zone=publique -->
# B-0221 — Lot du hook : ce qu'il laisse supprimer, les mots et les écritures du shell qu'il ne voit pas, et la règle qui borne ses trous

> statut : fait · origine : J-2026-11-14-M · forme : lot · après : B-0208, B-0204, B-0205, B-0206, B-0207 · ref : J-2026-11-14-AM · lu : backlog@30fa1fa0

Le troisième lot d'avant les nouvelles fonctions (le chantier actif) : le
hook de l'agent. Ses sujets touchent tous le découpage des commandes du
shell et le jugement des chemins (`engine/socle/hooks.py`,
`engine/socle/commands.py`) et leurs tests ; une seule revue les juge
contre le même modèle de menace. B-0208 d'abord, de priorité haute.

Hors des sujets, le lot écrit aussi la règle 2 de D-0112, que Théo a
validée (J-2026-11-14-M) : ce que le hook juge, et quels trous se
corrigent ; elle borne ce que B-0206 et B-0207 doivent couvrir.
