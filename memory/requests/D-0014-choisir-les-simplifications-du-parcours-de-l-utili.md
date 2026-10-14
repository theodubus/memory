<!-- socle: couche=demandes zone=publique -->
# D-0014 — Choisir les simplifications du parcours de l'utilisateur à faire

> date : 2026-10-11 · lu : decisions@e56960e0

## Décision demandée

Choisir, parmi dix propositions qui simplifient ce que l'humain fait avec le
socle, celles que je fais maintenant.

## Contexte

Tu m'as demandé de travailler le parcours de l'utilisateur avant d'écrire la
documentation, et accepté que je le mesure d'abord, puis que je te soumette
le relevé avant de rien changer. Je l'ai joué sur un projet Python neuf avec
un document de cadrage, puis une mise à jour du socle, l'ajout d'une mémoire
privée et un commit fait à la main. Ce qui pèse le plus : l'installation
finit en échec dès que le projet a du code, parce que le cliquet de mutation
réclame un plafond que rien n'explique comment mesurer ; une mise à jour
fait recopier à l'humain chaque fichier du moteur changé dans la commande
d'approbation ; l'option de mémoire privée, sur un projet déjà installé,
annonce la mémoire privée sans l'activer, ce qui est un défaut ; le mode
compagnon demande six gestes, dont trois sur GitHub, sans guide ; vingt
commandes s'affichent dans l'aide, dont cinq seulement sont pour toi ; et
aucun texte n'est écrit pour l'humain, seulement pour l'agent.

## Éléments cités

- **Le relevé du parcours** : douze étapes, chacune avec ce que l'humain
  tape, lit et doit décider, puis les dix propositions détaillées.
- **Le sujet du parcours** : le sujet de backlog que tu as ouvert pour rendre
  le socle simple à mettre en place et à utiliser, avant sa documentation.
- **Les dix propositions**, en bref :
  - P1, une installation qui finit verte : les modules qui ont du code entrent
    au cliquet de mutation « à mesurer », jusqu'au premier balayage ;
  - P2, un « et maintenant » de trois à cinq lignes à la fin de chaque
    commande de l'humain, et un audit qui ne montre que ce qui échoue ;
  - P3, approuver d'un geste les fichiers protégés que l'humain vient de
    changer, et la commande exacte imprimée par l'installeur ;
  - P4, corriger l'option de mémoire privée sur un projet installé ;
  - P5, mettre en place le mode compagnon pas à pas, clé de déploiement
    comprise ;
  - P6, une page d'aide pour l'humain, et les commandes rangées en trois
    groupes : humain, agent, interne ;
  - P7, rappeler dans l'état ce que l'humain a fait lui-même (une
    approbation, une réponse), pour que l'agent le cite ;
  - P8, le README à jour et un guide court de l'humain, base de la
    documentation ;
  - P9, prévenir au commit qu'une fonction publique sans test sera refusée
    par la CI sans dispense ;
  - P10, s'installer sans cloner le dépôt, par un paquet pip : c'est une
    publication externe.

## Où regarder

- [le relevé et les propositions](https://github.com/theodubus/memory/blob/b2dbc24c96bb43f8641f26673598301e3ffab352/docs/parcours.md) : vérifier que les
  douze étapes décrivent bien ce que tu as vécu (la migration en est une),
  et lire le tableau des propositions, avec l'effort de chacune.
- [le sujet du parcours](https://github.com/theodubus/memory/blob/b2dbc24c96bb43f8641f26673598301e3ffab352/memory/backlog.md#b-0034--le-parcours-de-lutilisateur-de-linstallation-%C3%A0-lusage-courant-rendu-simple) :
  vérifier que le relevé répond à ce que tu demandais.

## Options

- **La recommandation** (P1 à P4, P6 à P9 maintenant, P5 ensuite) : effort
  moyen, quelques jours de travail ; risque faible, chaque changement éprouvé
  sur une installation neuve et par l'auto-test ; réversible proposition par
  proposition.
- **Tout de P1 à P9** maintenant : le même effort, plus le mode compagnon
  guidé ; même risque ; réversible.
- **Ton propre choix**, par numéros : effort et risque à la mesure.
- **Rien** : effort nul ; le parcours reste tel que relevé, et la
  documentation décrira ses détours ; réversible à tout moment.
- P10 se décide à part dans tous les cas : publier un paquet est une action
  externe, qui demande sa propre demande.

## Conséquences

- Si tu valides la recommandation : je fais P1 à P4 et P6 à P9, chacune
  éprouvée sur une installation neuve, puis P5, puis la documentation.
- Si tu choisis toi-même : je fais les numéros que ton texte donne, dans
  l'ordre du tableau.
- Si tu refuses : je passe à la documentation, qui décrira le parcours tel
  qu'il est.
- Sans réponse : rien ne change ; je corrige seulement le défaut de l'option
  de mémoire privée, qui est un bogue, et je le note au backlog.

## Recommandation

La recommandation ci-dessus. Vérifié : chaque constat du relevé a été
rejoué ici, sur une installation neuve. Supposé : que ces étapes sont celles
qui te coûtent le plus ; tu n'en as vécu que certaines (la migration,
l'approbation).

## Réponses possibles

- `valider` — je fais la recommandation : P1 à P4 et P6 à P9, puis P5.
- `tout` — je fais P1 à P9.
- `choisir` — je fais les numéros que ta réponse donne.
- `refuser` — je passe à la documentation, sans rien simplifier.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
