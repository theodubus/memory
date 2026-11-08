<!-- socle: couche=decisions zone=publique -->
# ADR-0048 — Un agent coupé reprend seul à la levée de sa limite d'usage : un réveil armé pendant chaque tour de travail, retiré à sa fin normale

> statut : abandonnée · date : 2026-11-08 · source : B-0132@cc8d5405, J-2026-11-08-H@3d8256b3, ADR-0047@6c9bbf4f · lu : decisions@a3981c9d

## Contexte

Une limite d'usage, de cinq heures ou de la semaine, coupe l'agent au
milieu de son travail, et il ne reprend qu'au message suivant de
l'humain. Deux check-ins programmés, tombés pendant la limite, n'ont été
lus qu'alors (J-2026-11-08-G@a0ca8d26). Théo a refusé un rappel récurrent
(J-2026-11-08-H@3d8256b3), et posé six exigences : la solution est dans le
socle ; elle ne réveille pas un agent qu'aucune limite n'a coupé ; elle
reprend les sous-agents coupés ; elle vaut la nuit comme le jour ; elle ne
réveille jamais une session morte, projet inactif ou session abandonnée ;
et l'agent lit ses limites.

En session cloud de Claude Code, l'agent les lit : chaque appel au modèle
enregistre dans les événements de la session (`rate_limit_event`, lus par
`list_events`) l'utilisation de la fenêtre de cinq heures et de celle de
sept jours, et l'heure exacte de leur remise à zéro. Il peut programmer un
message à sa propre session (`send_later`), le déplacer et le retirer.

ADR-0047@6c9bbf4f armait un réveil au-delà de 80 % d'une fenêtre, s'il
restait du travail. Sa relecture à froid y a trouvé deux défauts : un
agent qui finit normalement son tour au-delà du seuil, du travail restant,
était réveillé quand même ; et une coupure soudaine, sous le seuil, n'était
pas couverte. Le 8 novembre, la reprise de cette session a coûté 12 % de
la fenêtre de cinq heures en un seul appel : un seuil laisse passer de
telles coupures. ADR-0047 est abandonnée.

## Décision

**1. Un réveil vit le temps d'un tour de travail.** Au début de chaque
tour qui travaille (un lot, une revue, un correctif, et non une simple
réponse), l'agent lit son utilisation et arme un réveil : un message à sa
session, programmé cinq minutes après la remise à zéro de la fenêtre la
plus remplie, à toute heure. À la fin normale du tour, il le retire. Seul
un tour coupé avant sa fin laisse donc un réveil : un agent qu'aucune
limite n'a coupé n'en reçoit jamais. Il n'en tient qu'un par session, sans
seuil d'utilisation.

**2. Le réveil porte le travail en cours.** Son message dit le lot,
l'étape, et chaque sous-agent lancé avec ce qu'il devait rendre. Avant de
lancer un sous-agent, et à chaque étape, l'agent le récrit, et le déplace
si la remise à zéro a changé.

**3. Au réveil, l'agent vérifie d'abord que la session vit encore.** Il
ne fait rien, et ne réarme rien, si une autre session a poussé sur sa
branche depuis son dernier commit, si sa pull request est fusionnée ou
fermée sans travail restant, ou si l'humain lui a dit d'arrêter. Sinon il
reprend l'étape notée, relance chaque sous-agent dont le résultat n'est pas
arrivé, avec le même message, puis travaille comme à tout tour : ce tour
arme son propre réveil.

**4. La procédure vit dans un skill du socle, `socle-reprise`.** Elle
dépend de l'agent et de ses outils de session cloud : le moteur n'en sait
rien. L'installeur pose le skill dans tout projet, et la politique le
protège, comme les autres skills du socle. Hors d'une session cloud, sans
ces outils, il est inerte.

## Conséquences

Un agent coupé reprend seul, au plus tard cinq minutes après la levée de
la limite, jour et nuit, quelle que soit son utilisation au moment de la
coupure. Une session morte n'est jamais réveillée : un réveil ne naît que
dans un tour vivant, ne tombe qu'une fois, et ne se réarme que si le tour
qu'il ouvre travaille. Chaque tour de travail coûte deux appels de plus,
armer et retirer. Qu'un réveil reprenne bien une session coupée est
supposé : la première coupure réelle le mesurera ; s'il ne la reprend pas,
B-0132 reste ouvert et l'humain relance comme aujourd'hui. Se défait en
retirant le skill.
