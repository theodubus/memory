<!-- socle: couche=backlog zone=publique -->
# T-0186 — Le prompt de mise à jour de chess récrit par thème, à jour du produit, avec la migration du backlog au compte rendu demandé

> statut : ouvert · origine : J-2026-11-25-AA · besoin : B-0323 · ref : D-0199, J-2026-11-25-Z, D-0209 · après : B-0161, B-0351 · lu : backlog@5c4e730c

Un commit de texte, le dernier lot avant la mise à jour de chess, selon
la suggestion 1 de la revue de cap 7 que Théo garde (D-0199) :
`docs/fabrication/chess/prompt-mise-a-jour.md` récrit, « Ce qui change »
par thème et à jour du produit, chaque règle vérifiée contre le guide,
les skills et la ligne de commande, les points dépassés retirés ; le
compte rendu demandé à chess dit aussi ce que l'installeur a fait de la
migration du backlog.

## Fait quand

- [ ] le prompt ne dit aucune règle que le produit a retirée, ni une commande qui n'existe plus, ce que relève une relecture contre `engine/socle/HELP.md` et `socle --help`
- [ ] le compte rendu demandé nomme la migration du backlog
- [ ] chaque note de version de `engine/socle/CHANGES.md` postérieure à la mise à jour du 13 novembre a son point dans le prompt, la couche des consignes (2026-11-25-e) comprise
- [ ] chaque point reste vrai dans une session cloud de chess : aucun ne promet ce que le proxy y refuse, comme la suppression d'une branche
