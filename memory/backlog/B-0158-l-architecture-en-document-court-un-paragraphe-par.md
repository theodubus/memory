<!-- socle: couche=backlog zone=publique -->
# B-0158 — L'architecture en document court : un paragraphe par module, une taille maximale

> statut : ouvert · origine : J-2026-11-10-N · lu : backlog@9bf101f2

`docs/fabrication/architecture.md` pèse 41,7 Ko, avec des cellules de
plusieurs milliers de caractères : la correspondance code ↔ doc y ajoute
une proposition à chaque correctif (constat 6, D-0093@333ad9d0, proposition 4). Un
paragraphe par module, ce qu'il fait et ses invariants ; l'historique des
correctifs reste dans les décisions et le journal ; une taille maximale
pour le fichier. Si la correspondance doit changer de cible, c'est un
garde-fou : une demande.

## Fait quand

- [ ] l'architecture tient en un paragraphe par module, sous un budget que les garde-fous déclarent
