# La réponse donnée avant le lot de son changement : spécification

Soumise à Théo le 25 novembre 2026, avant son code, par la demande de
T-0179. Elle répond à B-0347 et lève la contradiction que ce besoin
relève ; deux pistes y sont pesées, chacune avec son modèle de menace.

## Le problème

Un test dont la valeur attendue change, ou qui disparaît, exige une
validation de l'humain qui le nomme (politique, point 2) : une demande
écrite, ou, pour un changement mécanique, une question dans la
conversation consignée en décision de séance (la variante légère). Deux
règles du produit en règlent le moment :

- **La demande tôt** (D-0141, le 19 novembre ; T-0134) : la tâche qui
  contredit un test le nomme dès qu'elle s'écrit, et sa demande se pose
  aussitôt, avant le lot, pour que le lot ne s'arrête pas en son milieu.
- **La réponse avec son changement** (B-0142, le 14 novembre) : la CI
  d'un push, et le hook avant push qui la reproduit, ne comptent que les
  validations ajoutées dans leur plage (B-0043). La réponse se commite
  donc avec le changement qu'elle autorise, dans le même push, jamais
  avant ; `demandes.reponse-seule` avertit quand elle part seule.

Ensemble, elles se contredisent dès que la réponse et le changement ne
tiennent pas dans la même session. Ici, un lot par session, et l'agent
fusionne sa pull request à la fin du lot (D-0092) : la réponse donnée
dans une session, avant le lot de son changement, n'a nulle part où
attendre. Le conteneur qui l'a reçue disparaît ; poussée seule, elle est
fusionnée avec la pull request de sa session, hors de la plage de toute
pull request suivante, et ne couvre plus le test.

Vu trois fois :

- le 24 novembre, la réponse de D-0174 a dû partir en correctif dans un
  dossier de passation pour rester avec ses deux tests
  (J-2026-11-24-Z) ;
- le même jour, Théo valide dans la conversation le changement d'un
  test de T-0174, un lot plus tôt : la validation n'a pas pu attendre,
  et le lot de T-0174 l'a redemandée (J-2026-11-24-AG, D-0184) ;
- avant, pour D-0083, D-0103 et D-0105, une réponse poussée trop tôt a
  dû être consignée une seconde fois (B-0142).

L'autre face, vue sur chess le 13 novembre (B-0142, gêne 6) : une
réponse donnée mais non consignée reste « en attente » dans l'état,
que l'humain voit, et que le récap lui redemande.

## Piste A — la règle des skills

Aucun contrôle ne change ; deux règles des skills du produit.

- **La variante légère** (`socle-request`) : l'humain qui répond, dans
  la conversation, avant le lot qui change le test, voit sa réponse
  écrite au journal aussitôt, mot pour mot, et poussée. Le lot qui
  change le test, dans une autre session, consigne la décision de
  séance à partir de ce texte, qu'il cite par son entrée du journal,
  dans le même push que le test.
- **La demande écrite d'un test** (`socle-batch`, qui change D-0141) :
  elle ne se pose plus dès que la tâche s'écrit, mais à l'annonce du lot
  qui change le test, dans sa session, avant ses sous-agents. La tâche
  écrite plus tôt nomme le test ; sa demande attend son lot. Si
  l'humain ne répond pas dans la session, le test se commite et se
  pousse sous la demande en attente (D-0147), la CI rouge jusqu'à sa
  réponse, et la session suivante continue la même pull request.

**Modèle de menace.** Aucun garde-fou ne change : `tests.attendus` et
le cliquet ne comptent toujours que les validations de leur plage.

**Ce qui reste.** La réponse attend au journal, que l'état ne lit pas :
un lot qui ne l'y trouve pas la redemande, comme le 24 novembre. Une
demande écrite posée avant son lot, par une session qui ne suit pas la
règle, retombe dans le problème. Sans réponse dans la session du lot,
le test se pousse sous la demande en attente (D-0147) : le lot ne
s'arrête pas, mais sa pull request finit rouge, l'agent ne peut la
fusionner (D-0092), et la session suivante la reprend. Dans un projet
installé où l'humain fusionne quand il veut, une réponse fusionnée avant
le changement ne le couvre pas davantage. Le critère de B-0347 (« un
test le montre ») n'est tenu que par un test qui lit le texte du skill.

**Coût.** Le texte de `socle-request` et de `socle-batch`, en français
et en anglais, un test qui le lit, une note de version, et leurs copies
protégées remises par une demande : de 1 à 2 points de la semaine.

## Piste B — une validation compte hors de sa plage tant que sa tâche est ouverte et que ce qu'elle nomme n'a pas bougé

### La règle

Une validation (la réponse `valider` d'une demande, ou une décision de
séance) couvre le changement de ce qu'elle nomme même poussée plus tôt,
dans un push précédent ou une autre pull request, depuis une autre
session. Tout se juge depuis le **point de départ** du travail jugé :
l'ancêtre commun de la branche par défaut et de la tête, d'où part sa
branche.

- **Ajoutée sur la branche depuis le point de départ**, dans la pull
  request en cours mais hors de la plage d'un push, elle couvre comme
  une validation de la plage. La CI de la pull request, jugée depuis ce
  point, la compte déjà ; la CI d'un push et le hook avant push s'y
  alignent. C'est le cas de B-0142, vu pour D-0083, D-0103 et D-0105 :
  la réponse poussée, puis le test au push suivant.
- **Déjà dans la branche par défaut au point de départ**, fusionnée avec
  une pull request précédente, elle couvre à deux conditions, jugées à
  ce point :

1. **Une tâche ouverte la cite.** Au point de départ, une tâche du
   backlog encore ouverte nomme la demande : celle qui fera le
   changement, que D-0141 fait écrire avec le test et sa demande, et qui
   cite la demande ou la décision de séance par son identifiant. Le lot
   qui fait le changement clôt cette tâche ; fusionnée dans la branche
   par défaut, la clôture épuise la validation.
2. **Ce qu'elle nomme n'a pas bougé.** Au point de départ, ce qu'elle
   nomme est tel qu'il était au parent du commit qui a ajouté la
   demande : ce que l'humain avait sous les yeux en répondant. Changé
   dans la branche par défaut par un autre chemin, il n'est plus
   couvert. Le parent du commit de la demande, et non celui de la
   réponse : la réponse vient avant le changement, avec lui ou après lui
   (D-0147), mais la demande le précède ou l'accompagne toujours, et ce
   parent garde la version d'avant, que la fusion se fasse par un commit
   de fusion, par squash ou par rebase.

Ce qu'elle nomme, comme aujourd'hui :

- un test, en mot entier (`tests.attendus`), comparé par son corps, son
  en-tête et ses attributs, dans le même fichier ;
- un fichier de cas cité (`tests.attendus`), comparé en entier ;
- une clé des garde-fous citée comme le cliquet la reconnaît
  (`cliquet.garde-fous`), comparée par sa valeur ;
- un fichier protégé cité avec son empreinte (`protege.fichiers`),
  comparé en entier.

`tests.regression`, qui admet un correctif nommé par son SHA dans une
validation de la plage, n'est pas concerné.

La règle d'aujourd'hui demeure : une validation ajoutée dans la plage
couvre ce qu'elle nomme. Les deux cas nouveaux s'y ajoutent ; un même
contrôle les lit tous.

Ce qu'elle résout, par cas :

| Cas | Aujourd'hui | Piste B |
| --- | --- | --- |
| Réponse poussée seule, le test changé au push suivant de la même pull request | push refusé | couvert : ajoutée depuis le point de départ |
| Réponse fusionnée avec une pull request, le test changé dans une suivante, sa tâche ouverte | refusé | couvert : ses deux conditions tenues |
| Le test changé, poussé, puis corrigé après la revue, au push suivant | push refusé, la pull request acceptée | couvert : ajoutée depuis le point de départ |
| Réponse et test dans le même commit, fusionnés avec la tâche close ; le test changé de nouveau ensuite | refusé | refusé : la tâche est close, et le test a bougé |
| Test poussé sous sa demande en attente (D-0147), puis la réponse, fusionnés par squash ; le test changé de nouveau | refusé | refusé, de même |
| Une demande ancienne nomme un test, aucune tâche ouverte ne la cite | refusé | refusé |

### Ce qui disparaît

- **`demandes.reponse-seule`**, l'avertissement de B-0142 : une réponse
  poussée seule couvre désormais son changement, il dirait faux. Le
  contrôle se retire, avec la fonction qui calcule sa plage
  (`base_non_poussee`), sa mention au hook avant push, ses deux défauts
  injectés de l'auto-test, `reponse-poussee-seule` et
  `reponse-poussee-sans-sa-cle`, et ses tests, dans
  `tests/test_reponse_seule.py`, sauf celui de la gêne 6 de chess
  (`test_une_reponse_consignee_mais_pas_commitee_n_est_plus_en_attente`),
  qui reste. La demande nomme chacun des tests retirés. Deux témoins
  sains de l'auto-test et sa table des raisons le nomment encore : leur
  affirmation reste vraie, seule la référence se retire.
- **La règle du même push**, dans `socle-request` (« jamais avant ») et
  dans le skill `delegate-lot` de ce dépôt : la réponse se consigne dès
  qu'elle est donnée, se commite et se pousse aussitôt, et la tâche qui
  fera le changement la cite. Elle n'est plus jamais « en attente » une
  fois donnée, et la règle de D-0141, la demande tôt, reste telle
  quelle.

### Modèle de menace

**Ce qu'il arrête, comme aujourd'hui.** Un test changé ou retiré, une
clé relâchée, un fichier de cas ou un fichier protégé changé, sans
aucune validation qui les nomme. Et, nouveau : un second changement de
la même chose une fois le premier fusionné avec la clôture de sa tâche ;
le stock des validations passées, qu'aucune tâche ouverte ne cite.

**Ce qu'il laisse passer, qu'il refusait.** Le changement couvert par
une validation poussée plus tôt, hors de la plage : ajoutée sur la
branche depuis son point de départ ; ou déjà dans la branche par
défaut, tant que sa tâche est ouverte et que ce qu'elle nomme n'a pas
bougé. C'est le but. L'âge d'une validation fusionnée n'est pas borné,
mais sa tâche le borne. Mesuré sur ce dépôt le 25 novembre : sur 149
validations (86 demandes écrites, 63 décisions de séance), 4 sont
citées par une tâche ouverte ; elles nomment 2 tests, tous deux changés
depuis : aucun test n'est couvert hors de sa pull request. Sans la
condition de la tâche, 31 tests nommés par des validations anciennes,
jamais changés depuis, le redeviendraient : la revue de cette
spécification l'a relevé. Une tâche ouverte qui cite une demande pour
mémoire, sans la mettre en œuvre, couvre de même les tests qu'elle
nomme, s'ils n'ont pas bougé ; aucun cas aujourd'hui. Dans une pull
request qui réunit plusieurs lots, fusionnée par l'humain quand il
veut, une validation ajoutée sur la branche couvre jusqu'à la fusion
plusieurs changements du même test, comme la CI de la pull request le
laisse déjà passer aujourd'hui.

**Ce qu'il ne voit pas, comme aujourd'hui.** Que le changement soit
celui que l'humain a validé : le contrôle lit le nom, pas les valeurs
avant et après ; le relecteur du lot le juge. Un test rétabli à
l'identique sur la branche par défaut, sa tâche encore ouverte, se lit
comme jamais changé. Un test déplacé dans un autre fichier ne se suit
pas : sa validation ne le couvre plus, ce qui est plus strict. Sans la
branche par défaut ni l'historique du commit de la demande (un clone
partiel), la règle nouvelle ne s'applique pas, et le contrôle le dit :
la règle d'aujourd'hui seule juge. La CI tire tout l'historique.

C'est un assouplissement d'un garde-fou : seule une demande validée le
permet (politique, point 1), celle qui soumet cette spécification.

### Coût

Une tâche, menée par un sous-agent : la règle dans `tests.attendus`,
le cliquet et `protege.fichiers`, ses défauts injectés (une validation
épuisée, sa réponse commitée avec son test, ne couvre pas un second
changement ; une validation qu'aucune tâche ouverte ne cite ne couvre
pas ; une validation fusionnée dont le test a bougé dans la branche par
défaut ne couvre pas ; témoins sains, une validation poussée au push
d'avant couvre, et une validation fusionnée, sa tâche ouverte, couvre),
ses tests, le retrait de `demandes.reponse-seule`, le
texte de `socle-request` et de `socle-batch` (la tâche cite sa demande)
en français et en anglais, le guide là où il en parle, une note de
version. De 3 à 4 points de la semaine, puis la copie protégée des
skills remise par une demande, et le prompt de mise à jour de chess.

## Recommandation

La piste B. Elle tient les deux faces de B-0142, ni push refusé, ni
réponse donnée affichée comme attendue ; elle vaut dans tout projet, pas
seulement en session cloud, partout où la réponse et son changement
partent dans deux pull requests ; elle garde D-0141 ; elle retire un
contrôle et une règle que l'agent doit retenir ; et un test montre le
critère de B-0347 directement. Son assouplissement est borné : la CI
d'un push s'aligne sur celle de la pull request ; au-delà, une
validation fusionnée ne compte que pour le travail d'une tâche encore
ouverte qui la cite, et tant que ce qu'elle nomme n'a pas bougé.

La piste A ne coûte que du texte, mais elle laisse la réponse attendre
au journal, que rien ne vérifie, change D-0141, et ne vaut que si
chaque session suit la règle.

## Ce qui suit la réponse

- **B** : une tâche qui l'implémente, dans le prochain lot du jalon
  JA-0005, avant le code de L-0038, dont les tests changeront sous une
  réponse donnée avant son lot ; T-0179 se ferme, et L-0037 avec elle.
- **A** : une tâche qui écrit les deux règles, dans `socle-request` et
  `socle-batch`.
- **Refusée** : la spécification se réécrit sur ce que Théo dit, et
  revient en demande ; d'ici là, rien ne change, et B-0347 reste ouvert.
