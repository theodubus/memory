<!-- socle: couche=backlog zone=publique -->
# T-0129 — memoire.lectures accepte au hook avant envoi l'index qu'a cité un sous-agent parti avant le dernier push de la branche, comme la CI l'accepte

> statut : ouvert · origine : J-2026-11-21-Q · besoin : B-0272 · lu : backlog@6c894b15

Un commit : `memoire.lectures` (`engine/socle/checks_memory.py`) accepte aussi une version de l'index que connaît un commit de la branche du sous-agent, relié à la plage qui part par un ancêtre commun, quand la CI, qui juge depuis la branche par défaut, l'accepte ; le hook de l'agent ne change pas (ADR-0098) ; son témoin sain dans l'auto-test, le défaut d'une empreinte inventée gardé ; une note de version. Avant le code, B-0272 reçoit sa section « Modèle de menace » : ce que la lecture prouvée arrête encore, ce qu'elle laisse passer de plus. Les valeurs attendues de `tests/test_lectures.py` restent (cherché à la création, D-0141), dont celle de `test_une_lecture_recopiee_d_un_sujet_plus_ancien_est_refusee` : une lecture recopiée après un commit qui a changé l'index reste refusée, quand l'entrée du sous-agent cite l'index courant au départ de sa branche.

## Fait quand

- [ ] une entrée ouverte par un sous-agent parti avant un push de la branche s'intègre et se pousse sans être récrite, et une empreinte qu'aucune version connue de l'index n'a reste refusée ; un test montre les deux
- [ ] B-0272 a sa section « Modèle de menace », que `socle show B-0272` montre
