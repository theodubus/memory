<!-- socle: couche=backlog zone=publique -->
# L-0016 — Lot de la vue de la suite aux formats validés : le détaillé en tableaux, le compact en colonnes

> statut : en cours · origine : J-2026-11-18-N · après : L-0014, T-0088, T-0091 · lu : backlog@86148227

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

### Passe 2 — 2026-11-18

Commits : 381025a..c034332
- Bloquant : le compact collé en texte, que le skill socle-batch fait coller sans dire où, remplit encore le contrôle des deux lignes du récap · même cause
- Ouvre : T-0100

Recul : le bloquant de cette passe a, selon le relecteur, la même cause
que le premier de la passe 1 : la ligne « Ensuite : » du compact validé,
croisée avec le contrôle du récap. La correction de la passe 1 a retiré
les blocs de code de la lecture en supposant que le produit fait coller
le compact dans un bloc ; elle ne l'a pas vérifié dans le skill qui le
prescrit, et ADR-0089 l'affirmait à tort. Cette fois, chaque texte qui
fait coller le compact, les deux gabarits de `socle-batch` et
`delegate-lot`, dit « dans un bloc de code », un test les lit, et le
contexte de la décision dit le skill tel qu'il est : il ne reste pas de
chemin prescrit qui colle le compact en texte. C'est la première passe
où le relecteur voit une cause revenir ; la règle d'arrêt en veut deux
de suite. Le lot ferme T-0088, le rendu, et T-0091, le texte du skill ;
il ouvre T-0100, l'ordre des lots lu par besoin, de même nature que
T-0089 et T-0090 de la passe 1 : des affinements de la même fonction.
L-0014, qui a livré `socle roadmap` dans les mêmes fichiers, avait ouvert
B-0285, de la même famille : la vue de la suite reste à mesurer contre
son usage. La correction tient en quelques lignes de texte, sans
conception nouvelle : le skill de la revue ne demande pas de passe de
plus, et il ne reste au lot que la réponse de Théo sur les dix tests.
Décision : continuer
