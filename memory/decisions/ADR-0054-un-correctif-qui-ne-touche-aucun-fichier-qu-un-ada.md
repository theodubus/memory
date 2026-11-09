<!-- socle: couche=decisions zone=publique -->
# ADR-0054 — Un correctif qui ne touche aucun fichier qu'un adaptateur juge, refusé en le disant, admis par une demande

> statut : acceptée · date : 2026-11-09 · validation : D-0088@bf8c3a4b · source : B-0138@1bc2f066, D-0047@58341bcf, ADR-0051@70b27ffe, J-2026-11-09-U@eecea2d0 · lu : decisions@ab7fa6bf

## Contexte

Un correctif livre un test qui échoue sans lui, que `tests.regression`
rejoue sur le commit d'avant. Un correctif qui ne touchait aucun fichier
qu'un adaptateur juge se jugeait par l'adaptateur principal (ADR-0051), et
exigeait un test de son langage, sans rapport avec le code corrigé : sur
une branche d'essai de JustCook, un correctif en Dart exigeait un test
Python (B-0138). Il n'en sortait qu'en retirant `fix:` de son titre, ou
par un test fabriqué. Théo a validé la règle (D-0088).

## Décision

- Un correctif dont aucun fichier n'est désigné par un adaptateur du
  projet (ni son code, ni ses sources, ni ses tests ; hors du dossier du
  socle et des fichiers tiers) reste refusé par `tests.regression`, avec un
  message qui nomme ses fichiers et donne trois issues : un adaptateur pour
  leur langage ; ces fichiers déclarés tiers, un assouplissement, donc par
  une demande ; ou une demande que l'humain valide, qui nomme ce commit et
  l'admet sans test.
- Admis ainsi, il passe en avertissement, qui nomme la demande, comme le
  correctif dont le test passe sur le parent (D-0047).
- Le hook du message de commit le dit dès le commit, au lieu de conseiller
  un test qui n'y pourrait rien.
- Un correctif qui touche un fichier qu'un adaptateur juge se juge comme
  avant.

## Conséquences

Aucun correctif ne passe sans preuve ni l'accord de l'humain ; chaque
admission coûte une demande, ce qui suppose ces correctifs rares, ce
qu'aucune mesure ne dit encore. La défaire : `hors_de_tout_adaptateur`
dans `engine/socle/checks_tests.py`, et ses tests dans
`tests/test_regression.py`.
