<!-- socle: couche=backlog zone=publique -->
# B-0238 — Lot de l'installeur à la mise à jour : les notes de version d'une installation relancée, l'adoption vide, le balayage de mutation de chess

> statut : ouvert · origine : J-2026-11-15-J · forme : lot · après : B-0237, B-0225, B-0195, B-0172, B-0144, B-0152, B-0183, B-0186, B-0192 · lu : backlog@19378efe

Ce que dit et pose l'installeur à une mise à jour
(`engine/socle/installer.py`) : les notes de version perdues quand il
est relancé avant le commit (B-0225), son silence sur une adoption déjà
vide et le diff de politique réaffiché (B-0195), et, à terme, un seul
balayage de mutation sur chess (B-0172). Ce que chess a relevé le 13
novembre.

Le 16 novembre, selon la règle qui réunit dans un lot les sujets qui touchent les mêmes fichiers ou le même garde-fou, appliquée à tout le backlog ouvert (J-2026-11-16-J) : cinq sujets de l'installeur et de l'adoption : le second langage à la mise à jour (B-0144), les fichiers protégés d'une mise à jour qu'une session ne peut commiter (B-0152), le hook de fin de tour en double (B-0183), l'import d'un carnet (B-0186), la clé d'un constat toléré (B-0192).
