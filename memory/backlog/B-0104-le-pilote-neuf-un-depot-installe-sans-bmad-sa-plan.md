<!-- socle: couche=backlog zone=publique -->
# B-0104 — Le pilote neuf : un dépôt installé sans BMAD, sa planification faite à la main

> statut : en cours · origine : D-0051 · ref : D-0198 · lu : backlog@7d1ef046 · après : B-0323 · réserve : le pilote neuf, repris après JA-0006 dans l'ordre du chantier actif (D-0198) · trié : L-0056

Le pilote repart d'un dépôt neuf, installé depuis `main` sans BMAD, avec
le cadrage de Théo (D-0051) ; sa planification se fait d'abord à la main,
avant le skill de B-0101. Le moment
venu, Théo reçoit ce qu'il faut pour le lancer (J-2026-10-30-S) : la
création du dépôt, le prompt d'installation, les gestes sur GitHub, le
premier message de la session de travail. Ce qu'il montre se mesure ici :
les budgets du démarrage (B-0010), la pile à deux langages (B-0095).

Le 31 oct. (J-2026-10-31-A) : installé, la PR #1 de JustCook ouverte ;
la roadmap et le schéma que deux agents ont crus perdus l'étaient : le
cadrage est un artifact, dont l'export en Markdown les a perdus ; la
session de travail en reçoit le lien (J-2026-10-31-B).

À vérifier à sa prochaine mise à jour (J-2026-10-31-M) : qu'une session
cloud clone le dépôt public `theodubus/socle` sans l'ajouter.

Le 25 novembre, Théo le garde pour plus tard, après la mise à jour de
chess (D-0198) : il ne se clôt pas avec elle.

Le 28 novembre, sur D-0242 : le test qui gardait les skills du produit
sous 8 000 octets est retiré. JustCook, installé le 31 octobre, garde ce
plafond, que sa mise à jour ne touche pas : son prompt de mise à jour lui
fait poser la demande de passer à 10 000 octets la clé
`budgets.".claude/skills/*/SKILL.md".max_bytes` de ses garde-fous, et la
voir validée, avant d'en commiter les fichiers, comme chess l'a fait le
28 novembre ; sinon son hook avant commit refuse le skill trop long.
