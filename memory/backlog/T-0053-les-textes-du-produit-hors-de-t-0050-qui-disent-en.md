<!-- socle: couche=backlog zone=publique -->
# T-0053 — Les textes du produit hors de T-0050 qui disent encore « sujet » d'une entrée du backlog, ou « tâche » du travail en général

> statut : ouvert · origine : J-2026-11-16-V · besoin : B-0265 · lu : backlog@e7a68d02

Relevé par la revue du lot L-0013, passe 1 (J-2026-11-16-V), constats 5
et 6 pour le backlog : des textes du produit disent encore « sujet »
d'une entrée du backlog, hors de la liste de T-0050, que des tests ne
lisent pas mot pour mot : `engine/socle/templates/initialization.md`
(« chaque objectif devient un sujet du backlog », et « backlog topic » en
anglais), la docstring de `memoire.lectures` que `socle checks` affiche,
l'aide de `socle review` (`engine/socle/cli.py`), les libellés des
défauts injectés et un témoin de `engine/socle/selftest.py`. Et le guide
dit « tâche » du travail en général (`engine/socle/HELP.md`, lignes 13 et
105, et l'anglais), quinze lignes avant de définir la tâche `T-`. Le
livrable, un commit : ces textes disent l'entrée, le besoin, la tâche, le
lot ou le jalon, chacun pour sa chose.

## Fait quand

- [ ] les textes nommés ici n'appellent plus « sujet » une entrée du backlog, ni « tâche » autre chose qu'une tâche `T-`, et un test le montre pour le guide
