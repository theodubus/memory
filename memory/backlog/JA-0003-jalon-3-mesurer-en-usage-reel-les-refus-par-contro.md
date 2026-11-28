<!-- socle: couche=backlog zone=publique -->
# JA-0003 — Jalon 3 — Mesurer en usage réel : les refus par contrôle, les demandes par semaine

> statut : ouvert · origine : J-2026-11-10-N · ref : D-0198, D-0233 · après : JA-0006, B-0391 · lu : backlog@f4d5e8a1 · ancien : B-0159

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

Le 27 novembre, Théo y rattache la mesure que chess a faite à la main
(D-0233, revue de cap 10) : le compte des appels d'outil par nature
(§1.1 de `docs/fabrication/chess/cout-et-frictions-2026-11-26.md`) et
ses 56 refus classés, fondés ou à tort (§3), en sont le contenu et le
premier relevé ; ils mesurent avant et après les corrections du
troisième retour. Ses besoins se forment à l'arbitrage de B-0367.

Le 28 novembre, le relevé d'après le rejoint, à côté du premier
(`docs/fabrication/chess/cout-et-frictions-2026-11-28.md`, B-0383) : une
séance ordinaire de chess, 120 appels et 3 refus. Les appels se
comparent à ceux d'avant, les refus non : deux semaines d'un côté, une
séance de l'autre. B-0391, la commande qui refait ce relevé, y entre
(J-2026-11-28-D).

## Fait quand

- [ ] une commande relève les refus par contrôle et les demandes par semaine, et un test le montre
- [ ] un premier relevé du pilote est lu avec Théo
