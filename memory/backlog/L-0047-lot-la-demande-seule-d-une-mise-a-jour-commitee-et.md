<!-- socle: couche=backlog zone=publique -->
# L-0047 — Lot — la demande seule d'une mise à jour, commitée et poussée sans contournement (T-0200, T-0201)

> statut : en-cours · origine : J-2026-11-26-AA · lu : backlog@f81a2e08 · après : L-0046, T-0204, T-0200, T-0201

La gêne 1 de la mise à jour de chess du 26 novembre (B-0357, JA-0006) :
la migration du backlog qui ne touche plus l'index (`migration.py`,
T-0200), puis les hooks git avant commit et avant push qui, pendant une
mise à jour pas encore commitée, ne refusent que les constats que le
commit ou le push apporte (`hooks.py`, T-0201), son ADR d'abord. Il
change un garde-fou, sur la preuve qu'ADR-0098 demande : revue
adversariale, dont le relecteur vérifie que rien de ce qui marchait ne
casse, le modèle de menace de B-0357 à l'appui. Note de version
française et anglaise, et point au prompt de la prochaine mise à jour
de chess.

T-0204 le rejoint, d'abord (J-2026-11-26-AH) : le prompt de chess
récrit pour la mise à jour suivante, sur la réponse à D-0215, avant que
T-0200 et T-0201 y ajoutent leur note.
