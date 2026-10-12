<!-- socle: couche=demandes zone=publique -->
# D-0016 — Choisir comment éprouver le socle hors de ce dépôt (R6)

> date : 2026-10-12 · lu : decisions@8e6f1b5f

## Décision demandée

Choisir comment éprouver le socle hors de ce dépôt : sur le vrai projet
d'échecs, sur une copie de ce projet, par le seul banc sans les hooks de
l'agent, ou plus tard.

## Contexte

Tout ce que le socle sait faire n'a été mesuré que dans ce dépôt, sur des
projets jetables qu'il fabrique, et par le banc, où un agent réel travaille
sur un petit projet d'essai. Le premier risque du cadrage, des refus à tort
assez fréquents pour pousser à contourner, ne se mesure que sur un vrai
projet, avec du vrai travail. Le cadrage vise aussi d'autres agents que
Claude Code : sans ses hooks, seuls les hooks git et la CI protègent, et
personne n'a mesuré ce qu'ils attrapent seuls. Les quatre premiers lots de
la passe de recul sont faits : l'installation ne perd plus rien, le hook de
l'agent ne se contourne plus par les 25 commandes du relevé, la mémoire
privée tient, et chaque contrôle a été vu échouer. Le relevé recommandait
cette mesure maintenant, avant les choix de conception du lot suivant, pour
qu'elle aide à les prioriser. Le 10 octobre, tu préférais ne pas ouvrir de
pull request sur le vrai projet d'échecs tant que l'outil était en
construction, et tu proposais un fork. Installer, pousser ou créer un dépôt
ailleurs sont des actions externes : je ne les fais pas sans ta réponse.

## Éléments cités

- **La proposition R6 du relevé de la passe de recul** : installer le socle
  sur le projet d'échecs pour de vrai, en mode adoption (les contrôles qui
  échouent déjà sur le code existant passent en avertissement), relever
  ses refus pendant une semaine, puis faire tourner le banc sans les hooks
  de l'agent.
- **Ta réponse du 10 octobre sur le vrai projet d'échecs**, citée telle
  quelle au journal : tu demandais s'il fallait vraiment ouvrir une pull
  request sur le vrai dépôt avant d'avoir terminé l'outil, et si un fork
  suffirait.
- **Le projet d'échecs** (`theodubus/chess`) : un moteur Rust, entretenu
  par un agent, dont le socle a repris les outils génériques ; son fichier
  d'instructions fait environ 110 Ko, que l'adoption passerait dans
  AGENTS.md, au-delà du plafond de taille (un avertissement en adoption).
- **Le banc d'évaluation** : quatorze scénarios propices aux erreurs, joués
  par un agent réel sur un projet d'essai, chaque session plafonnée ; il
  n'a pas encore de mode sans les hooks de l'agent, que j'ajouterais.

## Où regarder

- [le relevé, proposition R6](https://github.com/theodubus/memory/blob/a847730f73f502176cc95397138e9b0c3c416553/docs/recul.md) :
  lire R6 dans la section 1, et la ligne R6 du tableau des lots.
- [ta réponse du 10 octobre](https://github.com/theodubus/memory/blob/a847730f73f502176cc95397138e9b0c3c416553/memory/journal/2026-10.md#j-2026-10-10-q--th%C3%A9o-fixe-lordre-de-la-suite--le-jalon-8-se-pose-sans-le-vrai-chess) :
  vérifier que l'option « copie » répond à ta réserve d'alors.
- [le banc](https://github.com/theodubus/memory/blob/a847730f73f502176cc95397138e9b0c3c416553/docs/banc.md) :
  ce qu'il mesure, ses scénarios, et ce qu'une session coûte.
- [l'inventaire du projet d'échecs](https://github.com/theodubus/memory/blob/a847730f73f502176cc95397138e9b0c3c416553/docs/inventaire-chess.md) :
  ce que le socle en a repris, donc ce que l'adoption y remplacerait.

## Options

- **Le vrai projet d'échecs** : j'installe le socle en adoption sur une
  branche, j'ouvre une pull request ; tu la fusionnes si elle te convient ;
  pendant une semaine, l'agent y travaille comme d'habitude, et je relève
  chaque refus, juste ou à tort, puis je fais tourner le banc sans les
  hooks de l'agent. Effort moyen ; risque : de la friction sur ton vrai
  travail, et des instructions réorganisées ; réversible en annulant la
  fusion.
- **Une copie du projet d'échecs** : tu crées un dépôt vide (par exemple
  `theodubus/chess-socle`) et tu me l'ouvres ; j'y pousse l'historique du
  projet, j'y installe le socle en adoption, et l'agent y fait cinq tâches
  tirées du backlog du projet, une session chacune, plafonnée comme celles
  du banc ; puis le banc sans les hooks de l'agent. Effort moyen ; aucun
  risque pour le vrai projet ; réversible en supprimant la copie ; mesure
  moins réelle, puisque le travail y est choisi.
- **Le banc sans les hooks de l'agent seulement** : quatorze sessions, une
  par scénario, chacune plafonnée à deux dollars d'usage, sur les mêmes
  limites que ma session. Effort faible ; aucun risque ; ne mesure pas les
  refus à tort sur un vrai projet.
- **Plus tard** : je passe au lot suivant (les contrôles qui laissent
  passer et les refus à tort), puis les autres, et je te repose la question
  à la fin. Effort nul ici ; la mesure manque pour prioriser ce lot.

## Conséquences

- Si tu valides sans choisir : je suis la recommandation, la copie.
- Si tu refuses : R6 reste au backlog, et je passe au lot suivant.
- Si tu choisis le vrai projet : je pose la branche et la pull request sur
  `theodubus/chess`, sans rien fusionner ; la semaine commence à ta
  fusion.
- Si tu choisis la copie : j'attends le dépôt vide ; en attendant, j'ajoute
  au banc son mode sans les hooks et je passe au lot suivant.
- Si tu choisis le banc seul : je l'ajoute et je le fais tourner, puis le
  lot suivant.
- Si tu choisis plus tard, ou sans réponse : je passe au lot suivant, et R6
  reste au backlog.

## Recommandation

La copie, puis le banc sans les hooks de l'agent : elle mesure
l'installation sur un vrai code (sa taille, ses 110 Ko d'instructions, sa
CI) et la friction sur du vrai travail, sans toucher au projet que tu fais
avancer, comme tu le préférais le 10 octobre ; le vrai projet viendra
après les derniers lots. Vérifié : le dépôt `theodubus/chess` existe et
m'est ouvert en écriture ; l'installation a réussi sur une copie jetable
du projet au jalon 8, avant que L1 ne déplace un fichier d'instructions
existant dans AGENTS.md ; le banc n'a pas de mode sans hooks aujourd'hui. Supposé : que cinq tâches suffisent à voir les refus à tort
fréquents, et qu'une copie s'en rapproche assez du vrai travail.

## Réponses possibles

- `vrai-chess` — j'ouvre la pull request sur le vrai projet d'échecs, puis la semaine de relevé et le banc sans hooks.
- `copie` — tu crées le dépôt vide ; j'y fais l'adoption et cinq tâches, puis le banc sans hooks.
- `banc-seul` — seulement le banc sans les hooks de l'agent.
- `plus-tard` — le lot suivant d'abord ; R6 reste au backlog.
- `valider` — la recommandation : la copie.
- `refuser` — R6 reste au backlog, et je passe au lot suivant.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
