<!-- socle: couche=backlog zone=publique -->
# L-0008 — Lot de l'installeur à la mise à jour : les notes de version d'une installation relancée, l'adoption vide, le balayage de mutation de chess

> statut : ouvert · origine : J-2026-11-15-J · après : L-0007, T-0025, T-0026, T-0076, T-0027, T-0077, T-0028, T-0029, T-0030, T-0031, T-0032 · lu : backlog@19378efe · ancien : B-0238

Ce que dit et pose l'installeur à une mise à jour
(`engine/socle/installer.py`) : les notes de version perdues quand il
est relancé avant le commit (B-0225), son silence sur une adoption déjà
vide et le diff de politique réaffiché (B-0195), et, à terme, un seul
balayage de mutation sur chess (B-0172). Ce que chess a relevé le 13
novembre.

Le 16 novembre, selon la règle qui réunit dans un lot les sujets qui touchent les mêmes fichiers ou le même garde-fou, appliquée à tout le backlog ouvert (J-2026-11-16-J) : cinq sujets de l'installeur et de l'adoption : le second langage à la mise à jour (B-0144), les fichiers protégés d'une mise à jour qu'une session ne peut commiter (B-0152), le hook de fin de tour en double (B-0183), l'import d'un carnet (B-0186), la clé d'un constat toléré (B-0192).

Le 18 novembre, T-0049 découpe B-0195 et B-0172 (J-2026-11-18-J) : T-0076, l'écart de politique déjà montré, à côté de l'adoption vide (T-0026) ; T-0077, la mesure sur chess et le retrait de son balayage, après celui du socle (T-0027).
