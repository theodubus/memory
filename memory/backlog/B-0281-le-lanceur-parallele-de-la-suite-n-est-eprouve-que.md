<!-- socle: couche=backlog zone=publique -->
# B-0281 — Le lanceur parallèle de la suite n'est éprouvé que sur la suite rapide de ce jour : rien ne fige sa parité avec unittest discover, son bilan compte ce qu'un test imprime, un module bloqué le bloque sans être nommé, la vérification complète n'est pas relevée

> statut : ouvert · après : D-0130 · origine : J-2026-11-17-J · lu : backlog@1df796e8

Les constats sans bloquant de la passe 1 de la revue du lot L-0012
(J-2026-11-17-J) sur le lanceur `tests/parallele.py` de T-0044, chacun
avec sa nature :

- Vérifié par le relecteur : aujourd'hui, le lanceur et `unittest
  discover -s tests -t .` prennent les mêmes 54 modules. Par
  construction, ils diffèrent : discover prend `test*.py`, dans les seuls
  paquets ; le lanceur prend `test_*.py`, dans tout sous-dossier. Un
  fichier de tests nommé testX.py sauterait en silence, et rien ne le
  rattrape.
- Mesuré par le relecteur, une fois : sortie standard tamponnée (sans
  `PYTHONUNBUFFERED`), ce qu'un test imprime arrive après le résumé de
  `unittest`, sur le flux que le lanceur lit, et le bilan le compte : un
  module d'un seul test donne « tests : 99 ». Le compte du bilan ne
  prouve pas la parité.
- Mesuré par le relecteur : un module qui ne rend jamais la main bloque
  le lanceur, qui n'imprime rien ; sous `verify`, le délai de l'étape dit
  « délai dépassé » sans nommer le module, et ses processus survivent.
  `discover` faisait de même : ce n'est pas une régression.
- Lu dans le code, non mesuré : hors de `--fast` et de la CI,
  `test_autotest` lance l'auto-test du socle sur quatre fils ; avec le
  lanceur, il tourne en même temps que trois autres modules, dont des
  tests qui mesurent des délais. `verify` complet n'a pas été relevé avec
  le lanceur.

Il attend la réponse à D-0130 : si Théo protège le lanceur, chaque tâche
qui le change passe par une demande.

## Satisfait quand

- [ ] le lanceur lance les modules que `unittest discover` lancerait, et un test le vérifie
- [ ] un module bloqué est arrêté, nommé et compté en échec
- [ ] `verify` complet passe avec le lanceur, sa durée relevée
