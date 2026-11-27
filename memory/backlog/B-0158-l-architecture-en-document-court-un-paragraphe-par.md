<!-- socle: couche=backlog zone=publique -->
# B-0158 — L'architecture en document court : un paragraphe par module, une taille maximale

> statut : ouvert · origine : J-2026-11-10-N · ref : D-0198 · lu : backlog@9bf101f2 · après : B-0323 · réserve : après JA-0006, dans l'ordre du chantier actif (D-0198) · trié : L-0056

`docs/fabrication/architecture.md` pèse 41,7 Ko, avec des cellules de
plusieurs milliers de caractères : la correspondance code ↔ doc y ajoute
une proposition à chaque correctif (constat 6, D-0093@333ad9d0, proposition 4). Un
paragraphe par module, ce qu'il fait et ses invariants ; l'historique des
correctifs reste dans les décisions et le journal ; une taille maximale
pour le fichier. Si la correspondance doit changer de cible, c'est un
garde-fou : une demande.

Le 25 novembre, Théo le place après la mise à jour de chess (D-0198) ;
l'architecture fait alors 79,8 Ko, et 116 des 183 commits du moteur
depuis le 10 novembre l'ont touchée.

## Satisfait quand

- [ ] l'architecture tient en un paragraphe par module, sous un budget que les garde-fous déclarent
