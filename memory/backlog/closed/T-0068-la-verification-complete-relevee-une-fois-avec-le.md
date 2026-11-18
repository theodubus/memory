<!-- socle: couche=backlog zone=publique -->
# T-0068 — La vérification complète relevée une fois avec le lanceur parallèle, où l'auto-test du socle tourne en même temps que d'autres modules de tests

> statut : fait · après : D-0130 · origine : J-2026-11-17-J · ref : J-2026-11-18-C · besoin : B-0281 · lu : backlog@5779d895

Après le changement de l'adaptateur que D-0130 demande, `python3
.socle/socle verify` relevé une fois dans une session de travail : sa
durée, et ses tests verts, dont ceux qui mesurent un délai (`test_garde`,
`test_demarrage`) et le délai de jugement du hook. S'il échoue sous la
charge, l'auto-test se lance à part, ou en dernier.

## Fait quand

- [x] `verify` complet passe avec le lanceur, sa durée relevée au journal (272,0 s, tout vert, J-2026-11-18-A)
