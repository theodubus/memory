<!-- socle: couche=demandes zone=publique -->
# D-0150 — Remettre la copie protégée du skill socle-batch de ce dépôt sur son gabarit, que le lot L-0020 a changé

> date : 2026-11-20

## Décision demandée

Autoriser l'agent à remettre la copie protégée de ce dépôt du skill `socle-batch` sur le texte exact de son gabarit, que le lot L-0020 a changé. Vous répondrez une fois la pull request du lot ouverte, après sa revue, son lien donné dans la conversation.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code tenu par un agent d'IA : il garde la mémoire du projet (décisions, journal, backlog des besoins et des tâches), vérifie ce que l'agent produit, et vous pose en demandes les décisions qui vous reviennent. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, est le projet pilote ; le dépôt `theodubus/socle` distribue le moteur seul.

**Le chantier.** Le lot L-0020 (des tâches menées et relues ensemble) traite le push et la fusion des pull requests par l'agent. Le 10 novembre, vous avez autorisé l'agent à fusionner lui-même ses pull requests dans ce dépôt ; le 13, vous avez voulu que tout ce qui est utile ici entre dans le produit ; le 17, qu'après une fusion l'agent vérifie ce qu'elle déclenche. Le lot fait de la fusion par l'agent une option de la politique de tout projet équipé, que seul l'humain active, et change en conséquence le skill `socle-batch` du produit, la procédure écrite que l'agent suit pour mener un lot. L'implémentation est faite ; restent la revue du lot par un relecteur sans contexte, la pull request et la fusion.

**La question.** Chaque skill du socle a deux textes : le gabarit, que le produit installe dans chaque projet, et, dans ce dépôt, une copie, celle que charge l'agent d'ici, protégée pour qu'il ne récrive pas ses propres règles : seul votre accord la change. Votre accord du 20 novembre a remis la copie de `socle-batch` sur son gabarit ; le lot vient de changer ce gabarit, et l'état du dépôt (le résumé que le socle calcule et donne à l'agent au démarrage) signale que la copie en diffère de nouveau.

**Ce qui change**, de la copie au gabarit, tout dans l'étape de la livraison :

- qui fusionne se lit dans la politique, `.socle/policy.toml`, le fichier où vous fixez ce que l'agent peut faire seul : par défaut vous ; l'agent, sa propre pull request, si la politique le permet, aux mêmes conditions qu'aujourd'hui (la CI verte sur le dernier commit, qu'il donne ; la revue faite ; aucune demande en attente sur son contenu). La copie disait « les instructions du projet le disent ». Dans ce dépôt, rien ne change : votre politique le permet depuis le 10 novembre, et les instructions de l'agent le disent ;
- après la fusion, l'agent attend les workflows (les scripts que GitHub lance) qu'elle déclenche sur la branche principale, comme il attend la CI, et son récap (le compte rendu de fin de tour) dit s'ils ont réussi. Ici, c'est la publication du moteur dans `theodubus/socle`, que l'agent vérifiait déjà par une règle propre à ce dépôt ;
- pour tenir sous le plafond de 8 000 octets d'un skill, deux phrases sur le changement de session resserrées, sans règle perdue.

## Éléments cités

- .claude/skills/socle-batch/SKILL.md sha256:c7cd2ef8d5fd84df

L'empreinte de cette ligne est celle du gabarit, que la copie prendra octet pour octet : votre accord porte sur ce texte exact. Plus bas : `D-`, une de vos décisions ; `L-`, un lot ; `T-`, une tâche ; `B-`, un besoin ; `ADR-`, une décision de l'agent ; après @, l'empreinte de la version lue.

- L-0020@7bab0c9d — le lot en cours, sur le push et la fusion par l'agent.
- T-0112@c1739d73 — sa tâche qui remet la copie protégée, sous cette demande.
- T-0064@d537c344 — la tâche qui a changé le gabarit de `socle-batch`.
- ADR-0103@1acee7a7 — la décision de l'agent : la fusion par l'agent devient une option de la politique, la ligne qui la retire des actions refusées.
- B-0218@fd498240 — le besoin des copies protégées en retard sur leur gabarit.
- D-0149@525a9975 — votre accord du 20 novembre, qui a remis la copie pour la dernière fois.
- D-0092@42266c33 — votre accord du 10 novembre : l'agent fusionne lui-même ses pull requests dans ce dépôt.
- D-0129@7c65528d — votre accord du 17 novembre : après une fusion, vérifier ce qu'elle déclenche.

## Où regarder

- [La copie actuelle](https://github.com/theodubus/memory/blob/792a2d860e2540698a99cd9fd3fe0d4e9dd2af7e/.claude/skills/socle-batch/SKILL.md), à remplacer : le point 4 de « Intégrer, pousser, livrer » et le premier paragraphe de « Changer de session ».
- Le texte nouveau : le gabarit `engine/socle/templates/skills/socle-batch/SKILL.md`, dans la pull request du lot ; y vérifier les trois changements dits plus haut.

## Options

- Valider : la copie devient son gabarit, octet pour octet ; effort faible, une réponse ; risque faible, c'est le texte que chess et tout projet recevront, relu par la revue du lot ; réversible par une demande nouvelle.
- Refuser : la copie reste ; l'état continue de signaler qu'elle diffère, jusqu'à une demande nouvelle ; effort nul ; risque faible, puisque dans ce dépôt l'ancienne étape mène au même geste ; réversible.

## Conséquences

Si vous validez : l'agent pose la copie par l'installeur (la commande qui installe ou met à jour le socle), la commite avec votre réponse, puis fusionne la pull request du lot. Si vous refusez : la copie reste, l'agent fusionne la pull request sans elle, et la tâche qui la remet se ferme sur votre refus. Sans réponse : la pull request attend, puisque l'agent ne fusionne pas sous une demande en attente sur son contenu. Si la revue change ce gabarit, l'agent vous le dit avec le lien de la pull request, et une demande nouvelle remplace celle-ci.

## Recommandation

Valider. Vérifié : l'empreinte citée est celle du fichier que pose l'installeur, relancé dans un dossier jetable, identique octet pour octet au gabarit ; seule cette copie diffère de ce que l'installeur poserait, comme l'état le dit ; les différences sont celles dites plus haut, lues dans le diff de la copie à son gabarit. Supposé : que la revue ne changera pas ce gabarit.

## Réponses possibles

- `valider` — la copie devient son gabarit.
- `refuser` — la copie reste telle quelle.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
