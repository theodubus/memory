<!-- socle: couche=decisions zone=publique -->
# ADR-0049 — Un agent coupé par une limite d'usage reprend seul à sa levée : un réveil par fenêtre pendant chaque tour de travail, qui ne reprend qu'une coupure par limite

> statut : abandonnée · date : 2026-11-08 · source : B-0132@cc8d5405, J-2026-11-08-H@3d8256b3, J-2026-11-08-I@4e3666a8, ADR-0048@daa1288e · lu : decisions@94e8477d

## Contexte

Une limite d'usage, de cinq heures ou de la semaine, coupe l'agent au
milieu de son travail, et il ne reprend qu'au message suivant de
l'humain. Théo veut qu'il reprenne seul (J-2026-11-08-H@3d8256b3), dans
le socle, sans réveiller un agent qu'aucune limite n'a coupé, en
reprenant les sous-agents coupés, la nuit comme le jour, et sans jamais
réveiller une session morte.

Les événements de la session le permettent (J-2026-11-08-I@4e3666a8). À
chaque appel au modèle, ils donnent l'utilisation de chaque fenêtre et
l'heure de sa remise à zéro ; au-delà de 90 %, un avertissement ; à la
coupure, un refus, et un tour fini en erreur `usage_limit_reached`. Un
message programmé qui tombe pendant la limite ouvre un tour, refusé puis
perdu ; programmé après la remise à zéro, il ouvre un tour accepté. La
cause de la fin d'un tour, une limite, une interruption de l'humain, ou
sa fin normale, s'y lit.

ADR-0048@daa1288e, abandonnée, calait un seul réveil sur la fenêtre la
plus remplie : il tombait lundi quand la fenêtre de cinq heures coupait
le soir même ; et un tour que l'humain interrompt laissait un réveil qui
relançait l'agent.

## Décision

**1. Un réveil par fenêtre, le temps d'un tour de travail.** Au début de
chaque tour qui travaille (un lot, une revue, un correctif, et non une
simple réponse), l'agent lit son utilisation et arme deux réveils, des
messages à sa session : l'un cinq minutes après la remise à zéro de la
fenêtre de cinq heures, l'autre cinq minutes après celle de la semaine, à
toute heure. Un tour qui commence déplace les réveils qu'il trouve, sans
en ajouter. À la fin du tour, qu'il finisse seul ou sur une interruption
de l'humain, l'agent les retire. Sans seuil d'utilisation.

**2. Les réveils portent le travail en cours.** Leur message dit le lot,
l'étape, et chaque sous-agent lancé avec ce qu'il devait rendre. Avant de
lancer un sous-agent, et à chaque étape, l'agent les récrit.

**3. Au réveil, l'agent ne reprend qu'une coupure par limite, dans une
session vivante.** Il lit d'abord comment son dernier tour a fini : s'il
n'a pas fini en erreur `usage_limit_reached`, il retire les réveils
restants et ne fait rien. Il ne fait rien non plus si une autre session a
poussé sur sa branche depuis son dernier commit, si sa pull request est
fusionnée ou fermée sans travail restant, ou si l'humain lui a dit
d'arrêter. Sinon il retire l'autre réveil, reprend l'étape notée, et
relance chaque sous-agent dont le résultat n'est pas arrivé, avec le même
message. Le tour de reprise, s'il travaille, arme ses propres réveils.

**4. La procédure vit dans un skill du socle, `socle-reprise`.** Elle
dépend de l'agent et de ses outils de session cloud : le moteur n'en sait
rien, et aucun contrôle ne prouve que l'agent l'applique. L'installeur
pose le skill dans tout projet, et la politique le protège, comme les
autres skills du socle. Hors d'une session cloud de Claude Code, sans ces
outils, il est inerte.

## Conséquences

Un agent coupé par une limite reprend seul, cinq minutes après sa levée,
jour et nuit, quelle que soit son utilisation au moment de la coupure. Un
agent qu'aucune limite n'a coupé n'est jamais repris : les réveils sont
retirés à la fin du tour, et celui qui tomberait quand même constate que
le tour n'a pas fini sur une limite. Une session morte n'est jamais
reprise : un réveil ne naît que dans un tour vivant, ne tombe qu'une fois,
et l'agent vérifie la session avant de rien faire. Armer, déplacer et
retirer coûtent quelques appels d'outil par tour, pas un tour de plus.
Qu'un réveil reprenne bien une session coupée reste à mesurer : la
première coupure réelle le dira ; sinon B-0132 reste ouvert, et le skill
se retire ou se corrige par une demande. Se défait en retirant le skill.
