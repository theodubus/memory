<!-- socle: couche=backlog zone=publique -->
# T-0067 — Un délai par module dans le lanceur parallèle : au-delà, il nomme le module, tue son groupe de processus et le compte en échec

> statut : ouvert · après : D-0130 · origine : J-2026-11-17-J · besoin : B-0281 · lu : backlog@69f87735

Un délai par module, réglable (`--timeout`), sous celui de l'étape de
`verify` ; au-delà, le lanceur tue le groupe de processus du module, le
compte en échec, et le nomme dans sa sortie et dans son bilan.

## Fait quand

- [ ] un test montre qu'un module qui ne rend pas la main est arrêté au délai, nommé, et que le lanceur rend 1
- [ ] un test montre qu'aucun processus du module ne survit au lanceur
