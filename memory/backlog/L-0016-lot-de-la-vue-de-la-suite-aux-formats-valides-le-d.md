<!-- socle: couche=backlog zone=publique -->
# L-0016 — Lot de la vue de la suite aux formats validés : le détaillé en tableaux, le compact en colonnes

> statut : en cours · origine : J-2026-11-18-N · après : L-0014, T-0088 · lu : backlog@86148227

Formé le 18 novembre (J-2026-11-18-N) pour T-0088 : la vue de la suite
que L-0014 a livrée ne suit pas les formats que Théo a validés
(D-0127). Fichiers : `engine/socle/roadmap.py`,
`tests/test_suite_du_projet.py`, le guide et son anglais, les notes de
version, le prompt de mise à jour de chess. Avant L-0015 : une fonction
livrée qui contredit ce que l'humain a validé se corrige d'abord.

## Revues

### Passe 1 — 2026-11-18

Commits : 8464fdd..381025a
- Bloquant : la ligne « Ensuite : » du compact collé dans un récap remplit le contrôle des deux lignes du hook de fin de tour
- Bloquant : le compact rangé par jalon perd l'ordre d'exécution quand les lots de deux jalons alternent
- Ouvre : T-0089, T-0090

Recul : c'est la première passe du lot, sans bloquant d'avant à qui
comparer ; ses deux bloquants n'ont pas la même cause entre eux : l'un
vient du format validé croisé avec le contrôle du récap, l'autre d'un
choix de rangement de l'orchestrateur. Les entrées ouvertes (T-0089,
T-0090, T-0091, B-0287) affinent la même fonction ou relèvent un défaut
voisin ; le lot n'en ferme qu'une, T-0088, qui attend Théo. L-0014, qui
avait livré `socle roadmap`, avait ouvert B-0285, de la même famille :
la vue de la suite reste à mesurer contre son usage. La correction
change un garde-fou, d'où une passe 2 sur elle seule, qui éprouve le
modèle de menace d'ADR-0089 et l'ordre d'exécution : continuer.
