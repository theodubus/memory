<!-- socle: couche=backlog zone=publique -->
# L-0008 — Lot de l'installeur à la mise à jour : les notes de version d'une installation relancée, le second langage, les fichiers protégés de « Et maintenant », les hooks de fin de tour

> statut : fait · origine : J-2026-11-15-J · ref : J-2026-11-21-L · après : L-0020, T-0025, T-0028, T-0029, T-0030 · lu : backlog@19378efe · ancien : B-0238

Ce que dit et pose l'installeur à une mise à jour
(`engine/socle/installer.py`) : les notes de version perdues quand il
est relancé avant le commit (B-0225), son silence sur une adoption déjà
vide et le diff de politique réaffiché (B-0195), et, à terme, un seul
balayage de mutation sur chess (B-0172). Ce que chess a relevé le 13
novembre.

Le 16 novembre, selon la règle qui réunit dans un lot les sujets qui touchent les mêmes fichiers ou le même garde-fou, appliquée à tout le backlog ouvert (J-2026-11-16-J) : cinq sujets de l'installeur et de l'adoption : le second langage à la mise à jour (B-0144), les fichiers protégés d'une mise à jour qu'une session ne peut commiter (B-0152), le hook de fin de tour en double (B-0183), l'import d'un carnet (B-0186), la clé d'un constat toléré (B-0192).

Le 18 novembre, T-0049 découpe B-0195 et B-0172 (J-2026-11-18-J) : T-0076, l'écart de politique déjà montré, à côté de l'adoption vide (T-0026) ; T-0077, la mesure sur chess et le retrait de son balayage, après celui du socle (T-0027).

Le 21 novembre, à son annonce, il est coupé en trois (J-2026-11-21-B) :
dix tâches pour un seuil de neuf (ADR-0101), et la suggestion 1 de la
revue de cap 2 que Théo retient (D-0151), JA-0005 fini sans attendre
chess. Restent ici les quatre tâches de l'installeur à la mise à jour
(`engine/socle/installer.py`) : T-0025, T-0028, T-0029 et T-0030.
L'adoption vide, l'écart de politique, l'import d'un journal et la clé
d'un constat toléré passent à L-0021 ; le balayage de mutation de chess
(T-0027, T-0077), à L-0022, dans JA-0006.

## Revues

### Passe 1 — 2026-11-21

Commits : da9b7f8d..02e868fb

- Bloquant : aucun
- Ouvre : B-0327, T-0123, B-0328, T-0124
