<!-- socle: couche=demandes zone=publique -->
# D-0175 — Remettre les copies protégées des skills socle-batch, socle-resume et socle-handoff de ce dépôt sur leurs gabarits, que D-0174 a fait changer

> date : 2026-11-24

## Décision demandée

Autoriser l'installeur à remettre, dans ce dépôt, les copies protégées des skills `socle-batch`, `socle-resume` et `socle-handoff` sur leurs modèles, tels que les a changés la passation programmée que vous avez validée le 24 novembre.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code confié à un agent d'IA : il garde la mémoire du projet, vérifie le travail de l'agent et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, recevra ces changements à sa prochaine mise à jour.

**Le chantier.** Le lot en cours (« de la session longue et de la reprise »), un ensemble de tâches relues ensemble, rend automatique le passage d'une session de l'agent à la suivante : quand l'agent doit s'arrêter (la fin d'un lot, une limite d'usage proche, une longue attente), il crée lui-même la session suivante et lui programme son prompt, ou, dans l'autre mode, vous donne le prompt à copier. Le 24 novembre, vous avez validé sa spécification (« Valider D0174 »), et précisé que ce dépôt-ci reste au prompt à copier ; les projets installés, eux, programment par défaut. Le lot est fait, et relu par un agent relecteur sans contexte : une commande nouvelle, `socle handoff`, un skill nouveau, `socle-handoff`, et deux skills retouchés. Il reste cette demande, puis la livraison.

**La question.** Un skill est une procédure écrite que l'agent charge quand elle sert. Le socle en garde le modèle, le gabarit, dans `engine/socle/templates/skills/`, en français et en anglais selon la langue du projet ; l'installeur en pose une copie dans `.claude/skills/`, où Claude Code la lit, ici en français. La politique d'autonomie, un fichier que vous seul modifiez, protège ces copies : seul l'installeur les réécrit, et sur votre accord, donné par une demande qui cite l'empreinte de chaque fichier. Aujourd'hui, l'agent de ce dépôt lit encore les anciennes copies de `socle-batch` et `socle-resume`, et n'a pas `socle-handoff`.

**Ce que chaque copie reçoit.**

- `socle-handoff`, nouveau : les deux modes, le moment de la passation, ses bornes, la garde contre le travail en double (une commande qui refuse la session neuve si quelqu'un a poussé sur sa branche ou écrit la mémoire depuis), la pull request ouverte, et comment vous voyez et arrêtez une session programmée ; c'est la spécification que vous avez validée, mise en procédure.
- `socle-batch`, la procédure d'un lot. « Changer de session » se réduit au rangement (tout pousser, écrire où en est le lot), puis renvoie à `socle-handoff`. Sans vous pour compacter la conversation (la résumer par `/compact`, que vous seul lancez), l'agent change de session sans vous attendre. Et deux règles que vous avez retenues : le 19 novembre, une tâche qui change un comportement nomme, avant le lot, le test qui affirme le contraire, et sa demande se pose aussitôt, puisque changer ce qu'un test attend vous revient ; le 23 novembre (« 1 ok »), une tâche qu'une revue ouvre rejoint le prochain lot qui lui convient, sinon un lot neuf.
- `socle-resume`, la reprise après une limite d'usage : l'agent coupé par une limite se relance seul à sa levée, par un message qu'il s'est programmé. À ce réveil, la garde de la passation (`socle handoff check`) remplace la comparaison, faite à la main, de la branche avant et après sa mise à jour ; au premier tour d'une session, une passation programmée qui attend vous est signalée.

Ici, rien ne se programme : `socle-handoff` lit le mode dans le chantier actif, qui porte votre consigne du 24 novembre, le prompt à copier.

**La spécification touchée.** Sur la branche du lot, son tableau des moments (quand part la session suivante), que le skill reprend mot pour mot, est remplacé par un renvoi au skill avec son résumé : un contrôle du socle refuse un même paragraphe dans deux fichiers, pour qu'ils ne divergent pas. Rien d'autre n'y change ; [la version que vous avez validée](https://github.com/theodubus/memory/blob/f32ff5d054af0b2895722dd68cca232904b87cfb/docs/fabrication/passation-programmee-specification.md) reste lisible, et son tableau est celui de la section « Le moment » du skill.

**Comment.** Une fois la demande validée, l'installeur est relancé sur ce dépôt dans son mode, « amont », celui d'un dépôt qui fabrique le moteur (`install --target . --mode amont`) ; il réécrit les trois copies, que l'agent vérifie identiques aux empreintes ci-dessous. Il régénère aussi la section du socle dans `AGENTS.md`, les instructions que l'agent relit à chaque session : elle passerait le plafond de taille que les garde-fous de ce dépôt lui fixent, 16 309 octets pour 16 000, et l'agent la remet à son état commité, comme le 24 novembre. Seule la section de ce dépôt reste ainsi en retard, ce que votre tri du backlog du 24 novembre a accepté ; les projets installés reçoivent la section entière.

## Éléments cités

Plus bas : `D-`, une demande ou une décision ; `T-`, une tâche ; `B-`, un besoin ; `L-`, un lot ; `J-`, une entrée du journal, datée et lettrée ; après @, l'empreinte de la version lue ; `sha256:`, celle du fichier que l'installeur posera.

- .claude/skills/socle-batch/SKILL.md sha256:4c605323d4054359
- .claude/skills/socle-resume/SKILL.md sha256:37e7dae998d02606
- .claude/skills/socle-handoff/SKILL.md sha256:5c81a7e3b26ce764
- D-0174@95b3c303 — votre validation du 24 novembre de la passation programmée et de sa spécification, que ces trois skills disent.
- D-0173@163bc9a2 — votre décision du 24 novembre : ce dépôt reste au prompt à copier, le produit programme par défaut.
- D-0141@284ef820 — votre décision du 19 novembre : le test contraire nommé et sa demande posée avant le lot.
- D-0158@41eaf6ee — votre décision du 23 novembre : une tâche ouverte par une revue reçoit un lot.
- D-0168@f095a79d — votre tri du backlog du 24 novembre, qui a fermé la tâche de la section d'`AGENTS.md` en retard ici.
- D-0092@42266c33 — votre accord du 10 novembre : l'agent fusionne lui-même sa pull request.
- L-0010@527346df — le lot en cours, que cette demande permet de clore.
- T-0079@9d5ffd48 — la tâche qui a écrit le skill `socle-handoff` et réduit `socle-batch`.
- T-0081@bfec54bb — la tâche qui a écrit `socle handoff` et sa garde, et retouché `socle-resume`.
- B-0259@a694fbe7 — le besoin de la passation programmée, satisfait par le lot.
- J-2026-11-24-N@5bfad5a1 — la remise, le 24 novembre, de la copie du skill de la revue d'un lot, et la section d'`AGENTS.md` remise de même.

## Où regarder

- [Le skill `socle-handoff`](https://github.com/theodubus/memory/blob/78221b0545604a0f87c8ffa2630df326e90fe510/engine/socle/templates/skills/socle-handoff/SKILL.md) : qu'il dit la spécification que vous avez validée, les deux modes et leurs bornes.
- [Le skill `socle-batch`](https://github.com/theodubus/memory/blob/78221b0545604a0f87c8ffa2630df326e90fe510/engine/socle/templates/skills/socle-batch/SKILL.md) : sa section « Changer de session », et les deux règles de « Le lot ».
- [Le skill `socle-resume`](https://github.com/theodubus/memory/blob/78221b0545604a0f87c8ffa2630df326e90fe510/engine/socle/templates/skills/socle-resume/SKILL.md) : « Au réveil : vérifier d'abord », où la garde entre.

## Options

- **Valider** : l'installeur remet les trois copies ; l'agent de ce dépôt suit dès la session suivante la procédure que chess recevra. Effort : une commande et sa vérification, dans ce lot. Risque : faible, du texte de procédure, déjà relu. Réversible : une demande de plus remet les anciennes copies.
- **Refuser** : les copies restent les anciennes. L'agent de ce dépôt suit l'ancienne fin de session, qui donne aussi le prompt à copier, et, au réveil, compare sa branche à la main au lieu de lancer la garde : rien ne se contredit, la vérification est seulement moins complète. Il lit les gabarits à la main quand la procédure propre à ce dépôt pour mener un lot (le skill `delegate-lot`) y renvoie.

## Conséquences

Si vous validez : l'installeur remet les trois copies, que l'agent commite avec votre réponse ; puis il clôt le lot, ouvre la pull request et la fusionne une fois la CI verte, selon votre accord du 10 novembre ; cette fusion publie le moteur dans le dépôt `theodubus/socle`, d'où chess se met à jour, comme à chaque fusion. Si vous refusez : le lot se clôt sans elles, et l'écart demeure jusqu'à une demande nouvelle. Sans réponse : le lot attend sa clôture ; rien d'autre ne change.

## Recommandation

Valider : ce sont les textes de vos décisions des 19, 23 et 24 novembre, et l'agent de ce dépôt doit suivre ce que chaque projet recevra.

Vérifié : les trois empreintes sont celles des gabarits français relus par la revue du lot ; les tests des skills et l'auto-test du socle passent sur eux. Sur une copie jetable de ce dépôt, l'installeur pose les trois copies à ces empreintes, et, la section d'`AGENTS.md` remise, tous les contrôles passent, hors celui qui attend votre réponse.

Supposé : rien.

## Réponses possibles

- `valider` — l'installeur remet les trois copies protégées, commitées avec votre réponse.
- `refuser` — les copies restent les anciennes ; le lot se clôt sans elles.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
