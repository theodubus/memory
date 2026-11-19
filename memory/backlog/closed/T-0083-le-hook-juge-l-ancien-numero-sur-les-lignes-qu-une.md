<!-- socle: couche=backlog zone=publique -->
# T-0083 — Le hook juge l'ancien numéro sur les lignes qu'une écriture ajoute, pas sur tout le fichier : une entrée neuve du journal qui reprend un ancien numéro déjà cité ailleurs dans le fichier est refusée

> statut : fait · origine : J-2026-11-18-L · besoin : B-0265 · lu : backlog@84ad299e · ref : J-2026-11-19-X, D-0139, ADR-0092

Relevé par la revue de L-0014, passe 1 (J-2026-11-18-L), constat 2 pour
le backlog. `references_refusees` (`engine/socle/hooks.py`, vers la ligne
394) saute toute mention déjà présente dans le fichier d'avant : dans un
fichier du journal qui cite déjà B-0224, une entrée neuve « Voir B-0224. »
passe, quand « Voir B-0237. » est refusée. Chez chess, le fichier du
journal du mois de la migration citera presque tous les anciens numéros :
le refus que pose T-0051 n'y tirerait presque jamais, là où l'agent les
reprend. Le livrable, un commit : l'ancien numéro se juge sur les lignes
que l'écriture ajoute, l'exception de la ligne qui nomme aussi
l'identifiant actuel gardée, et le modèle de menace d'ADR-0087 mis à jour.

## Fait quand

- [x] une écriture qui ajoute, dans un fichier qui cite déjà un ancien numéro, une ligne qui le reprend sans l'identifiant actuel est refusée, et un test le montre
- [x] une écriture qui garde telles quelles les lignes d'avant qui citent un ancien numéro passe, et un test le montre
