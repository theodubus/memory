<!-- socle: couche=demandes zone=publique -->
# D-0029 — Changer deux tests du format 3 que contredit le rangement des sujets clos

> date : 2026-10-15 · lu : decisions@9a83834a

## Décision demandée

Valider le changement de deux tests de `tests/test_format_3.py` qui
affirment l'ancienne règle, « un sujet clos reste dans son fichier », que
tu viens de remplacer en validant le rangement des sujets clos dans un
sous-dossier.

## Contexte

Tu as répondu `sous-dossier` à la demande sur la place des sujets clos du
backlog. Le rangement est écrit : `socle archive` déplace un sujet clos
dans le sous-dossier `closed` du backlog, le contrôle du backlog refuse un
sujet mal rangé, la migration et la mise à jour rangent les projets
existants. Toute la suite de tests passe, sauf deux tests écrits pour
l'ancienne règle. La politique (point 2) interdit de supprimer un test ou
de changer une valeur attendue sans une demande validée qui le nomme : ta
réponse sur le rangement ne les nommait pas. Rien n'est commité ; le code
attend ta réponse dans mon arbre de travail.

Les deux tests, et ce qui change :

1. `TestApresLaMigration.test_un_sujet_clos_reste_dans_son_fichier`
   vérifie que `socle archive` ne fait rien au format 3 (« rien ne
   s'archive ») et que le sujet clos reste à sa place. Il est remplacé par
   `test_un_sujet_clos_se_range_avec_les_clos`, qui vérifie l'inverse : le
   sujet clos par la migration est déjà rangé ; un sujet qu'on clôt
   ensuite fait refuser le contrôle avec la commande à lancer ; `socle
   archive` le range et indexe le déplacement ; le contrôle passe ;
   l'état compte deux sujets clos.
2. `TestMigration.test_un_fichier_par_sujet_sans_rien_perdre` lit le
   fichier d'un sujet clos à sa place d'avant ; seul ce chemin change, vers
   le sous-dossier `closed`. Ses assertions ne changent pas.

Cinq tests nouveaux s'ajoutent, sans validation requise : un sujet rouvert
revient parmi les ouverts, un sujet rangé garde le plafond d'un sujet, la
bascule en privé garde le rangement, la mise à jour range un projet
existant, et la lecture reconnaît le sous-dossier. Chacun échoue sans le
changement.

## Éléments cités

- D-0028@aa33fbf6 — ta demande validée : les sujets clos du backlog vont
  dans un sous-dossier, rangés par le moteur.
- ADR-0030@8d5490d8 — la décision qui l'écrit, et qui remplace ce point de
  la décision du 13 oct. sur le backlog en dossier.

## Où regarder

- [le premier test, tel qu'il est](https://github.com/theodubus/memory/blob/c31e4a69d20414bbabf1cdc93b4294bc6490e688/tests/test_format_3.py#L91-L97) :
  il affirme que `socle archive` ne range rien ; c'est lui qui est remplacé.
- [le second test, tel qu'il est](https://github.com/theodubus/memory/blob/c31e4a69d20414bbabf1cdc93b4294bc6490e688/tests/test_format_3.py#L52-L63) :
  la ligne 55 lit le sujet clos à son ancienne place ; seul ce chemin
  change.
- [ta demande validée sur le rangement](https://github.com/theodubus/memory/blob/c31e4a69d20414bbabf1cdc93b4294bc6490e688/memory/requests/D-0028-ranger-les-sujets-clos-du-backlog-dans-un-sous-dos.md) :
  la règle que ces deux tests suivraient.

À vérifier : que ces deux changements suivent bien la règle que tu as
validée, et rien de plus.

## Options

- **Valider** : je commite le rangement avec ces deux tests changés,
  l'auto-test et les tests nouveaux, je range le backlog de ce dépôt (25
  sujets clos à déplacer) et je pousse. Effort : une heure, la vérification
  complète comprise. Risque faible : les deux tests changent dans le sens
  de la règle validée. Réversible : un commit qui se défait.
- **Refuser** : je retire le rangement de mon arbre ; les sujets clos
  restent à leur place, malgré ta réponse sur le rangement. Effort nul ;
  aucun risque ; la liste du dossier reste mêlée.

## Conséquences

- Si tu valides : je commite et je pousse le rangement, puis je te donne
  le lien du dossier rangé.
- Si tu refuses : rien n'est commité ; la demande sur le rangement reste
  sans effet, et je te demande comment en tenir compte.
- Sans réponse : rien n'est commité ; le travail reste dans mon arbre, et
  j'attends.

## Recommandation

Valider. Vérifié : toute la suite passe avec ces deux changements (558
tests), l'auto-test aussi (le défaut nouveau est attrapé, son témoin sain
passe) ; sans le changement du code, les deux tests changés et les cinq
nouveaux échouent. Supposé : rien d'autre ; la vérification complète se
relance avant le commit.

## Réponses possibles

- `valider` — je commite le rangement avec ces deux tests changés, et je range le backlog de ce dépôt.
- `refuser` — je retire le rangement ; les sujets clos restent à leur place.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
