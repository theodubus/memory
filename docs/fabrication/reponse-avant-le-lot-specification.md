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
règle, retombe dans le problème. La demande tardive peut de nouveau
arrêter un lot en son milieu, ce que D-0141 évitait. Dans un projet
installé où l'humain fusionne quand il veut, une réponse fusionnée avant
le changement ne le couvre pas davantage. Le critère de B-0347 (« un
test le montre ») n'est tenu que par un test qui lit le texte du skill.

**Coût.** Le texte de `socle-request` et de `socle-batch`, en français
et en anglais, un test qui le lit, une note de version, et leurs copies
protégées remises par une demande : de 1 à 2 points de la semaine.

## Piste B — une validation compte hors de sa plage tant que ce qu'elle nomme n'a pas changé

### La règle

Une validation (la réponse `valider` d'une demande, ou une décision de
séance) couvre le changement de ce qu'elle nomme, même poussée plus tôt,
dans une autre pull request, depuis une autre session, tant que la
branche par défaut ne l'a pas encore reçu. Deux points de la branche
par défaut se comparent : celui d'où partait la branche où la réponse a
été ajoutée (l'ancêtre commun de la branche par défaut et du commit de
la réponse), ce que l'humain avait sous les yeux ; et celui d'où part
le travail jugé (l'ancêtre commun de la branche par défaut et de la
tête). Si ce qu'elle nomme y est identique, la validation couvre son
changement. Ce changement fusionné dans la branche par défaut, les deux
points diffèrent : la validation est épuisée, et un changement suivant
de la même chose en demande une nouvelle.

Ce qu'elle nomme, comme aujourd'hui :

- un test, en mot entier (`tests.attendus`), comparé par son corps, son
  en-tête et ses attributs, dans le même fichier ;
- un fichier de cas cité (`tests.attendus`), comparé en entier ;
- une clé des garde-fous citée comme le cliquet la reconnaît
  (`cliquet.garde-fous`), comparée par sa valeur ;
- un fichier protégé cité avec son empreinte (`protege.fichiers`),
  comparé en entier.

La règle d'aujourd'hui demeure : une validation ajoutée dans la plage
couvre ce qu'elle nomme. La règle nouvelle s'y ajoute ; un même
contrôle les lit toutes deux.

Ce qu'elle résout, par cas :

| Cas | Aujourd'hui | Piste B |
| --- | --- | --- |
| Réponse poussée seule, le test changé au push suivant de la même pull request | push refusé | couvert |
| Réponse fusionnée avec une pull request, le test changé dans une suivante | refusé | couvert |
| Le test changé, poussé, puis corrigé après la revue, au push suivant | push refusé, la pull request acceptée | couvert, comme par la pull request |
| Le même test changé de nouveau après la fusion du premier changement | refusé | refusé : la validation est épuisée |

### Ce qui disparaît

- **`demandes.reponse-seule`**, l'avertissement de B-0142 : une réponse
  poussée seule couvre désormais son changement, il dirait faux. Le
  contrôle se retire, avec la fonction qui calcule sa plage
  (`base_non_poussee`), sa mention au hook avant push, ses deux défauts
  injectés de l'auto-test, `reponse-poussee-seule` et
  `reponse-poussee-sans-sa-cle`, et ses tests, dans
  `tests/test_reponse_seule.py`, sauf celui de la gêne 6 de chess
  (`test_une_reponse_consignee_mais_pas_commitee_n_est_plus_en_attente`),
  qui reste. La demande nomme chacun des tests retirés.
- **La règle du même push**, dans `socle-request` (« jamais avant ») et
  dans le skill `delegate-lot` de ce dépôt : la réponse se consigne dès
  qu'elle est donnée, se commite et se pousse aussitôt. Elle n'est plus
  jamais « en attente » une fois donnée, et la règle de D-0141, la
  demande tôt, reste telle quelle.

### Modèle de menace

**Ce qu'il arrête, comme aujourd'hui.** Un test changé ou retiré, une
clé relâchée, un fichier de cas ou un fichier protégé changé, sans
aucune validation qui les nomme. Et, nouveau : un deuxième changement
de la même chose sous une validation déjà épuisée par un premier,
fusionné.

**Ce qu'il laisse passer, qu'il refusait.** Le changement couvert par
une validation poussée plus tôt, hors de la plage, quand rien de ce
qu'elle nomme n'a changé depuis sur la branche par défaut : c'est le
but. Une validation ancienne, de plusieurs semaines, couvre de même un
changement tardif, même si le projet a bougé autour du test : son âge
n'est pas borné. Dans une pull request qui réunit plusieurs lots,
fusionnée par l'humain quand il veut, une validation couvre aussi un
second changement du même test avant la fusion : la CI de la pull
request le laisse déjà passer aujourd'hui, la CI des pushes s'y aligne.

**Ce qu'il ne voit pas, comme aujourd'hui.** Que le changement soit
celui que l'humain a validé : le contrôle lit le nom, pas les valeurs
avant et après ; le relecteur du lot le juge. Un test rétabli à
l'identique sur la branche par défaut, après un changement validé, se
lit comme jamais changé, et sa validation d'origine le couvre de
nouveau ; il faut pour cela un premier changement validé, puis un retour
exact. Un test déplacé dans un autre fichier ne se suit pas : sa
validation ne le couvre plus, ce qui est plus strict. Sans la branche
par défaut ni l'historique du commit de la réponse (un clone partiel),
la règle nouvelle ne s'applique pas, et le contrôle le dit : la règle
d'aujourd'hui seule juge. La CI tire tout l'historique.

C'est un assouplissement d'un garde-fou : seule une demande validée le
permet (politique, point 1), celle qui soumet cette spécification.

### Coût

Une tâche, menée par un sous-agent : la règle dans `tests.attendus`,
le cliquet et `protege.fichiers`, ses défauts injectés (une validation
épuisée ne couvre pas ; une validation poussée plus tôt couvre, témoin
sain), ses tests, le retrait de `demandes.reponse-seule`, le texte de
`socle-request` en français et en anglais, le guide là où il en parle,
une note de version. De 3 à 4 points de la semaine, puis la copie
protégée de `socle-request` remise par une demande, et le prompt de
mise à jour de chess.

## Recommandation

La piste B. Elle tient les deux faces de B-0142, ni push refusé, ni
réponse donnée affichée comme attendue ; elle vaut dans tout projet, pas
seulement en session cloud, partout où la réponse et son changement
partent dans deux pull requests ; elle garde D-0141 ; elle retire un
contrôle et une règle que l'agent doit retenir ; et un test montre le
critère de B-0347 directement. Son assouplissement est borné : une
validation par changement, tant que ce qu'elle nomme n'a pas bougé sur
la branche par défaut.

La piste A ne coûte que du texte, mais elle laisse la réponse attendre
au journal, que rien ne vérifie, change D-0141, et ne vaut que si
chaque session suit la règle.

## Ce qui suit la réponse

- **B** : une tâche qui l'implémente, au jalon JA-0005, dans un lot
  neuf après L-0038 ; T-0179 se ferme, et L-0037 avec elle.
- **A** : une tâche qui écrit les deux règles, au même endroit.
- **Refusée** : la spécification se réécrit sur ce que Théo dit, et
  revient en demande ; d'ici là, rien ne change, et B-0347 reste ouvert.
