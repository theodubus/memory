<!-- socle: couche=demandes zone=publique -->
# D-0138 — Remettre la copie protégée du skill socle-review au texte de son gabarit, que le lot L-0015 a changé

> date : 2026-11-19

## Décision demandée

Autoriser l'agent à remettre la copie protégée de ce dépôt du skill `socle-review` au texte exact de son gabarit, que le lot L-0015 a changé aujourd'hui.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code entretenu par un agent d'IA : il garde la mémoire du projet (ses décisions, son journal, son backlog, la liste du travail à faire), vérifie ce que l'agent produit, et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, est le projet pilote.

**Le chantier.** L'agent mène le travail par lots, des tâches menées ensemble ; avant de livrer un lot, il le fait relire par un relecteur sans contexte, un autre agent chargé de le prendre en défaut : c'est la revue, dont le skill `socle-review` est la procédure. Chaque relecture est une passe, et le recul écrit après chacune décide d'en faire une de plus ou de s'arrêter. Le lot L-0015, fini et fusionné aujourd'hui, a outillé cet historique des passes : `socle review`, la commande qui prépare la revue, reconnaît une passe relancée sans changement, refuse une ligne de constat mal écrite, et montre l'historique quand il refuse une passe ou la clôture du lot. Ce matin, vous avez validé la remise des copies de `socle-review`, `socle-batch` et `socle-request` sur leurs gabarits ; la demande annonçait que L-0015 changerait encore celui de `socle-review`, et que sa copie suivrait par une demande à la fin du lot : c'est celle-ci.

**La question.** Un skill est une procédure écrite que l'agent charge quand elle sert. Chacun a deux textes : le gabarit, que le produit installe dans chaque projet (chess le recevra à sa mise à jour, quelle que soit votre réponse), et, dans ce dépôt, une copie, celle que charge l'agent d'ici, protégée pour qu'il ne récrive pas ses propres règles : seul votre accord la change. La copie de `socle-review` a le texte que vous avez validé ce matin, d'avant les trois tâches de L-0015 qui ont changé le gabarit. Les copies des quatre autres skills du socle (`socle-batch`, `socle-request`, `socle-resume`, `socle-private-memory`) ont déjà le texte de leur gabarit. Le gabarit nouveau a été relu par le relecteur de L-0015, un agent, pas par vous.

**Ce qui change**, de la copie au gabarit, en cinq passages.

1. Le relecteur reçoit le chemin du dossier, pas son texte (T-0062), la règle que vous avez voulue dans le produit le 17 novembre. Le dossier est ce que `socle review` produit pour le relecteur : la consigne, le diff du lot, les entrées du backlog et les décisions qui le concernent. Avant, il était le seul message du relecteur, et restait dans la conversation de l'agent qui mène le lot, relu à chacun de ses appels (24 Ko pour une passe d'un lot du 16 novembre). Le texte nouveau : « Le dossier n'y entre pas, qui la relirait à chaque pas : la sortie de `socle review` s'écrit dans un fichier hors du dépôt, et le seul message du relecteur (sous Claude Code, un sous-agent, outil `Agent`) donne son chemin, avec la consigne de le lire en entier et de le suivre tel quel. »
2. Pour tenir sous le plafond de 8 000 octets que les garde-fous (des règles que le socle fait respecter, déclarées dans un réglage que vous seul assouplissez) fixent à un skill, trois précisions sortent du texte, que l'outil dit lui-même : le commit d'où se mesure le diff du lot quand la branche distante le contient déjà (`socle review` le dit, avec sa raison, en tête du dossier) ; le refus d'une option `--base` ou `--since` qui nomme un commit inconnu ou hors de l'historique (`socle review` le refuse, en le disant) ; et ce que le hook de l'agent, le programme qui contrôle chacune de ses commandes, refuse au relecteur (le hook le dit à chaque refus). Il reste : « le dossier lui dit de ne rien modifier hors d'un dossier temporaire (`mktemp -d`), ce que le hook de l'agent n'impose pas. »
3. La passe se commite (T-0055) : `socle review` l'écrit dans l'entrée du lot au backlog, souvent dans la copie du dépôt d'un sous-agent, effacée après. Le texte nouveau : « Commiter la passe écrite, et ce qu'on y consigne : sinon, elle se perd là où `socle review` a tourné. » Sans quoi la passe suivante repartirait de « Passe 1 », sans le recul exigé.
4. À la clôture d'un lot relu, le contrôle qui refuse un lot clos sans recul montre ce que montre le refus d'une passe (T-0055) : l'historique, les entrées que le lot a ouvertes et closes selon git, et les trois questions du recul (les bloquants ont-ils la cause de ceux d'avant ? ce que le lot ouvre est-il de la nature de ce qu'il ferme ? les lots clos sur les mêmes fichiers ont-ils ouvert de telles entrées ?).
5. Le dossier donne aussi les décisions de conception de l'agent et les demandes que citent celles que le lot écrit (T-0056), pas seulement celles que citent ses entrées du backlog.

**L'effet de votre réponse.** `delegate-lot`, le skill propre à ce dépôt qui dit ce qui s'ajoute ici aux skills du produit, n'est pas protégé : l'agent le tient seul. Il dit déjà de ranger le dossier dans un fichier et de n'en donner au relecteur que le chemin, et de commiter la passe : c'était la pratique de ce dépôt ; la revue de L-0015 s'est faite ainsi. Si vous validez, la copie le dit aussi, et ne contredit plus `delegate-lot`. Si vous refusez, la copie garde le texte de ce matin jusqu'à la remise de toutes les copies en retard (T-0072, qui remettra aussi celles que L-0006 aura changées), et sur ces deux points l'agent suit `delegate-lot` ; les points 4 et 5 sont le fait de l'outil, qui s'applique quelle que soit la copie. Aucune vérification ne signale encore une copie en retard (B-0218).

L'installeur, le programme qui pose le socle dans un projet et l'y met à jour, relancé pour poser cette copie, change aussi deux lignes de la section d'`AGENTS.md` (le fichier d'instructions de l'agent) qu'il écrit lui-même : l'une dit de coller la suite du projet quand vous la demandez, l'autre nomme ce résumé parmi les étapes de la CI. Sans rapport avec ce skill, elles feraient passer le fichier au-delà de son plafond de 16 000 octets : la section reste telle quelle, comme ce matin, jusqu'à la tâche T-0069.

## Éléments cités

- .claude/skills/socle-review/SKILL.md sha256:4ab7fe91f564377a

L'empreinte de cette ligne est celle que la copie aura, celle de son gabarit : votre accord porte sur ce texte exact. Plus bas : `D-`, une demande comme celle-ci ; `L-`, un lot ; `B-`, un besoin, un résultat à atteindre ; `T-`, une tâche, le livrable d'un commit qui sert un besoin ; après @, l'empreinte de la version lue.

- D-0137@8a882c42 — votre accord de ce matin qui a remis cette copie, avec celles de `socle-batch` et `socle-request`, au texte d'avant L-0015.
- D-0129@7c65528d — votre accord du 17 novembre de porter dans le produit trois pratiques de ce dépôt, dont le chemin du dossier donné au relecteur.
- L-0015@a86a520b — le lot clos de l'historique des revues, avec sa passe de revue et son recul.
- T-0062@5526673e — la tâche qui fait donner au relecteur le chemin du dossier, pas son texte.
- T-0055@1cb9ac7c — la tâche qui fait commiter la passe et montre l'historique au refus de la clôture.
- T-0056@eef926ec — la tâche qui ajoute au dossier les décisions et les demandes citées par celles du lot.
- L-0005@6ba5c924 — le lot suivant, sur les commandes que le hook de l'agent juge mal ; il ne touche pas ce skill.
- L-0006@c60c9481 — le lot des copies protégées et des skills, qui suit les lots du hook, sans date : environ un lot par session.
- B-0218@fd498240 — le besoin des copies protégées en retard sur leurs gabarits, qu'aucune vérification du socle ne signale.
- T-0072@f84a75da — la tâche qui remettra toutes les copies en retard, à la fin du lot L-0006.
- T-0069@92a4d3a7 — la tâche qui remettra la section du socle d'`AGENTS.md` sur son gabarit, une fois raccourcie la partie propre à ce dépôt.

## Où regarder

- Le texte nouveau, [le gabarit de `socle-review`](https://github.com/theodubus/memory/blob/63fb0beea1c74da253ac38cb7936e2c1b40ddf5f/engine/socle/templates/skills/socle-review/SKILL.md) : l'étape 3 de « Comment » et le premier paragraphe de « L'historique du lot et le recul ».
- [La copie actuelle](https://github.com/theodubus/memory/blob/63fb0beea1c74da253ac38cb7936e2c1b40ddf5f/.claude/skills/socle-review/SKILL.md), à remplacer.
- Le changement du gabarit, tâche par tâche, dans le diff de `engine/socle/templates/skills/socle-review/SKILL.md` de chaque commit : [T-0062](https://github.com/theodubus/memory/commit/3909a0aeb3797a1c9ec2bf2cb3a405adffeeef69), [T-0056](https://github.com/theodubus/memory/commit/0b194d3c284fcfbe51b0f5c91c1643f496d2a785), [T-0055](https://github.com/theodubus/memory/commit/dda074d70d9bc635a9fec5d2e891e75283d58138).
- [Votre accord du 17 novembre](https://github.com/theodubus/memory/blob/63fb0beea1c74da253ac38cb7936e2c1b40ddf5f/memory/requests/D-0129-ouvrir-au-backlog-dans-les-lots-dont-la-regle-s-ap.md), son premier point.

## Options

- Valider : la copie devient son gabarit, octet pour octet ; effort faible ; risque faible, c'est le texte relu par un agent et fusionné que chess recevra ; réversible par une demande nouvelle.
- Refuser : la copie garde le texte de ce matin jusqu'à T-0072 ; effort nul ; réversible.

## Conséquences

Si vous validez : l'agent pose la copie par l'installeur, sans `AGENTS.md`, et la commite avec votre réponse dans un même push ; il mène ensuite le lot L-0005 avec ce texte. Si vous refusez : rien ne change dans ce dépôt, et l'agent mène L-0005 comme le dit « L'effet de votre réponse ». Sans réponse : de même, la demande restant en attente.

## Recommandation

Valider. Vérifié : l'empreinte citée est celle du fichier que l'installeur pose, relancé dans un clone jetable de ce dépôt, identique octet pour octet au gabarit ; les différences sont les cinq passages dits plus haut, lus dans le diff de la copie au gabarit ; les trois précisions retirées, lues dans le code : `socle review` dit la base retenue et sa raison, et refuse une référence inconnue en le disant ; le hook dit chacun de ses refus ; les quatre autres copies des skills du socle sont identiques à leurs gabarits ; `delegate-lot` dit bien le chemin du dossier et la passe commitée ; les deux lignes d'`AGENTS.md` ne touchent pas ce skill. Supposé : rien.

## Réponses possibles

- `valider` — la copie devient son gabarit, avec votre réponse dans le même push.
- `refuser` — la copie reste telle quelle jusqu'à la remise de toutes les copies.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
