<!-- socle: couche=backlog zone=publique -->
# B-0238 — Lot de l'installeur à la mise à jour : les notes de version d'une installation relancée, l'adoption vide, le balayage de mutation de chess

> statut : ouvert · origine : J-2026-11-15-J · forme : lot · après : B-0237, B-0225, B-0195, B-0172 · lu : backlog@19378efe

Ce que dit et pose l'installeur à une mise à jour
(`engine/socle/installer.py`) : les notes de version perdues quand il
est relancé avant le commit (B-0225), son silence sur une adoption déjà
vide et le diff de politique réaffiché (B-0195), et, à terme, un seul
balayage de mutation sur chess (B-0172). Ce que chess a relevé le 13
novembre.
