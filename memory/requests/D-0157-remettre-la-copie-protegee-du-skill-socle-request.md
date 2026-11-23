<!-- socle: couche=demandes zone=publique -->
# D-0157 — Remettre la copie protégée du skill socle-request de ce dépôt sur son gabarit, que le lot L-0009 a changé

> date : 2026-11-22

## Décision demandée

Autoriser l'agent à remplacer la copie protégée du skill `socle-request` de ce dépôt par le texte exact de son gabarit, que le lot L-0009 a changé d'une phrase : le relecteur à froid d'une demande répond en un seul message, sans lancer d'outil.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code tenu par un agent d'IA : il garde la mémoire du projet, vérifie ce que l'agent produit, et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, est le projet pilote, qui recevra ces changements à sa prochaine mise à jour.

**Le chantier.** Le jalon en cours, un groupe de besoins qui servent un même but, corrige et stabilise le produit avant cette mise à jour de chess. Son lot L-0009, un ensemble de tâches menées puis relues ensemble, mesure ce que coûte le travail de l'agent, compté en jetons, l'unité de ce que le modèle lit et écrit. Il fait entrer dans le produit une commande qui dit ce qu'une session a coûté ; règle le temps que le démarrage d'une session sur les serveurs d'Anthropic laisse pour compléter l'historique du dépôt puis installer les outils ; corrige un scénario du banc d'essai, qui joue des sessions d'agent sur des projets jetables pour juger le socle ; et mesure la relecture à froid d'une demande. Tout est fait, et relu par un relecteur sans contexte ; reste cette copie.

**La question.** Un skill, une procédure écrite que l'agent charge quand elle sert, a deux textes : le gabarit, que le produit installe dans chaque projet, en français ou en anglais selon sa langue, et, dans ce dépôt, une copie française, celle que lit l'agent d'ici, protégée pour qu'il ne récrive pas ses propres règles : seul votre accord la change. Le lot a changé le gabarit de `socle-request`, le skill des demandes ; la copie d'ici a gardé l'ancien texte, et l'état du dépôt, le résumé que le socle calcule au démarrage de chaque session, le signale.

**La relecture à froid.** Avant de vous poser une demande, l'agent la fait lire par un sous-agent, un second agent lancé sans la conversation, qui la lit à votre place, comme si vous n'aviez pas ouvert le projet depuis trois semaines, et dit ce qu'il n'a pas compris. Le 13 novembre, sur chess, une telle relecture avait coûté 131 786 jetons, sans qu'on sache ce qu'elle avait lu. Le 22 novembre, deux relectures d'une même demande, faites sous l'ancienne phrase, ont été mesurées : un seul échange avec le modèle, aucun outil (ni lecture de fichier, ni commande), environ 80 000 jetons, dont 5 % pour la demande elle-même ; le reste est le prix fixe de tout sous-agent, ce qu'il reçoit avant de lire quoi que ce soit. Une revue de lot, la relecture d'un lot entier par un relecteur sans contexte, en coûte de 245 000 à 375 000 : la relecture d'une demande en coûte au plus le tiers. La phrase nouvelle fixe ce comportement observé, qui ne tenait jusqu'ici qu'à la consigne donnée au relecteur.

**Ce qui change**, dans l'étape 4 du skill, une seule phrase. Avant : « Il lit la demande dans le rôle de l'humain qui n'a pas ouvert le projet depuis trois semaines, sans lien ni fichier, et rend ce qu'il en a compris et ce qui lui manque pour décider. » Après : « Il lit la demande dans le rôle de l'humain qui n'a pas ouvert le projet depuis trois semaines, et rend en un seul message, sans lancer d'outil, ce qu'il en a compris et ce qui lui manque pour décider : il ne coûte alors que le prix fixe d'un sous-agent, son dossier et sa réponse. Un compte rendu qui compte un outil lancé dit une lecture qui n'était pas à froid : le récap le dit. » Le dossier est le texte que le socle prépare pour ce relecteur, une consigne puis la demande ; le compte rendu, ce que l'outil qui lance un sous-agent rend à l'agent, dont le nombre d'outils lancés ; le récap, le résumé de fin de tour que l'agent vous donne. Rien d'autre ne change dans le skill. Le gabarit anglais, que reçoivent les projets en anglais, dit la même chose ; il n'a pas de copie dans ce dépôt.

**Ce que votre réponse couvre.** La copie seule. La pull request du lot, l'agent la fusionne lui-même une fois la CI (les contrôles que GitHub lance sur elle) passée et la revue faite, comme vous l'avez permis le 10 novembre, mais jamais tant qu'une demande sur son contenu attend : celle-ci la retient. Si vous refusez, elle se fusionne sans la copie.

**Hors de cette demande.** Relancé, l'installeur, le programme qui installe ou met à jour le socle, change aussi `AGENTS.md`, le fichier d'instructions de l'agent : la part qu'y écrit le socle grossirait de 144 octets et passerait le plafond de 16 000 octets que le projet donne à ce fichier. Cela ne vient pas de ce lot : une autre tâche du même jalon, T-0135, le traite. L'agent relance l'installeur, remet `AGENTS.md` à son état du dernier commit, ce que la règle des fichiers protégés lui permet, et ne commite que la copie du skill. Chaque lot qui change un gabarit de skill finit ainsi par une demande comme celle-ci.

## Éléments cités

- .claude/skills/socle-request/SKILL.md sha256:b931dd8b4d86e166

L'empreinte de cette ligne est celle du gabarit, que la copie prendra octet pour octet : votre accord porte sur ce texte exact. Plus bas : `JA-`, un jalon ; `L-`, un lot ; `T-`, une tâche ; `B-`, un besoin, un résultat à atteindre ; `D-`, une demande, comme celle-ci ; après @, l'empreinte de la version lue.

- #81 — la pull request du lot L-0009, qui porte tous ses changements, ouverte le 22 novembre.
- JA-0005@e927ffa5 — le jalon en cours : le produit corrigé et stabilisé avant la mise à jour de chess.
- L-0009@bb5fd258 — le lot en cours, sur la consommation mesurée.
- T-0034@d210379b — sa tâche qui a mesuré la relecture à froid et changé le gabarit.
- B-0197@7ede861f — le besoin né du coût relevé sur chess le 13 novembre.
- T-0113@82563418 — la tâche qui remet la copie, la dernière du lot.
- B-0218@8f6ac9c8 — le besoin des copies protégées de ce dépôt qui suivent leurs gabarits, ouvert tant que T-0135 n'est pas faite.
- D-0149@525a9975 — votre accord du 20 novembre, qui a remis cette copie pour la dernière fois.
- D-0092@42266c33 — votre accord du 10 novembre : l'agent fusionne lui-même sa pull request.
- T-0135@2839bc62 — la tâche, hors de ce lot, qui remettra la part du socle d'`AGENTS.md`.

## Où regarder

- [La pull request du lot, #81](https://github.com/theodubus/memory/pull/81) : le diff du gabarit, en français et en anglais, et la mesure.
- [Le gabarit nouveau, étape 4](https://github.com/theodubus/memory/blob/1ba55423d6d9cb443c276aeedc52a217d95e7ff2/engine/socle/templates/skills/socle-request/SKILL.md#L47-L63) : la phrase nouvelle, lignes 54 à 59.
- [La copie actuelle, étape 4](https://github.com/theodubus/memory/blob/1ba55423d6d9cb443c276aeedc52a217d95e7ff2/.claude/skills/socle-request/SKILL.md#L47-L60) : l'ancienne, lignes 54 à 56.
- [La mesure](https://github.com/theodubus/memory/blob/1ba55423d6d9cb443c276aeedc52a217d95e7ff2/docs/fabrication/consommation.md), section « Ce que lit le relecteur à froid d'une demande » : les chiffres des deux relectures.

## Options

- Valider : la copie devient le gabarit, octet pour octet ; l'agent d'ici suit la règle que chess recevra ; effort faible ; risque faible, une phrase relue par la revue du lot et vérifiée par un test ; réversible par une demande nouvelle.
- Refuser : la copie garde l'ancien texte et le gabarit le nouveau, que chess recevra ; l'état signale l'écart à chaque démarrage jusqu'à une demande nouvelle ; effort nul ; risque faible, l'agent d'ici fait relire ses demandes comme aujourd'hui, sans la phrase ; réversible.

## Conséquences

Si vous validez : l'agent pose la copie, la commite avec votre réponse, puis fusionne la pull request une fois la CI passée. Si vous refusez : la copie ne change pas, T-0113 s'abandonne, le lot se ferme sans elle et la pull request se fusionne ; si vous voulez aussi retirer la phrase du gabarit, pour que chess ne la reçoive pas, dites-le avec votre réponse : l'agent la retire dans ce lot, et copie et gabarit redeviennent égaux. Sans réponse : la pull request reste ouverte, non fusionnée, et l'état continue de signaler l'écart.

## Recommandation

Valider. Vérifié : l'installeur, relancé dans une copie jetable du dépôt, sur l'arbre du lot, pose une copie identique octet pour octet au gabarit, d'empreinte `b931dd8b4d86e166` ; c'est la seule des copies que l'état surveille qui diffère ; la différence est la phrase citée plus haut, lue dans le diff ; un test vérifie cette phrase dans les deux langues ; les trois relectures mesurées, dont celle de cette demande, n'ont lancé aucun outil. Supposé : que la phrase tienne dans l'usage, ce que les relectures suivantes mesureront.

## Réponses possibles

- `valider` — la copie devient le gabarit, commitée avec votre réponse, puis le lot se fusionne.
- `refuser` — la copie reste telle quelle ; T-0113 s'abandonne, et l'écart reste signalé jusqu'à une demande nouvelle.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
