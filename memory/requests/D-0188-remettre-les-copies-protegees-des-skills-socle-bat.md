<!-- socle: couche=demandes zone=publique -->
# D-0188 — Remettre les copies protégées des skills socle-batch, socle-handoff et socle-request de ce dépôt sur leurs gabarits, que L-0036 a changés

> date : 2026-11-25

## Décision demandée

Autoriser l'installeur à remettre, dans ce dépôt, les copies protégées des skills `socle-batch`, `socle-handoff` et `socle-request` sur leurs modèles, tels que les a changés le lot des corrections que vous avez retenues le 24 novembre.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code confié à un agent d'IA : il garde la mémoire du projet, vérifie le travail de l'agent et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, recevra ces changements à sa prochaine mise à jour.

**Le chantier.** Le jalon en cours rassemble tout ce qui corrige et stabilise le produit avant que chess soit mis à jour d'un coup. Son lot en cours, un ensemble de tâches relues ensemble, réunit les corrections restantes que la revue de cap du 24 novembre a relevées et que vous avez retenues ce jour-là ; la revue de cap est le regard d'un agent neuf, tous les trois lots, sur la direction du travail. Ses cinq tâches sont faites, et relues par un agent relecteur sans contexte, dont le seul constat bloquant est corrigé. Il reste cette demande, puis la livraison.

**La question.** Un skill est une procédure écrite que l'agent charge quand elle sert. Le socle en garde le modèle, le gabarit, dans `engine/socle/templates/skills/`, en français et en anglais selon la langue du projet ; l'installeur en pose une copie dans `.claude/skills/`, où Claude Code la lit, ici en français. La politique d'autonomie, un fichier que vous seul modifiez, protège ces copies : seul l'installeur les réécrit, et sur votre accord, donné par une demande qui cite l'empreinte de chaque fichier. Trois gabarits ont changé dans ce lot ; l'agent de ce dépôt lit encore les anciennes copies, et l'état, le résumé que le socle calcule et montre à l'agent à chaque démarrage, le signale. Votre réponse ne touche que ces copies-ci : chess reçoit les gabarits changés avec la publication du moteur, que vous validiez ou non.

**Ce que chaque copie reçoit.**

- `socle-batch`, la procédure d'un lot. À la livraison, l'agent attend la CI du commit qu'il a poussé, désigné par son identifiant (`gh run list --commit <sha>`), et non plus la ligne « CI » de l'état : cette ligne suit le dernier commit local, si bien qu'un commit fait pendant l'attente la déplaçait, et l'agent attendait la CI d'un commit qui n'était pas parti. Vous avez retenu cette correction le 24 novembre (suggestion 2 de la revue de cap). Pour tenir le gabarit sous son plafond de 8 000 octets, trois paragraphes sont remis en forme, leurs retours à la ligne déplacés, sans qu'un mot y change.
- `socle-handoff`, la passation d'une session à la suivante. Ses deux commandes `socle handoff prompt`, qui écrivent le prompt de la session neuve, l'une pour une session que l'agent programme, l'autre pour le prompt qu'il vous donne à copier, perdent l'option `--session` : le prompt ne porte plus le lien de la session qui part, dont la session neuve ne se sert pas, et qui ne s'ouvre pas d'un autre compte. Vous l'avez décidé le 24 novembre.
- `socle-request`, les demandes comme celle-ci. Une demande qui en remplace une autre, renvoyée par votre réponse « contexte insuffisant », la cite dans ses éléments cités ; l'état ne dit plus alors l'ancienne « à réécrire ». Retenu le 24 novembre (suggestion 1 de la revue de cap).

**Comment.** Une fois la demande validée, l'installeur, la commande du socle qui pose ou met à jour le moteur dans un projet, est relancé sur ce dépôt dans son mode, « amont », celui d'un dépôt qui fabrique le moteur (`install --target . --mode amont`) ; il réécrit les trois copies, que l'agent vérifie identiques aux empreintes ci-dessous. Il régénère aussi la section du socle dans `AGENTS.md`, les instructions que l'agent relit à chaque session : elle passerait le plafond de taille que les garde-fous de ce dépôt lui fixent, 16 341 octets pour 16 000, et l'agent la remet à son état commité, comme pour les copies remises le 24 novembre. Seule la section de ce dépôt reste ainsi en retard, ce que votre tri du backlog du 24 novembre a accepté ; les projets installés reçoivent la section entière.

## Éléments cités

Plus bas : `D-`, une demande ou une décision ; `T-`, une tâche ; `L-`, un lot ; `J-`, une entrée du journal, datée et lettrée ; après @, l'empreinte de la version lue ; `sha256:`, celle du fichier que l'installeur posera.

- .claude/skills/socle-batch/SKILL.md sha256:6d8d266b5eb14ce9
- .claude/skills/socle-handoff/SKILL.md sha256:6bc70a936df673d7
- .claude/skills/socle-request/SKILL.md sha256:f68f86ad3835bb31
- D-0181@9a42ba1d — votre décision du 24 novembre : le gabarit de `socle-batch` attend la CI du commit poussé, par son identifiant.
- D-0176@42bc84cc — votre décision du 24 novembre : le lien de la session qui part sort du prompt de passation.
- D-0180@76614e84 — votre décision du 24 novembre : les corrections restées hors de tout jalon, dont l'état qui disait encore « à réécrire » une demande remplacée, rejoignent ce lot.
- D-0175@6ad5e987 — la demande du 24 novembre, que vous avez validée, qui a remis de même trois copies protégées, la section d'`AGENTS.md` remise à son état commité.
- D-0168@f095a79d — votre tri du backlog du 24 novembre, qui a fermé la tâche de la section d'`AGENTS.md` en retard ici.
- D-0092@42266c33 — votre accord du 10 novembre : l'agent fusionne lui-même sa pull request.
- L-0036@445c700b — le lot en cours, que cette demande permet de clore.
- T-0176@62d4fb89 — la tâche qui a changé l'attente de la CI dans `socle-batch`.
- T-0174@bb0c4a05 — la tâche qui a retiré l'option `--session`, du moteur et de `socle-handoff`.
- T-0177@2f9f9392 — la tâche qui a changé l'état et `socle-request` pour une demande renvoyée déjà remplacée.
- J-2026-11-25-B@00245425 — la revue du lot : son seul constat bloquant, le gabarit de `socle-batch` qui ne disait plus que le dossier où une passation range le travail non relu est dans le dépôt, corrigé ; et les constats écartés.

## Où regarder

- [Le skill `socle-batch`](https://github.com/theodubus/memory/blob/3afb8d041c585f8ec99bd0b3f9e81580e914ee15/engine/socle/templates/skills/socle-batch/SKILL.md) : l'étape 3 de « Intégrer, pousser, livrer », où l'attente de la CI change.
- [Le skill `socle-handoff`](https://github.com/theodubus/memory/blob/3afb8d041c585f8ec99bd0b3f9e81580e914ee15/engine/socle/templates/skills/socle-handoff/SKILL.md) : les deux commandes de « Programmer » et « Le prompt à copier », sans `--session`.
- [Le skill `socle-request`](https://github.com/theodubus/memory/blob/3afb8d041c585f8ec99bd0b3f9e81580e914ee15/engine/socle/templates/skills/socle-request/SKILL.md) : « Relayer une réponse », la demande qui en remplace une autre et la cite.

## Options

- **Valider** : l'installeur remet les trois copies ; l'agent de ce dépôt suit dès la session suivante la procédure que chess recevra. Effort : une commande et sa vérification, dans ce lot. Risque : faible, du texte de procédure, déjà relu. Réversible : une demande de plus remet les anciennes copies.
- **Refuser** : les copies restent les anciennes. L'agent de ce dépôt attend déjà la CI du commit poussé, comme le dit `delegate-lot`, la procédure de ce dépôt pour mener un lot, qui prime ; sa copie de `socle-handoff` lui fait écrire une commande avec `--session`, que le moteur refuse désormais, et il se corrige à l'erreur ; sa copie de `socle-request` ne lui dit pas de citer la demande qu'il remplace, et l'état la dirait encore « à réécrire » ; l'état lui signale l'écart à chaque démarrage. Effort : aucun. Risque : faible, une gêne. Réversible : une demande nouvelle les remet.

## Conséquences

Si vous validez : l'installeur remet les trois copies, que l'agent commite avec votre réponse ; puis il clôt le lot, ouvre la pull request et la fusionne une fois la CI verte, selon votre accord du 10 novembre ; cette fusion publie le moteur dans le dépôt `theodubus/socle`, d'où chess se met à jour, comme à chaque fusion. Si vous refusez : le lot se clôt sans elles, la pull request se fusionne et le moteur se publie de même, et l'écart demeure dans ce dépôt jusqu'à une demande nouvelle. Sans réponse : le lot attend sa clôture ; rien d'autre ne change.

## Recommandation

Valider : ce sont les textes de vos décisions du 24 novembre, et l'agent de ce dépôt doit suivre ce que chaque projet recevra.

Vérifié : les trois empreintes sont celles des gabarits français relus par la revue du lot, son bloquant corrigé ; les tests des skills passent sur eux. Sur une copie jetable de ce dépôt, l'installeur ne touche que les trois copies, posées à ces empreintes, et la section d'`AGENTS.md` ; elle remise, tous les contrôles passent, hors celui des fichiers protégés, qui attend votre réponse.

Supposé : rien.

## Réponses possibles

- `valider` — l'installeur remet les trois copies protégées, commitées avec votre réponse.
- `refuser` — les copies restent les anciennes ; le lot se clôt sans elles.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
