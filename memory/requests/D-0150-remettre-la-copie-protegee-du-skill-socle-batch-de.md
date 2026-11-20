<!-- socle: couche=demandes zone=publique -->
# D-0150 — Remettre la copie protégée du skill socle-batch de ce dépôt sur son gabarit, que le lot L-0020 a changé

> date : 2026-11-20

## Décision demandée

Autoriser l'agent à remettre la copie protégée du skill `socle-batch` de ce dépôt, `theodubus/memory`, sur le texte exact de son gabarit, que le lot L-0020 a changé. Vous répondrez une fois la pull request du lot ouverte, après sa revue, son lien donné dans la conversation.

## Contexte

**Le projet.** Ce dépôt, `theodubus/memory`, fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code tenu par un agent d'IA : il garde la mémoire du projet (décisions, journal, backlog des besoins et des tâches), vérifie ce que l'agent produit, et vous pose en demandes les décisions qui vous reviennent. Le produit est ce qu'un projet reçoit à l'installation : le moteur, ses gabarits et son guide ; un projet équipé est un projet où il est installé. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, est le projet pilote ; le dépôt `theodubus/socle` distribue le moteur seul.

**Le chantier.** Le lot L-0020 (des tâches menées et relues ensemble) traite le push et la fusion des pull requests par l'agent. Le 10 novembre, vous avez autorisé l'agent à fusionner lui-même ses pull requests dans ce dépôt ; le 13, vous avez demandé que ce qui sert ici entre dans le produit ; le 17, qu'après une fusion l'agent vérifie ce qu'elle déclenche. Le lot fait de la fusion par l'agent une option de la politique de tout projet équipé : une ligne `[irreversible] tools`, commentée par défaut, que seul l'humain décommente, et qui retire la fusion de la liste des actions que l'agent se voit refuser. Il change en conséquence le skill `socle-batch` du produit, la procédure écrite que l'agent suit pour mener un lot. L'implémentation est faite ; restent la revue du lot par un relecteur sans contexte (un autre agent, lancé sans la conversation), la pull request et la fusion.

**La question.** Chaque skill du socle a deux textes : le gabarit, que le produit installe dans chaque projet, et, dans ce dépôt, une copie, celle que charge l'agent d'ici, protégée pour qu'il ne récrive pas ses propres règles : seul votre accord la change. Votre accord du 20 novembre a remis la copie de `socle-batch` sur son gabarit ; le lot vient de changer ce gabarit, et l'état du dépôt (le résumé que le socle calcule et donne à l'agent au démarrage) signale que la copie en diffère de nouveau. Le gabarit change dans la pull request quelle que soit votre réponse : vous ne tranchez ici que la copie de ce dépôt. Chess recevra le skill changé à sa prochaine mise à jour, avec les autres fichiers protégés de celle-ci, sous la demande que son installeur pose.

**Ce qui change**, de la copie au gabarit, mot pour mot.

L'étape 4 de la livraison (« Intégrer, pousser, livrer »), avant :

> Qui fusionne, les instructions du projet le disent : par défaut l'humain, et le lot suivant s'ajoute à la même pull request ; l'agent, la sienne, si elles le permettent : CI verte sur le commit de tête, qu'il donne, revue faite, aucune demande en attente sur son contenu.

Après :

> Qui fusionne : par défaut l'humain, et le lot suivant s'ajoute à la même pull request ; l'agent, la sienne, si la politique le permet : CI verte sur le commit de tête, qu'il donne, revue faite, aucune demande en attente sur son contenu. Il attend de même les workflows que la fusion lance sur la branche par défaut ; le récap dit s'ils ont réussi.

« Le commit de tête, qu'il donne » : l'agent vous donne l'identifiant du dernier commit dont la CI (les vérifications que GitHub lance à chaque envoi) est verte. Les workflows sont les scripts que GitHub lance ; le récap, le compte rendu de fin de tour de l'agent. Dans ce dépôt, rien ne change dans les faits : votre politique permet la fusion depuis le 10 novembre, et les instructions de l'agent, `AGENTS.md`, le disent ; le workflow qu'une fusion lance est la publication du moteur dans `theodubus/socle`, que l'agent vérifiait déjà par le skill `delegate-lot`, propre à ce dépôt.

Le premier paragraphe de « Changer de session », la section qui dit quand l'agent range et passe la main à une session neuve, avant :

> Quand le lot est livré et que la fenêtre ne permet pas d'en mener un autre entier, ou qu'une attente de plus d'une heure s'annonce. Ranger d'abord, pour qu'une session neuve reparte du dépôt seul :

Après :

> Quand le lot est livré sans fenêtre pour un autre, ou avant une attente de plus d'une heure. Ranger d'abord, qu'une session neuve reparte du dépôt seul :

Dans la même section, « dire à l'humain pourquoi changer de session » devient « dire à l'humain pourquoi ». Et dans « Un sous-agent par tâche », la phrase « Sans la conversation, sa consigne se lit seule. » devient « Sa consigne se lit sans la conversation. ». Ces resserrements tiennent le skill sous le plafond de 8 000 octets qu'un contrôle du socle impose à chaque skill : il fait 7 998 octets.

## Éléments cités

- .claude/skills/socle-batch/SKILL.md sha256:d79c42c1a513fe4a

Cette ligne nomme la copie, que vous autorisez à changer, et l'empreinte du texte qu'elle prendra, celui du gabarit `engine/socle/templates/skills/socle-batch/SKILL.md`, octet pour octet : votre accord porte sur ce texte exact. L'empreinte est le début de sa somme SHA-256 (`sha256sum` sur le gabarit, ses seize premiers caractères). Plus bas : `D-`, une de vos décisions ; `J-`, une entrée du journal ; `L-`, un lot ; `T-`, une tâche ; `B-`, un besoin ; `ADR-`, une décision de l'agent ; après @, l'empreinte de la version lue.

- L-0020@7bab0c9d — le lot en cours, sur le push et la fusion par l'agent.
- T-0112@c1739d73 — sa tâche qui remet la copie protégée, et qui attend cette demande.
- T-0064@d537c344 — la tâche qui a changé le gabarit de `socle-batch`.
- ADR-0103@1acee7a7 — la décision de l'agent : la fusion par l'agent devient l'option de la ligne `[irreversible] tools` de la politique.
- B-0218@fd498240 — le besoin des copies protégées en retard sur leur gabarit.
- D-0149@525a9975 — votre accord du 20 novembre, qui a remis la copie pour la dernière fois.
- D-0092@42266c33 — votre accord du 10 novembre : l'agent fusionne lui-même ses pull requests dans ce dépôt.
- J-2026-11-13-F@8a674408 — votre consigne du 13 novembre : ce qui sert ici entre dans le produit.
- D-0129@7c65528d — votre accord du 17 novembre : après une fusion, vérifier ce qu'elle déclenche.

## Où regarder

- [La copie actuelle](https://github.com/theodubus/memory/blob/792a2d860e2540698a99cd9fd3fe0d4e9dd2af7e/.claude/skills/socle-batch/SKILL.md), à remplacer : le point 4 de « Intégrer, pousser, livrer » et les sections « Changer de session » et « Un sous-agent par tâche », où lire le texte d'avant cité plus haut.
- Le texte nouveau : le gabarit `engine/socle/templates/skills/socle-batch/SKILL.md`, dans la pull request du lot ; y vérifier les passages cités plus haut, seuls changés.

## Options

- Valider : la copie devient son gabarit, octet pour octet ; effort faible, une réponse ; risque faible, c'est le texte que chess et tout projet recevront, relu par la revue du lot ; réversible par une demande nouvelle.
- Refuser : la copie reste ; l'état continue de le signaler au démarrage de chaque session, d'une ligne, sans qu'aucun contrôle échoue ni que rien ne se bloque, jusqu'à une demande nouvelle ; effort nul ; risque faible, puisque dans ce dépôt l'ancienne étape mène au même geste ; réversible.

## Conséquences

Si vous validez : l'agent pose la copie par l'installeur (la commande qui installe ou met à jour le socle), la commite avec votre réponse, puis fusionne la pull request du lot. Si vous refusez : la copie reste, l'agent fusionne la pull request sans elle, et la tâche qui la remet se ferme sur votre refus. Sans réponse : la pull request attend, puisque l'agent ne fusionne pas sous une demande en attente sur son contenu. Si la revue change ce gabarit, l'agent vous le dit avec le lien de la pull request, et une demande nouvelle remplace celle-ci.

## Recommandation

Valider. Vérifié : l'empreinte citée est celle du fichier que pose l'installeur, relancé dans un dossier jetable, identique octet pour octet au gabarit ; seule cette copie diffère de ce que l'installeur poserait, comme l'état le dit ; les passages cités sont, mot pour mot, tout le diff de la copie au gabarit. Supposé : que la revue ne changera pas ce gabarit.

## Réponses possibles

- `valider` — la copie devient son gabarit.
- `refuser` — la copie reste telle quelle.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
