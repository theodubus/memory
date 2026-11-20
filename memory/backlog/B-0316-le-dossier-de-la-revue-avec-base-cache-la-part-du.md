<!-- socle: couche=backlog zone=publique -->
# B-0316 — Le dossier de la revue avec --base cache la part du lot que la branche par défaut a reçue avant la revue, quand la branche la fusionne ensuite

> statut : ouvert · origine : J-2026-11-20-AK · lu : backlog@5b8c08d4

La revue de L-0007, passe 1 (J-2026-11-20-AK), constat 3 pour le
backlog. Un lot poussé en plusieurs fois, dont l'humain fusionne une
partie (L1) dans la branche par défaut avant la revue ; la branche
fusionne ensuite la branche par défaut, puis `socle review --base <le
commit d'avant le lot>`. `sans_la_fusion` (`engine/socle/review.py`)
mesure le lot depuis la fusion refaite sur ce commit, qui contient déjà
L1 : le dossier ne montre plus que la suite du lot, et la note dit
pourtant ne retirer que ce que la fusion a apporté. Avant T-0022, L1
restait visible, avec le bruit de la branche par défaut. Une fusion par
commit de fusion se reconnaît par l'ascendance (un commit du lot,
ancêtre du commit fusionné) ; une fusion par écrasement ou par rebase,
non : la correction n'est pas tranchée.

## Satisfait quand

- [ ] le dossier d'un lot dont la branche par défaut a reçu une partie avant sa revue montre cette partie, ou sa note le dit et donne la commande qui la montre
