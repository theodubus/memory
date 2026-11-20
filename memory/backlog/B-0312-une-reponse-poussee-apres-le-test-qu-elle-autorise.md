<!-- socle: couche=backlog zone=publique -->
# B-0312 — Une réponse poussée après le test qu'elle autorise, déjà poussé sous sa demande en attente (D-0147), fait avertir demandes.reponse-seule à tort

> statut : ouvert · origine : J-2026-11-20-V · lu : backlog@0f931c91

Vu en menant T-0075, sur le projet d'essai de l'auto-test, la CI du socle
exigée : la demande qui nomme `test_double` poussée, le test changé,
commité et poussé sous elle (D-0147), puis la réponse `valider` commitée
et poussée seule. Le hook avant push laisse partir, mais avertit
(`demandes.reponse-seule`) : « la branche ne change encore rien de ce
qu'elle nomme (`test_double`). Poussée seule, elle ne couvrira pas ce
changement ». C'est faux : le test est déjà sur la branche, et la CI de
la pull request, qui juge la branche depuis la branche par défaut, lit la
réponse et le test ensemble.

`_reponse_seule` (`engine/socle/checks_memory.py`) mesure les tests et
les clés nommés sur la seule plage pas encore poussée, et les fichiers
protégés sur la branche entière, parce qu'un fichier poussé sous une
demande en attente précède sa réponse sans dommage (D-0071). Depuis
D-0147, un test aussi. La revue de B-0142 gardait la mesure étroite pour
un test changé plus tôt sur la branche sous une validation antérieure :
la mesure qui sépare les deux cas part du commit qui a posé la demande.

## Satisfait quand

- [ ] une réponse poussée après le test qu'elle autorise, poussé sous elle, ne fait plus avertir ; une réponse poussée avant son test, ou après un test changé sous une autre validation, fait toujours avertir
