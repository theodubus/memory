<!-- socle: couche=backlog zone=publique -->
# T-0116 — demandes.reponse-seule compte le test changé sur la branche depuis la demande, comme un fichier protégé

> statut : ouvert · origine : J-2026-11-20-V · besoin : B-0312 · lu : backlog@02de763b

Un commit : `_reponse_seule` compte aussi un test, un fichier de cas ou
une clé nommés que la branche a changés depuis le commit qui a posé la
demande ; son témoin sain dans l'auto-test (la réponse poussée après le
test, sans avertissement), le défaut `reponse-poussee-seule` gardé.

## Fait quand

- [ ] la réponse poussée après le test qu'elle autorise, poussé sous sa demande en attente, part sans avertissement, et un témoin sain le montre ; la réponse poussée avant son test avertit toujours
