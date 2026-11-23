<!-- socle: couche=demandes zone=publique -->
# D-0164 — Remettre la copie protégée du skill socle-resume de ce dépôt sur son gabarit, que L-0010 et L-0023 ont changé

> date : 2026-11-23

## Décision demandée

Remettre la copie du skill `socle-resume` que ce dépôt utilise sur la version que le produit installe désormais : vous ne validez que cet alignement, la copie devenant identique à la version de référence, qui porte quatre changements de la reprise faits depuis le 20 novembre.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code tenu par un agent d'IA, Claude Code : il garde la mémoire du projet, vérifie ce que l'agent produit, et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Ce dépôt s'en sert lui-même, comme un projet installé ; chess, votre jeu d'échecs, recevra ces changements à sa prochaine mise à jour, faite d'un coup quand le jalon en cours sera fini.

**Le chantier.** Le jalon en cours corrige et stabilise le produit avant cette mise à jour. Le travail se fait par lots, des groupes de tâches relues ensemble (L-0023, celui-ci ; L-0010, le précédent). Ce lot traite la reprise après une limite d'usage : quand votre compte atteint sa limite, le service refuse les tours de l'agent (un tour : ce qu'il fait entre un message reçu et sa réponse), sa session s'arrête, et deux « réveils », des messages qu'il se programme, la font repartir à la levée. La procédure vit dans le skill `socle-resume`, une procédure écrite que l'agent charge quand elle sert. Le produit en garde la version de référence, le gabarit, que l'installeur copie dans chaque projet ; la copie est protégée : seul l'installeur la change, et seulement sous une décision de votre part. Le 20 novembre, vous avez fait remettre de même les copies de trois autres skills (la conduite d'un lot, sa relecture, les demandes).

**La question.** Depuis, le gabarit de `socle-resume` a changé quatre fois, et la copie de ce dépôt est en retard : l'agent de ce dépôt suit encore l'ancienne procédure. La remettre exige votre accord. Les changements 1 à 3 sont un travail de l'agent, relu, qui part de toute façon chez chess ; le 4 est votre décision de ce soir.

**Ce qui change dans la copie**, du plus ancien au plus récent :

1. Le 23 novembre, lot précédent : certaines sessions n'ont pas l'outil qui lit l'historique de la session sur les serveurs (celles de chess, par exemple). Au réveil, l'agent lit alors la transcription que Claude Code garde sur le disque pour savoir si la session a été coupée par une limite, et à quelle heure.
2. Ce soir : cette lecture précisée. La coupure est le premier refus du service qui suit le dernier travail de l'agent. Un message que vous avez tapé s'y reconnaît à un champ de la transcription relevé sur une transcription réelle, et retient l'agent de reprendre (il y répond d'abord), même si c'est ce message qui s'est heurté à la limite. Une transcription qui a perdu le tour coupé (un conteneur remplacé) n'est pas lue : l'agent juge sur sa conversation.
3. Ce soir : au premier tour d'une session, l'agent vous signale les réveils de reprise qu'une session close (archivée, dans l'application) a laissés, et ne les désactive que si vous le demandez. Vu une fois, le 19 novembre, quand deux sessions se sont suivies sur le même lot.
4. Ce soir, votre réponse `valider` à D-0163 : quand l'agent finit un tour en attendant un événement dont il connaît l'heure (un rappel qu'il s'est programmé, une commande en arrière-plan, la CI), il garde ses réveils au lieu de les retirer, pour que la session reparte si la limite a refusé cet événement ; et au réveil d'un travail que vous avez interrompu, il le dit en une ligne, sans le finir ni reprogrammer ses réveils.

Pour tenir sous la taille maximale d'un skill, 8 000 octets, le texte a été resserré. Deux relecteurs sans contexte l'ont vérifié, le second après les corrections du premier ; les corrections du second n'ont pas été relues à leur tour, mais les tests du skill les lisent.

**Ce que devient `AGENTS.md`.** L'installeur réécrit aussi la section du socle d'`AGENTS.md`, le fichier d'instructions de l'agent, sur un gabarit qu'un lot du 20 novembre a changé (la fusion d'une pull request par l'agent), et le fichier dépasserait son budget de taille. Ce n'est pas l'objet de cette demande : j'annule cette réécriture aussitôt, et le fichier reste tel qu'aujourd'hui ; la tâche T-0135 la traitera, avec la place qu'il lui faut.

**Si vous refusez**, la copie attend la remise suivante, T-0165, à la fin du lot précédent, en pause jusqu'à un essai de cette nuit (une session qui en programme une autre) puis encore plusieurs tâches : des jours, pendant lesquels l'agent de ce dépôt suit l'ancienne procédure.

## Éléments cités

Plus bas : `L-`, un lot ; `T-`, une tâche ; `B-`, un besoin ; `D-`, une demande ; `ADR-`, une décision écrite ; après @, l'empreinte de la version lue ; `sha256:`, l'empreinte du fichier que l'installeur posera.

- .claude/skills/socle-resume/SKILL.md sha256:7f128d4f25b7eb7a
- L-0010@f701f5fe — le lot précédent, sur la passation entre sessions et la reprise, en pause jusqu'à l'essai de cette nuit.
- L-0023@6e0056e2 — ce lot, la seconde moitié de la reprise, mené avant la fin du précédent.
- T-0114@0d266e2e — la tâche de ce lot qui remet la copie protégée du skill `socle-resume` sur son gabarit.
- B-0218@8f6ac9c8 — le besoin : que ce dépôt tourne sur ce que le produit installe, ses copies protégées suivant leurs gabarits.
- T-0040@3d745419 — la tâche du lot précédent qui fait lire la transcription locale au réveil (le changement 1).
- T-0164@8a5b24f9 — la tâche de ce lot qui précise cette lecture (le changement 2).
- T-0127@f1c68f69 — la tâche de ce lot qui fait signaler les réveils d'une session archivée (le changement 3).
- T-0082@40f4884b — la tâche de ce lot qui écrit la règle que vous avez validée ce soir (le changement 4).
- D-0163@01b2736f — votre demande de ce soir sur les deux cas de la reprise, validée.
- ADR-0107@b9f3e852 — la décision écrite qui complète la règle de la reprise, sur votre réponse à D-0163.
- D-0149@525a9975 — votre décision du 20 novembre, qui a remis les copies de trois autres skills sur leurs gabarits.
- T-0165@0a09d3f6 — la tâche qui remettra de nouveau cette copie, avec celle du skill de la conduite d'un lot, à la fin du lot précédent.
- T-0135@2839bc62 — la tâche qui traitera la section du socle d'`AGENTS.md`, hors de cette demande.

## Où regarder

- [Le gabarit du skill](https://github.com/theodubus/memory/blob/c5c13f69d3664d21e3abbc6418804c1a2b7a4d2c/engine/socle/templates/skills/socle-resume/SKILL.md) : la version que la copie prendra, à l'identique ; ses sections « À la fin de chaque tour » et « Au réveil : vérifier d'abord » portent le changement 4.
- [La copie actuelle](https://github.com/theodubus/memory/blob/c5c13f69d3664d21e3abbc6418804c1a2b7a4d2c/.claude/skills/socle-resume/SKILL.md) : celle que l'agent de ce dépôt suit aujourd'hui ; les quatre changements plus haut font tout l'écart.

## Options

- **Valider** : l'installeur, relancé dans le mode de ce dépôt (le mode « amont », celui du dépôt qui fabrique le moteur), pose la copie, identique au gabarit ; je défais sa réécriture d'`AGENTS.md` ; la copie se commite avec votre réponse, sur la branche de ce lot, dans sa pull request. Effort : une commande et un commit. Risque : nul hors du skill. Réversibilité : une demande nouvelle remettrait l'ancienne copie.
- **Refuser** : la copie reste en retard. Effort : aucun. Risque : l'agent de ce dépôt suit l'ancienne procédure pendant des jours, sans les deux cas que vous venez de valider, et l'état du projet, que l'agent calcule à chaque démarrage, le signale. Réversibilité : la demande peut se reposer.

## Conséquences

Si vous validez : la copie est remise dans ce lot, l'état ne la signale plus, et le lot peut se clore. Si vous refusez : la tâche T-0114 s'abandonne en citant votre réponse, et la copie attend T-0165. Sans réponse : le lot ne se clôt pas, et sa pull request, dont le lien vous est donné dans la conversation, attend.

## Recommandation

Valider. Vérifié : l'installeur, relancé dans un clone jetable de ce dépôt, pose une copie identique au gabarit, à l'empreinte citée ; il ne change par ailleurs que la section d'`AGENTS.md`, que je défais ; les tests du skill passent en français et en anglais, ses deux versions. Supposé : rien.

## Réponses possibles

- `valider` — l'installeur pose la copie, commitée avec votre réponse.
- `refuser` — la copie reste en retard jusqu'à T-0165 ; T-0114 s'abandonne.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
