<!-- socle: couche=backlog zone=publique -->
# B-0097 — Reprise, la session qui a installé le socle démarre hors de la racine du projet

> statut : fait · origine : J-2026-10-30-D · ref : J-2026-10-30-E · lu : backlog@e00eea09

Pour installer, la session cloud du projet ajoute le dépôt privé du socle
(`add_repo`) et le clone. La session devient alors une session à deux
dépôts ; reprise, elle démarre hors de la racine du projet, et les hooks
de l'agent ne se chargent pas. Mesuré sur le pilote : l'état l'a dit en
tête, l'agent s'est arrêté sans rien pousser.

Le dire là où l'installation se décrit : la session qui installe ne se
reprend pas ; le travail continue dans une session neuve sur le seul dépôt
du projet. À terme, un dépôt de distribution public (B-0083) rendrait
l'ajout inutile.
