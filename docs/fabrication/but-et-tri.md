# Le but du socle et le tri des sujets

Validé par Théo le 24 novembre 2026, en séance (D-0167) : la
description et les critères ci-dessous, mot pour mot, et ce qui en
découle. Ils remplacent la formulation de D-0166.

## Le projet

Le socle permet de confier un projet de code à un agent d'IA sur la
durée, comme à un développeur qui ne perd jamais le fil. Il se souvient
de ce qui a été décidé et fait, sait où en est le projet et ce qui vient
ensuite, vérifie son propre travail, et ne vient chercher l'humain que
pour les vraies décisions. L'humain garde la direction sans avoir à
surveiller chaque pas.

## Ce qui entre

Un sujet (un besoin, une tâche, un constat de revue, une suggestion)
entre s'il passe les trois tests suivants.

**1. À quoi il sert : au moins un de ces cinq points, de façon
vérifiable.**

- **Mémoire** : il empêche qu'une décision, un fait, une entrée du
  journal ou du backlog, ou une réponse de l'humain se perde, se
  corrompe ou devienne introuvable. On peut décrire la session où, sans
  lui, l'agent perdrait ou fausserait cette information.
- **Contexte** : il change ce que l'agent voit à un moment précis (l'état
  au démarrage, un skill, un message de refus, le récap), pour qu'il
  agisse juste ; ou il réduit de façon mesurée ce que l'agent relit.
- **Vérification** : il ajoute ou répare un contrôle automatique qui
  attrape une erreur qu'un agent fait réellement ; ou il empêche une
  action irréversible (push sur `main`, push forcé, suppression du
  projet, perte de travail non commité).
- **Décision humaine** : il réduit ce que l'humain doit lire ou faire, ou
  rend une décision plus claire.
- **Marche pour de vrai** : il corrige un bug qui casse ou fausse
  l'installation, la mise à jour, la CI, le démarrage ou les tests d'un
  projet réel ; ou il sert un langage qu'un projet utilise.

**2. La preuve : au moins une de ces trois.**

- Vu en usage réel : une session, une CI, un commit, une entrée du
  journal qui le relève, un message de l'humain ou d'un pilote.
- Demandé par l'humain.
- Son effet serait irréversible (perte de données, push sur `main`,
  suppression), même s'il n'a jamais été vu.

**3. Le coût en proportion.** Un cas rare et bénin ne vaut au plus
qu'une ligne de documentation (D-0165). Un bug qui casse ou fausse le
travail d'un projet réel passe en priorité, quel que soit l'effort.

## Ce qui n'entre pas

Un sujet sort dès qu'une de ces exclusions s'applique.

- **X1.** Il ne compte que si l'agent cherche à contourner le socle :
  forme de commande inhabituelle, seuil abaissé pour passer un contrôle,
  fichier protégé modifié par une astuce.
- **X2.** Il a été imaginé par un relecteur ou un agent, jamais vu en
  usage réel, et son effet est soit rattrapé par autre chose (la CI, le
  hook avant commit, une erreur que l'agent voit aussitôt), soit une
  gêne légère.
- **X3.** Il peaufine la machinerie elle-même (forme ou libellé d'une
  sortie, règle sur la façon de former un lot, une passe ou une demande)
  sans qu'une gêne réelle ait été constatée : une plainte de l'humain, un
  agent bloqué, du temps perdu mesuré.
- **X4.** Il ne concerne que ce dépôt-atelier et ne change rien à ce
  qu'un projet reçoit, sauf s'il bloque le travail ici.
- **X5.** Il généralise à un langage, une plateforme ou un outil dont
  aucun projet ne se sert.
- **X6.** C'est de la mesure pour elle-même : une statistique plus fine
  dont aucune décision ne dépend.

## Ce qui en découle

- En cas de doute, le sujet n'entre pas. Un sujet écarté ou abandonné
  revient s'il est vu en usage réel.
- Les bloquants d'une revue (un critère contredit, une régression, une
  perte de données) se corrigent dans le lot ; ses autres constats
  passent ces tests comme le reste.
- Avant d'abandonner des entrées du backlog, l'agent en donne le récap à
  l'humain : chacune, avec la raison de son abandon.
