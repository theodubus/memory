<!-- socle: couche=decisions zone=publique -->
# ADR-0060 — Les réveils de reprise s'arment une fois par tour, jamais dans le passé, et ne se récrivent qu'au lancement d'un sous-agent

> statut : acceptée · date : 2026-11-11 · source : B-0155@50294243, ADR-0050@da14d54e, D-0093@333ad9d0, J-2026-11-10-N@bcf0f6ad · lu : decisions@f027321a

## Contexte

ADR-0050@da14d54e fait armer les deux réveils de reprise au début de
chaque tour qui agit, récrire leur texte à chaque étape et à chaque
sous-agent lancé ou rendu, et les retirer à la fin. L'usage l'a mesuré
coûteux : à chaque tour, lire les remises à zéro dans les événements de
la session (plusieurs kilo-octets), lister les réveils, en armer ou
déplacer deux, les récrire à chaque étape (deux appels, plusieurs
kilo-octets chacun), en retirer deux ; soit sept appels plus deux par
étape et par sous-agent. La passe de recul l'a relevé (D-0093@333ad9d0,
proposition 1, validée : J-2026-11-10-N@bcf0f6ad). Deux fois le 10
novembre, un réveil armé à une heure déjà passée, l'heure lue datant
d'une fenêtre close, s'est déclenché aussitôt. Et un réveil d'une fenêtre
écoulée, resté armé alors que l'humain avait écrit pendant la coupure,
a tiré après que l'agent avait repris sur son message : un tour pour rien.

## Décision

Elle amende les points 1 à 4 d'ADR-0050 ; le reste tient.

1. *Une fois par tour.* Au début d'un tour qui agit, l'agent arme les deux
   réveils, une fois. L'heure d'une remise à zéro lue plus tôt dans la
   conversation, encore à venir, vaut sans relire (une fenêtre ne se
   remet pas à zéro avant son heure) ; l'identifiant de la session se lit
   dans son lien avant `get_session`. Les réveils laissés par un tour
   d'avant, la conversation les montre ; `list_triggers` ne sert qu'après
   un compactage qui les a perdus.
2. *Jamais dans le passé.* L'heure courante se lit (`date -u`, ou `now`
   que rend l'outil). Une remise à zéro lue qui n'est pas à plus d'une
   minute dans l'avenir vient d'une fenêtre close : le réveil s'arme à la
   borne, maintenant plus la durée de la fenêtre plus cinq minutes, tard
   mais jamais à tort.
3. *Un tour qui s'ouvre fait siens les réveils restants*, sur un message
   de l'humain comme sur un réveil : la coupure qu'ils gardaient est
   finie ; celui dont l'heure est encore la bonne reste, l'autre se
   déplace à l'heure du tour, et un tour en texte seul les retire. Un
   réveil laissé garde le texte du lot d'avant, qui ferait reprendre
   l'ancien lot si ce tour était coupé : l'appel qui le déplace lui donne
   aussi le texte du lot du tour (`update_trigger` prend l'heure et le
   texte ensemble), sans appel de plus ; celui qui reste ne le reçoit que
   si le lot a changé (revue du lot).
4. *Récrits, en cours de tour, au seul lancement d'un sous-agent*, une
   fois pour ceux lancés ensemble. Leur texte porte le lot et les sous-agents en cours, plus
   l'étape : au réveil, la conversation, git, le chantier actif et les
   worktrees la disent. Un sous-agent qui rend ne demande rien.
5. La fin du tour et la vérification au réveil restent celles
   d'ADR-0050 (points 3 et 4) ; au réveil, l'agent reprend le lot à
   l'étape que ces sources disent.

Le compte, par tour sans sous-agent : avant, sept appels plus deux par
étape ; après, cinq (une lecture de l'heure, deux armements, deux
retraits), quatre quand l'heure lue vaut encore, plus deux par lancement
de sous-agents.

## Conséquences

Ce qu'elle garde : deux réveils par tour qui agit, retirés à sa fin sauf
sous-agent en cours, la vérification au réveil, qui ne relance qu'un
agent coupé, et rien dans le moteur. Ce qu'elle abandonne : le texte à
jour de l'étape, et le recalage d'une heure pendant le tour ; une
fenêtre remise à zéro pendant un tour long laisse tirer son réveil, qui
attend la fin du tour et ouvre un tour d'une ligne, le cas qu'ADR-0050
admettait déjà d'une étape longue, devenu celui de tout tour long. Un réveil armé à la borne reprend plus tard qu'il ne
pourrait, jusqu'à cinq heures, ou sept jours pour la semaine, si la
lecture de l'heure ment encore ; le tour suivant le recale. La défaire :
rétablir le texte du skill d'ADR-0050, sans demande, la décision étant
réversible. Les copies posées dans les projets, protégées, se
rafraîchissent par l'installeur.
