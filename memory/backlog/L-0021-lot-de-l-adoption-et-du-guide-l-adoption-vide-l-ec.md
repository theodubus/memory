<!-- socle: couche=backlog zone=publique -->
# L-0021 — Lot de l'adoption et du guide : l'adoption vide, l'écart de politique déjà montré, l'import d'un journal, la clé d'un constat toléré

> statut : en cours · origine : J-2026-11-21-B · après : L-0008, T-0026, T-0076, T-0031, T-0105, T-0121, T-0123, T-0124 · lu : backlog@18f4b4cb

Coupé de L-0008 à son annonce, le 21 novembre (J-2026-11-21-B) : dix
tâches pour un seuil de neuf (ADR-0101), et un lot de dix tâches de
l'installeur ne tient pas dans une fenêtre de cinq heures. Ce qu'il
réunit : la sortie de l'installeur à l'adoption et à la mise à jour
(`engine/socle/installer.py`), une adoption vide (T-0026) et un écart de
politique déjà montré (T-0076), du même besoin B-0195 ; le guide
(`engine/socle/HELP.md` et sa version anglaise) pour l'import d'un
journal (T-0031) ; la clé d'un constat toléré (T-0032), qui
s'abandonne si aucun projet n'en a montré le besoin.

Le 21 novembre, Théo place B-0324 avant la mise à jour de chess (D-0152,
J-2026-11-21-D) : sa tâche T-0121, les notes de version qu'une mise à
jour imprime en entier, rejoint ce lot, celui de l'installeur qui suit
L-0008, en cours, qui ne reçoit rien.

Le 21 novembre, la revue à froid de L-0008 ouvre deux constats de
l'installeur (J-2026-11-21-L) : T-0123, l'adaptateur nommé que remplace
une copie de son langage, à dire ; T-0124, la commande du projet qu'efface
la fusion des réglages. Ils touchent `engine/socle/installer.py` : ils
rejoignent ce lot, le suivant de l'installeur.

Le 21 novembre, T-0032 en sort (D-0153, J-2026-11-21-O) : son besoin
B-0192 passe à JA-0006, jugé à la mise à jour de chess.

Le 21 novembre, à la formation des lots qui manquent à JA-0005 (D-0154,
J-2026-11-21-Q) : T-0105, l'exception d'ADR-0088 dans le guide, de
priorité haute, rejoint ce lot, qui change déjà le guide (T-0031).

## Revues

### Passe 1 — 2026-11-22

Commits : d3cfd6d9..f1ebcda0
