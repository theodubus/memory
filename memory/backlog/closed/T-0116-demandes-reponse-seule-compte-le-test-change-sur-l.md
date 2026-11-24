<!-- socle: couche=backlog zone=publique -->
# T-0116 — demandes.reponse-seule compte le test changé sur la branche depuis la demande, comme un fichier protégé

> statut : abandonné · origine : J-2026-11-20-V · besoin : B-0312 · lu : backlog@02de763b · ref : D-0168

Un commit : `_reponse_seule` compte aussi un test, un fichier de cas ou
une clé nommés que la branche a changés depuis le commit qui a posé la
demande ; son témoin sain dans l'auto-test (la réponse poussée après le
test, sans avertissement), le défaut `reponse-poussee-seule` gardé.

T-0116 s'abandonne le 24 novembre 2026 par D-0168 avec son besoin B-0312, sous « D-0165 — une légère gêne que l'agent règle lui-même » du tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`).

## Fait quand

- [ ] la réponse poussée après le test qu'elle autorise, poussé sous sa demande en attente, part sans avertissement, et un témoin sain le montre ; la réponse poussée avant son test avertit toujours
