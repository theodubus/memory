<!-- socle: couche=backlog zone=publique -->
# B-0172 — Sur chess, un seul balayage de mutation à terme : celui du socle, quand il sait faire ce que fait celui de chess

> statut : ouvert · origine : J-2026-11-11-Q · après : B-0126 · priorité : basse · lu : backlog@65c7a36c

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

## Fait quand

- [ ] le balayage du socle tourne sur chess, un job par fichier, dans la durée de sa CI, avec les plafonds repris de ceux de chess
- [ ] une mesure sur chess montre les mêmes mutants survivants que son balayage actuel, et celui-ci est retiré
