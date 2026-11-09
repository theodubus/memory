<!-- socle: couche=demandes zone=publique -->
# D-0086 — Valider une règle née des gênes du pilote : une citation qui survit à un changement de métadonnées

> date : 2026-11-09

## Décision demandée

Valider qu'une citation d'une entrée de la mémoire reste valide quand
l'entrée citée ne change que sa ligne de métadonnées, ce qui change ce
qu'attend un test existant.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA : il tient la mémoire
du projet, et des contrôles automatiques vérifient ce que l'agent produit.
JustCook, votre application de cuisine, est le projet pilote : l'agent qui
y travaille vous rapporte ce qui le gêne dans le socle, et vous me le
transmettez.

**Le chantier.** Le 8 novembre, l'agent de JustCook vous a rapporté six
gênes. Ce 9 novembre, vous avez demandé qu'elles soient réglées avant la
prochaine mise à jour du socle installé dans JustCook. Trois sont réglées
(un lien qui visait le mauvais commit, un commit refusé à tort, une CI
restée rouge pendant une mise à jour, que la façon de commiter une mise à
jour, validée le 2 novembre, évite déjà). Les trois autres vous sont
posées ce jour, chacune dans sa demande ; celle-ci porte sur la première.

**La question.** La règle touche la lecture prouvée par empreinte, que
vous aviez proposée le 10 octobre, et change ce qu'un test existant
attend : rien de cela ne se fait sans votre accord.

### Ce qui gêne

Dans la mémoire du projet, chaque entrée (un sujet du backlog, la liste
des travaux à faire ; une décision ; une demande comme celle-ci) a un
titre, puis une ligne de métadonnées : son statut, son origine, ce qu'elle
attend (`après`), ce que l'agent a lu avant de l'écrire (`lu`). Quand
l'agent s'appuie sur une entrée, il la cite avec son empreinte : son
identifiant, une arobase, et les huit premiers caractères d'une somme de
contrôle de son texte. La décision du 10 octobre dit ce que cela prouve :
« que le texte de cette version est passé par les outils de l'agent, et
qu'il n'a pas changé depuis » ; et ce que cela ne prouve pas : « qu'il a
été compris, ni qu'il a été lu en entier ». « La règle vise l'oubli, pas
la fraude. »

Une citation se contrôle quand elle est écrite : elle doit correspondre à
la version actuelle de l'entrée citée, ou à celle du commit où la citation
est apparue. Une fois commitée, elle n'est plus recontrôlée.

Aujourd'hui, l'empreinte couvre tout le texte, métadonnées comprises.
Quand l'agent change le statut d'un sujet, ou y ajoute ce qu'il attend,
pendant le travail même où il écrit une entrée qui le cite, la citation
neuve ne correspond plus : il doit relire le sujet, qui n'a pas changé
sur le fond, et récrire la citation. Une demande qui cite le sujet qui
l'attend, ce sujet nommant la demande en retour dans ses métadonnées, ne
s'écrit que dans un ordre précis ; si les deux se citent avec empreinte,
chaque réécriture de l'une périme l'autre, sans fin. L'agent de JustCook
l'a vécu avec une de ses demandes et le sujet qui l'attendait.

### La règle proposée

L'empreinte couvre le titre et le corps de l'entrée, sans sa ligne de
métadonnées ; `socle show`, la commande par laquelle l'agent lit une
entrée, donne cette empreinte. Une citation à l'empreinte du texte entier,
toutes celles écrites avant, reste valide : rien de la mémoire existante
ne casse. Ce qu'une citation prouve reste ce que dit la décision du 10
octobre, pour le corps ; le statut, lui, se lit ailleurs. Celui des
décisions et des sujets du backlog est dans leur index, une ligne par
entrée avec son titre et son statut, que l'agent reçoit à chaque
démarrage ; celui d'une demande, répondue ou non, tient dans le fichier de
votre réponse, à part, et ne change pas son texte.

### Le test qui change

`test_une_citation_neuve_d_une_version_perimee_est_refusee`, dans
`tests/test_lectures.py`, clôt un sujet en ne changeant que sa ligne de
métadonnées, puis attend qu'une citation neuve de la version d'avant la
clôture soit refusée ; avec la règle proposée, elle serait acceptée. Il
changerait ainsi : la clôture y changerait aussi le corps du sujet, et la
citation de la version d'avant resterait refusée. Un test nouveau
prouverait qu'un changement des seules métadonnées ne périme plus une
citation neuve, ni deux citations croisées.

## Éléments cités

Les numéros : B- un sujet du backlog, ADR- une décision du projet, J- une
entrée du journal, datée et suivie de son rang dans la journée ; après @,
l'empreinte de la version que j'ai lue.

- B-0135@79bfad25 — le sujet des citations que périme un changement de
  métadonnées, ouvert sur le retour de l'agent de JustCook.
- ADR-0008@c8c9e0ec — la décision du 10 octobre : une lecture se prouve
  par l'empreinte de la version lue ; ses phrases sont citées plus haut.
- J-2026-11-08-S@b8e4e7e4 — le retour de l'agent de JustCook, le 8
  novembre, et ses six gênes.

## Où regarder

- [Le test qui change](https://github.com/theodubus/memory/blob/95a3f20d7268e6d860ad8ca14e2dabab425a6f34/tests/test_lectures.py#L219),
  ligne 219 et suivantes : vérifier qu'avant la citation refusée, seule la
  ligne de métadonnées du sujet change (la préparation commune des tests
  de ce groupe, `setUp`, un peu plus haut).
- [ADR-0008](https://github.com/theodubus/memory/blob/95a3f20d7268e6d860ad8ca14e2dabab425a6f34/memory/decisions/ADR-0008-lecture-prouvee-par-empreinte.md) :
  la décision entière.
- [La pull request en cours](https://github.com/theodubus/memory/pull/26),
  où la règle serait livrée.

## Options

- **L'empreinte sans la ligne de métadonnées** (recommandée) : ce qui est
  décrit plus haut. Effort : quelques heures, tests compris. Risque : une
  citation ne prouve plus qu'un statut a été lu ; l'index le montre.
  Réversible : revenir à l'empreinte du texte entier, les citations de
  l'une ou l'autre forme restant acceptées.
- **Une commande qui récrit les citations périmées** d'une entrée dont
  seules les métadonnées ont changé, l'empreinte restant celle du texte
  entier : aucun test ne change ; mais deux entrées qui se citent avec
  empreinte se périment toujours l'une l'autre à chaque réécriture.
- **Rien** : la gêne reste.

## Conséquences

Si vous validez : j'écris la règle, ses tests et sa documentation, avec le
changement du test nommé plus haut, et je la livre dans la pull request en
cours. Si vous refusez, en disant quoi changer (l'autre option, ou rien),
je fais ce que dit votre réponse. Sans réponse, rien ne change ; selon
votre consigne, la mise à jour de JustCook attend vos réponses à ses
gênes, mais vous pouvez la lancer sans elles.

## Recommandation

Valider. Vérifié : le test cité ne change que la ligne de métadonnées du
sujet avant d'attendre le refus ; l'auto-test du socle, qui injecte une
citation périmée pour s'assurer qu'elle est refusée, change le corps de
l'entrée citée, et reste attrapé avec la règle proposée ; une citation
commitée n'est plus recontrôlée. Supposé : qu'un statut changé n'ôte rien
à ce qu'une citation doit prouver.

## Réponses possibles

- `valider` — la règle recommandée, et le changement de `test_une_citation_neuve_d_une_version_perimee_est_refusee`.
- `refuser` — l'agent fait ce que dit la réponse : l'autre option, ou rien.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
