<!-- socle: couche=backlog zone=publique -->
# B-0172 — Sur chess, un seul balayage de mutation à terme : celui du socle, quand il sait faire ce que fait celui de chess

> statut : abandonné · origine : J-2026-11-11-Q · après : B-0126 · priorité : basse · lu : backlog@65c7a36c · ref : D-0168

chess a son propre balayage de mutation : un job par fichier, un profil
de compilation dédié, des plafonds mesurés avec leurs raisons
(`docs/fabrication/chess/essai-a-blanc-2026-11-11.md`). Celui du socle
balaie tous les modules dans un seul job, sans ce profil, et dépasserait
probablement sa durée sur le module de recherche. À l'installation, celui
de chess est gardé et celui du socle n'est pas posé (D-0100, B-0126).

Théo demande si on le garde tel quel à terme (J-2026-11-11-Q) : non. Deux
balayages ne se justifient pas, et tant que celui de chess reste hors du
socle, ses plafonds ne sont gardés que par les règles propres de chess,
pas par le cliquet du socle (à vérifier à l'installation). La cible est un
seul balayage, celui du socle : un job par fichier, le profil porté par
l'adaptateur, les plafonds repris de ceux de chess
(`docs/fabrication/chess/mutation-caps.toml`), puis le retrait de celui de
chess. Ce qui manque au socle pour cela se mesure d'abord sur chess.

Le 13 novembre, Théo retient la priorité basse proposée (D-0108@96eeead5).

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X3 — peaufine la machinerie sans gêne constatée » : remplacer le balayage de mutation de chess par celui du socle ; celui de chess marche. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] chess n'a plus qu'un balayage de mutation, celui du socle, qui fait ce que faisait le sien, ses plafonds gardés par le cliquet du socle
