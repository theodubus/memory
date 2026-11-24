<!-- socle: couche=backlog zone=publique -->
# T-0171 — L'auto-test intermittent établi à la dernière publication, sa cause confirmée, corrigé, et sa durée mesurée avant et après

> statut : fait · origine : J-2026-11-24-A · besoin : B-0341 · lu : backlog@4a658caa · ref : J-2026-11-24-R

Les cinq pas de la demande de chess (J-2026-11-24-A), dans l'ordre : les
cas qui écrivent dans l'origine partagée pendant que d'autres la clonent,
nommés ; la reproduction à la dernière publication, l'attendu écrit
avant, l'auto-test en boucle (30 fois au moins) ou un essai ciblé, les
échecs comptés ; le correctif (clone sans liens durs, origine par cas qui
pousse, ou verrou) et le clone dans le `try`, la durée de l'auto-test
mesurée avant et après (le parallélisme l'a fait passer de 76 à moins de
40 secondes) ; un test qui échoue sans le correctif si la course se rend
déterministe, sinon pourquoi ; une note de version. Le compte rendu à
Théo, court, pour la session chess.

## Fait quand

- [x] l'existence du défaut à la dernière publication est établie, avec les comptes de la boucle, et sa cause confirmée ou non
- [x] l'auto-test corrigé ne fait plus échouer un clone de l'origine pendant un push, un clone qui échoue n'échoue que son cas, et un test le montre (ou la raison de son absence est écrite)
- [x] la durée de l'auto-test avant et après est mesurée, et la note de version écrite
