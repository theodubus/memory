<!-- socle: couche=demandes zone=publique -->
# D-0059 — Ajouter aux questions de départ le choix de la livraison, et passer à 6 le nombre de questions qu'attend test_rien

> date : 2026-10-31

## Décision demandée

Valider que les questions de départ, que `socle init` pose à tout projet
neuf, ajoutent une sixième question, le choix de la livraison, et que le
test `test_rien`, qui en compte cinq, en attende six.

## Contexte

Vous avez tranché en séance la livraison par défaut (D-0058@ad1cea8b,
`branche-de-dev`) : une branche de développement où tout se fait, avec
une seule pull request ouverte à la fois ; une branche et une pull request
par sujet en option, « a décider au début ». Les instructions que pose le
socle le disent déjà, sur la branche en cours. Reste le « au début » : la
demande des questions de départ, la première qu'un projet reçoit, est
l'endroit où ce choix se fait. La question ajoutée, telle qu'elle se
lirait :

> **Le travail se livre-t-il par une branche de développement, une seule
> pull request ouverte à la fois, ou par une branche et une pull request
> par sujet ?** Défaut : une branche de développement : chaque lot fini
> s'ajoute à la pull request ouverte, que tu fusionnes quand tu veux. Ce
> que ça change : une pull request par sujet se relit sujet par sujet,
> mais il y en a une à fusionner par sujet ; le choix devient un fait de
> la mémoire, que l'agent suit.

Les questions passent ainsi de cinq à six, sous le plafond de sept que
fixe la politique. Le test `test_rien` vérifie qu'un projet vide reçoit
cinq questions : sa valeur attendue passerait à six. Changer une valeur
attendue d'un test revient à vous (politique, point 2), et votre décision
en séance ne nommait pas ce test. Le changement attend donc votre réponse,
hors de la branche poussée ; un test nouveau vérifie la question et son
défaut.

## Éléments cités

- D-0058@ad1cea8b — votre décision en séance : la livraison par défaut sur une branche de développement, une pull request par sujet en option choisie au départ.
- `test_rien` — le test de l'initialisation qui compte les questions de départ d'un projet vide.

## Où regarder

- [les questions de départ](https://github.com/theodubus/memory/blob/cd4d9966d758a5af018bb524e9eccb8ca9adccdd/engine/socle/initialization.py#L103) : les cinq questions actuelles ; la sixième s'insère avant celle des contraintes.
- [le test `test_rien`](https://github.com/theodubus/memory/blob/cd4d9966d758a5af018bb524e9eccb8ca9adccdd/tests/test_initialisation.py#L256) : la valeur attendue, 5, qui passerait à 6.

## Options

- **Ajouter la question** : un projet neuf choisit sa livraison au départ, d'un mot, ou garde le défaut en validant tous les défauts. Effort : nul, le changement est prêt. Risque : une question de plus à lire au départ. Réversible.
- **Ne pas l'ajouter** : la livraison par défaut vaut quand même ; une pull request par sujet se choisit en le disant à l'agent, qui l'écrit en fait de la mémoire, comme le guide le dit déjà. Effort : nul. Risque : le choix ne se présente pas au début, contrairement à votre décision. Réversible.

## Conséquences

- Si vous validez : la question et le test qui attend six questions se commitent dans la pull request en cours, et le guide nomme les questions de départ comme l'endroit du choix.
- Si vous refusez : rien ne change ; le choix se fait en le disant à l'agent.
- Sans réponse : le changement reste hors de la pull request, qui peut se fusionner sans lui.

## Recommandation

Ajouter la question : c'est le « a decider au début » de votre décision, et la valider ne coûte qu'un mot au départ de chaque projet.

Vérifié : avec la question, la suite des tests de l'initialisation passe, sauf `test_rien`, qui attend cinq questions ; le test nouveau passe.

Supposé : qu'un projet choisisse rarement la pull request par sujet ; le défaut couvre le cas courant.

## Réponses possibles

- `valider` — la question s'ajoute, et `test_rien` attend six questions.
- `refuser` — rien ne change ; le choix se fait en le disant à l'agent.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
