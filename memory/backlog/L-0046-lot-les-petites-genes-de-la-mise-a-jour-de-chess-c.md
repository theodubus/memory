<!-- socle: couche=backlog zone=publique -->
# L-0046 — Lot — les petites gênes de la mise à jour de chess : CODEOWNERS, correctif de mémoire, commande prise pour une branche, notes datées (T-0196 à T-0199)

> statut : ouvert · origine : J-2026-11-26-AA · lu : backlog@358e3475 · après : L-0045, T-0196, T-0197, T-0198, T-0199

Les quatre corrections courtes que la mise à jour de chess du
26 novembre a montrées (JA-0006), chacune sa correction claire et son
test : l'installeur (`_codeowners` pour T-0196, les notes de version
pour T-0199), `tests.regression` (T-0197), la lecture de « Pour toi »
par la fin de tour (`links.py`, T-0198). Chacune change ce que reçoit un
projet : sa note de version, française et anglaise, et son point au
prompt de la prochaine mise à jour de chess. Aucune ne pose ni ne change
de garde-fou ; la revue est adversariale si le lot passe 150 lignes de
code et de tests.
