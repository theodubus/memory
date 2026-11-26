<!-- socle: couche=demandes zone=publique -->
# D-0220 — Relever le plafond de memory/directives.md de 16 000 à 24 000 octets, dans ce dépôt et dans le gabarit des garde-fous du produit, avec la valeur attendue de son test

> date : 2026-11-26

## Décision demandée

Relever le plafond de taille de `memory/directives.md`, le fichier des consignes durables, de 16 000 à 24 000 octets, dans ce dépôt et dans le gabarit des garde-fous que le socle pose dans chaque projet, et changer en conséquence la valeur attendue du test de l'installeur qui le lit.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outillage pour les agents de code : une mémoire de projet versionnée, des contrôles et des hooks, que des projets comme chess installent, et dont ce dépôt se sert lui-même.

**Le chantier.** Le jalon en cours corrige ce que la mise à jour de chess du 26 novembre a montré. Le 26 novembre, sur la revue de cap 9, tu as tranché comment donner de la place aux textes du socle arrivés à leur plafond : relever celui des consignes par une demande qui en donne la valeur, et garder ceux des skills et d'`AGENTS.md` en sortant leurs justifications vers le guide. Ceci est la demande ; la seconde moitié est une tâche à part.

**La question.** `memory/directives.md` fait 15 555 octets pour un plafond de 16 000 : la consigne suivante que tu donnes ferait refuser le fichier par le contrôle des budgets. Relever un plafond assouplit un garde-fou, et la politique d'autonomie exige ta validation.

Une consigne, règle durable que tu donnes à l'agent, garde ton texte exact et ne se lève que sur ta parole : le fichier ne fait que croître. Les 25 consignes en vigueur font en moyenne 613 octets, la plus longue 1 575. Le besoin demande que trois consignes de plus tiennent : 17 400 octets environ. Leur rythme : 25 depuis le 11 octobre, environ quatre par semaine, mais 14 depuis le 13 novembre, sept par semaine. À 20 000, il en tient environ sept de plus, une à deux semaines ; à 24 000, environ treize, deux à quatre semaines.

Le démarrage de chaque session n'est pas touché : il ne charge les consignes que par leur ligne de résumé, sous sa propre part, et une ligne `!! coupé` dit où lire le reste. Seul grandit le fichier, lu consigne par consigne (`socle show C-NNNN`).

Ce qui change, en quatre lignes : la clé du plafond dans `.socle/guardrails.toml` et dans les deux gabarits, français et anglais, et la valeur attendue du test de l'installeur. S'y ajoutent la spécification des consignes et la note de version : un projet installé garde sa valeur, et la reprendre assouplit son garde-fou, donc se demande à son humain.

## Éléments cités

- D-0218@0ef5bdbe — ta décision du 26 novembre : relever le plafond des consignes par une demande, sortir des skills et d'`AGENTS.md` leurs justifications vers le guide.
- B-0354@9dc74c0a — le besoin : les textes à leur plafond ont la place des règles suivantes, dont trois consignes de plus.
- T-0205@e034aa8f — la tâche qui fera le changement une fois cette demande répondue.

## Où regarder

- [`.socle/guardrails.toml`, ligne 20](https://github.com/theodubus/memory/blob/08d1e0caa275fb9d5a5eeeba34ec367c16d2593d/.socle/guardrails.toml#L20) : le plafond de ce dépôt, `16000`.
- [`engine/socle/templates/guardrails.toml`, ligne 21](https://github.com/theodubus/memory/blob/08d1e0caa275fb9d5a5eeeba34ec367c16d2593d/engine/socle/templates/guardrails.toml#L21) : celui que reçoit un projet à son installation.
- [`tests/test_consignes.py`, ligne 435](https://github.com/theodubus/memory/blob/08d1e0caa275fb9d5a5eeeba34ec367c16d2593d/tests/test_consignes.py#L435) : la valeur attendue qui changerait de `16000` à `24000`.
- [`memory/directives.md`](https://github.com/theodubus/memory/blob/08d1e0caa275fb9d5a5eeeba34ec367c16d2593d/memory/directives.md) : les 25 consignes et leurs dates.

## Options

- **24 000 octets** (recommandée) : environ treize consignes de marge, deux à quatre semaines. Effort : quatre lignes, une note de version. Risque : faible, le démarrage reste borné à part. Réversible : baisser durcit, et l'agent le fait sans demande.
- **20 000 octets** : environ sept consignes de marge ; au rythme des deux dernières semaines, la même demande reviendrait dans une à deux semaines. Même effort, même réversibilité.
- **32 000 octets** : environ vingt-six consignes de marge. Même effort ; le contrôle cesse longtemps de signaler un fichier qui grossit, son rôle.

## Conséquences

- **Si tu valides** : l'agent fait le changement dans la même pull request, avec la note de version, et la tâche se clôt ; tes trois prochaines consignes et plus s'écrivent sans refus.
- **Si tu refuses** : le plafond reste à 16 000 ; à la prochaine consigne, l'agent devra resserrer le texte d'autres consignes (leurs lignes d'attribution), sans toucher à tes mots, ou te demander d'en lever une.
- **Sans réponse** : rien ne change ; l'agent continue sur la seconde moitié du besoin. Une consigne nouvelle avant ta réponse ferait refuser le fichier.

## Recommandation

24 000 octets. Vérifié : 15 555 octets aujourd'hui pour 25 consignes, 613 en moyenne, et leurs dates, mesurés sur le fichier ; seuls la ligne de test, les deux gabarits, la spécification et des notes de version passées, inchangées, portent la valeur. Supposé : le rythme des deux dernières semaines ne dure pas ; le troisième retour de chess, que l'on triera plus tard, note d'ailleurs que des paroles rangées en consignes étaient des décisions ou des attentes, ce qui en ralentirait le flux.

## Réponses possibles

- `valider` — 24 000 octets ici et dans les deux gabarits, la valeur attendue du test changée, la note de version écrite.
- `refuser` — le plafond reste à 16 000 ; la place se trouvera en resserrant les consignes existantes.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
