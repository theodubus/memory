<!-- socle: couche=backlog zone=publique -->
# JA-0003 — Jalon 3 — Mesurer en usage réel : les refus par contrôle, les demandes par semaine

> statut : ouvert · origine : J-2026-11-10-N · ref : D-0198 · après : JA-0006 · lu : backlog@f4d5e8a1 · ancien : B-0159

Le troisième jalon (D-0093@333ad9d0, proposition 6), en parallèle du deuxième :
mesurer ce que le socle coûte et rapporte en usage réel, comme le cadrage
le demandait pour les faux positifs. Une commande qui ne fait que lire
relève, depuis la trace des hooks et le registre des demandes, les refus
par contrôle et les demandes par semaine ; l'agent du pilote classe ses
refus, fondés ou à tort ; un relevé mensuel dit quels contrôles gardent
leur place.

Le 25 novembre, Théo le confirme après la mise à jour de chess (D-0198).
À son découpage : les refus ne sont tracés que dans `.git/socle/hooks.log`,
local, perdu avec le conteneur d'une session cloud ; chaque commit devra
d'abord porter les siens.

## Fait quand

- [ ] une commande relève les refus par contrôle et les demandes par semaine, et un test le montre
- [ ] un premier relevé du pilote est lu avec Théo
