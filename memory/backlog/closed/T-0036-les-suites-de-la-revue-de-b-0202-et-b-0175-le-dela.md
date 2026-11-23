<!-- socle: couche=backlog zone=publique -->
# T-0036 — Le partage du délai du démarrage entre l'historique et les outils, décidé par une ADR et montré par un test

> statut : fait · origine : J-2026-11-14-J · besoin : B-0219 · lu : backlog@9966bbbd · ref : J-2026-11-22-L, ADR-0105

Un commit : une ADR dit comment le démarrage (`session_start`, `engine/socle/hooks.py`) partage son délai entre l'historique et les outils, et un test montre ce que chacun reçoit. L'échec de l'historique marqué est T-0078 ; les deux fetch sans délai et la phrase du modèle de menace de B-0175 sont écartés (D-0111).

## Fait quand

- [x] une ADR décide du partage du délai du démarrage, et un test montre que les outils reçoivent le délai qu'elle dit
