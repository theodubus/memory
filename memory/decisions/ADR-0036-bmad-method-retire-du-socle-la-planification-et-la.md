<!-- socle: couche=decisions zone=publique -->
# ADR-0036 — BMAD Method retiré du socle : la planification et la répartition du travail reviennent au socle

> statut : acceptée · date : 2026-10-30 · source : D-0051@cea58730 · lu : decisions@828266d1

## Contexte

ADR-0032@7a953a66 mariait le socle et BMAD Method : la planification à
BMAD, la preuve et la mémoire au socle, une seule façon de consulter
l'humain. Le pilote l'a éprouvé (J-2026-10-30-M@3b42399d) : les workflows
de planification de BMAD sont des coachs par conception, qui transforment
le besoin et inventent du contexte ; BMAD tient une seconde mémoire à côté
de celle du socle ; sa répartition du travail lance tous les sous-agents
au modèle de la session. Théo a validé le principe du retrait
(D-0050@def47d1d), puis le plan complet (D-0051@cea58730).

## Décision

- **BMAD Method n'est plus intégré au socle.** Ses modules, ses trois
  contrôles et leurs défauts injectés, son installation et la
  personnalisation de ses skills par l'installeur, `socle bmad-import`, la
  lecture de ses décisions `AD-n` et sa ligne dans l'état sont retirés.
- **Ce qui servait à tout outil reste** : la déclaration des fichiers
  tiers, que tous les contrôles ignorent (ADR-0031@ded211d6), et les
  décisions prises en séance, dont `--about` ne garde que le chemin du
  document approuvé.
- **La planification revient au socle** (B-0101@451fce1e), à sa manière :
  des documents courts, des ADR, des demandes, des sujets de backlog, et
  l'approbation consignée en séance ; un skill du socle, au ton formel et
  technique.
- **La répartition du travail entre agents revient au socle**
  (B-0055@f93057d0, rouvert), avec le choix du modèle et de l'effort de
  chaque tâche.

## Conséquences

Une seule mémoire, celle du socle, et un seul ton, celui que le projet
fixe. Le socle ne dépend plus de Node ni d'un format qui change avec les
versions d'un autre outil ; le moteur perd environ 390 lignes, et les
tests qui les jugeaient. Le prix : la planification et la répartition du
travail sont à construire, ce que BMAD fournissait déjà. Un projet peut
toujours installer BMAD à côté, et déclarer ses fichiers comme fichiers
tiers ; le socle ne le lit plus. Pour défaire : rétablir les modules
retirés depuis l'historique, et une décision qui remplace celle-ci.
