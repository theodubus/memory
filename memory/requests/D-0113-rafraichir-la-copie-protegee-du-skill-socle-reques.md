<!-- socle: couche=demandes zone=publique -->
# D-0113 — Rafraîchir la copie protégée du skill socle-request depuis son gabarit : la réponse poussée avec son changement, dans le même push

> date : 2026-11-14

## Décision demandée

Autoriser l'agent à remplacer la copie du skill `socle-request` que ce dépôt utilise, un fichier protégé, par le texte de son gabarit, que le moteur installe désormais dans tout projet : un seul paragraphe s'ajoute.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui rend fiables la mémoire, la documentation et les tests d'un projet de code entretenu par un agent d'IA. Le moteur est ce qu'un projet reçoit à l'installation ; ce dépôt s'en sert lui-même, comme premier projet équipé.

**Le chantier.** Avant de revenir aux nouvelles fonctions, l'agent finit une liste de sujets du backlog (la liste des sujets à traiter, chacun nommé B-NNNN) que vous avez fixée le 13 novembre. Il les livre par lots : quelques sujets, livrés ensemble par une pull request qu'il fusionne dans la branche principale. Plus tôt aujourd'hui, un défaut a été traité : quand vous validez une demande qui autorise un changement (une valeur attendue d'un test, un réglage des garde-fous, un fichier protégé), votre réponse, poussée seule avant ce changement, cessait de le couvrir, et le push du changement était refusé. Ce refus reste voulu (une validation ne couvre que le push qui la porte, pour ne pas couvrir sans fin des changements futurs) ; le moteur avertit désormais avant le push qui en souffrirait. Le premier lot, fusionné ce matin, a ensuite mis d'accord sur l'ordre juste les textes qui le disent : le gabarit de ce skill, le message de l'avertissement, la procédure des lots.

**La question.** Un skill est une procédure écrite que l'agent charge quand il en a besoin ; `socle-request` est celle qui pose une demande comme celle-ci et consigne votre réponse. Le socle pose ses skills dans chaque projet sous forme de copies protégées, que l'agent ne modifie pas sans votre accord. Le gabarit a reçu le paragraphe qui dit cet ordre ; la copie de ce dépôt ne l'a pas encore. C'est le dernier critère du sujet B-0216.

Le paragraphe ajouté, en entier, à la fin de la section « Relayer une réponse » :

> La réponse se consigne dès qu'elle est donnée, dans l'arbre : l'état la lit répondue avant son commit, et l'humain ne la voit plus en attente. Elle se commite et se pousse avec le changement qu'elle autorise (une valeur attendue, une clé des garde-fous, un fichier protégé), dans le même push, jamais avant : la CI d'un push ne compte que les validations de sa plage, et le push du changement, seul après elle, serait refusé. Seul un fichier protégé peut la précéder, poussé sous la demande en attente là où la CI du socle est exigée : la réponse part ensuite seule, sans dommage. `demandes.reponse-seule` avertit avant qu'elle parte seule.

Les termes : « l'arbre », les fichiers du dépôt dans le conteneur de l'agent, pas encore commités ; « l'état », le résumé que la commande `socle state` calcule à chaque démarrage, où figurent les demandes qui vous attendent ; « la plage », les commits qu'un push envoie ; « les validations », vos réponses `valider` ; « les garde-fous », les contrôles et les refus automatiques qui arrêtent une faute de l'agent, et le fichier de leurs réglages ; « la CI », l'intégration continue sur GitHub, qui rejoue tous ces contrôles à chaque push ; elle est « exigée » quand la branche principale refuse une fusion sans elle, ce qui est le cas dans ce dépôt ; `demandes.reponse-seule`, l'avertissement ajouté aujourd'hui. « Poussé sous la demande en attente » : l'exception du fichier protégé vient de votre accord du 2 novembre, où un fichier protégé peut être poussé dès que la demande qui le cite l'est, la CI restant rouge jusqu'à votre réponse. Rien d'autre ne change dans le fichier.

## Éléments cités

- .claude/skills/socle-request/SKILL.md sha256:c516b1114e9492e2
Les identifiants : B-NNNN, un sujet du backlog ; D-NNNN, une demande comme celle-ci ; ADR-NNNN, une décision de conception que l'agent écrit seul quand elle est réversible ; le suffixe après @, l'empreinte de la version lue.

- B-0216@ae4f7f09 — le sujet : les textes de cette règle, faits au premier lot, et cette copie en retard, son dernier critère.
- B-0142@e05ad571 — le sujet fait plus tôt aujourd'hui, avant le premier lot : la réponse poussée seule ne couvre plus le changement qu'elle autorise.
- ADR-0076@0df38de1 — la décision de l'agent qui spécifie l'avertissement `demandes.reponse-seule`.
- D-0071@9b06b40c — votre accord du 2 novembre : un fichier protégé poussé sous la demande en attente qui le cite.
- D-0103@271de17d — votre accord du 11 novembre, qui a mis cette copie à son texte actuel, `sha256:8ad7d5f7450f2e67`.

L'empreinte de la première ligne, les seize premiers caractères de l'empreinte SHA-256 du fichier, est celle que la copie aura après remplacement, identique à celle du gabarit : votre accord porte sur ce texte exact. Le contrôle des fichiers protégés refuse une copie dont l'empreinte diffère de celle que cite votre validation.

## Où regarder

- [Le gabarit, le texte nouveau](https://github.com/theodubus/memory/blob/472178aebfc5f09d5e63d77052e1444c15a12cee/engine/socle/templates/skills/socle-request/SKILL.md) : le paragraphe cité plus haut, juste avant « Un test dont la valeur attendue change ».
- [La copie actuelle, à remplacer](https://github.com/theodubus/memory/blob/472178aebfc5f09d5e63d77052e1444c15a12cee/.claude/skills/socle-request/SKILL.md) : sans ce paragraphe, identique au gabarit pour le reste.

## Options

- Rafraîchir la copie : le gabarit recopié octet pour octet par l'installeur (la commande du moteur qui pose ou met à jour ses fichiers dans un projet) ; effort nul, risque faible, réversible par une nouvelle demande qui reprend le texte d'avant.
- La laisser en retard : aucun effort ; une session qui consigne une réponse dans ce dépôt ne lit pas l'ordre juste dans son skill, et ne l'apprend que par l'avertissement, au moment de pousser.

## Conséquences

Si vous validez : l'agent recopie le gabarit dans la copie, et pousse votre réponse avec ce changement, dans le même push ; B-0216 se clôt. Si vous refusez : la copie garde son texte ; le gabarit reste celui que le moteur installe dans les autres projets, et l'agent ouvre un sujet pour remettre les deux d'accord, dont le sens (le gabarit ramené à l'ancien texte, ou une nouvelle demande pour la copie) dépendra de la raison de votre refus, que vous pouvez dire dans la conversation. Sans réponse : rien ne change, et l'agent continue les autres sujets du lot.

Valider ne vaut que pour la recopie. La règle elle-même est déjà dans le gabarit, que le moteur installe depuis ce matin ; la contester se fait par un message dans la conversation, qui deviendra une décision nouvelle, et non par un refus de cette demande.

## Recommandation

Valider. Vérifié : la copie et le gabarit ne diffèrent que par ce paragraphe (comparaison des deux fichiers) ; l'empreinte citée est celle du gabarit ; la copie actuelle est celle que vous avez approuvée le 11 novembre ; la CI du premier lot, qui rejoue tous les contrôles, est passée avant sa fusion. Supposé : qu'une session se tromperait d'ordre sans ce paragraphe ; l'avertissement du moteur la rattraperait de toute façon avant le push.

## Réponses possibles

Répondez dans la conversation par l'un de ces mots ; l'agent consigne votre texte exact.


- `valider` — l'agent remplace la copie par le gabarit, et pousse votre réponse avec ce changement.
- `refuser` — la copie garde son texte actuel ; l'agent ouvre un sujet pour remettre la copie et le gabarit d'accord.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
