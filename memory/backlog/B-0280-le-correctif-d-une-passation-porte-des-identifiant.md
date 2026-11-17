<!-- socle: couche=backlog zone=publique -->
# B-0280 — Le correctif d'une passation porte des identifiants que la branche reprend ensuite : une décision ou une entrée de journal écrite avant son application prend le même numéro

> statut : ouvert · origine : J-2026-11-17-H · lu : backlog@1df796e8

Mesuré le 17 novembre (J-2026-11-17-G, J-2026-11-17-H) : la passation du
lot L-0012 range en correctif, sous docs/fabrication/passation-l0012
(au commit 5e84cd7, retiré à son intégration), deux commits pas encore relus, qui créent une demande et une entrée de
journal. Sur la branche, ces numéros restent libres : la décision de Théo
consignée ensuite en séance a pris le numéro de la demande du correctif,
et l'entrée de journal du même tour le sien. Appliqué, le correctif
aurait deux demandes sous un même numéro ; il a fallu le régénérer, deux
fois, ses numéros décalés à la main.

Le skill `socle-batch` prescrit ce correctif de passation à tout projet :
le défaut s'y produit dès qu'une entrée s'écrit entre la passation et son
application. Le contrôle des références lit déjà les chemins qu'un
correctif suivi du dépôt crée (`_dans_une_rustine`) ; le calcul des
identifiants ne lit pas ceux qu'il crée.

## Satisfait quand

- [ ] un identifiant qu'un correctif de passation crée n'est pas repris par une entrée écrite avant son application
