<!-- socle: couche=backlog zone=publique -->
# B-0176 — socle renumber refuse une collision née d'un rebase : l'identifiant pris par la branche passe pour existant avant elle

> statut : ouvert · origine : J-2026-11-11-S · lu : backlog@582bc1c8

Relevé pendant B-0168. Reproduction : sur une branche B, créer une ADR
(`socle new adr`, qui rend ADR-0065) et la commiter ; pendant ce temps, la
branche de base en prend une autre sous le même numéro ; `git rebase
<base>` laisse deux fichiers ADR-0065 ; `python3 .socle/socle renumber
ADR-0065` répond « existait avant la branche : ce n'est pas à elle de le
renuméroter ». Il faut le faire à la main : renommer, corriger chaque
mention, reposer les empreintes. La commande devrait reconnaître, parmi
deux entrées du même identifiant, celle que la branche ajoute, et
renuméroter celle-là.

Le 19 novembre (J-2026-11-19-V), le même défaut sur le journal : après
le cherry-pick d'un commit de sous-agent, deux entrées J-2026-11-19-S
dans le même fichier, l'une déjà poussée ; `socle renumber
J-2026-11-19-S` les renomme toutes deux, avec les mentions de la
première dans le chantier actif. Réparé à la main.

## Satisfait quand

- [ ] une collision d'identifiants née d'un rebase se répare par `socle renumber`, sans renommage ni mention corrigés à la main
