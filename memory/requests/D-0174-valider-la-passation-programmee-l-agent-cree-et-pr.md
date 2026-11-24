<!-- socle: couche=demandes zone=publique -->
# D-0174 — Valider la passation programmée : l'agent crée et programme lui-même la session suivante, selon sa spécification

> date : 2026-11-24

## Décision demandée

Valider la spécification de la passation programmée : quand l'agent doit arrêter une session, il crée lui-même la suivante et programme son prompt, aux heures, dans les bornes et avec la garde qu'elle fixe.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code confié à un agent d'IA : il garde la mémoire du projet, vérifie le travail de l'agent et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, recevra ces changements à sa prochaine mise à jour.

**Le chantier.** Une conversation avec l'agent coûte plus cher à chaque échange à mesure qu'elle s'allonge ; d'où la règle d'un lot, un ensemble de tâches relues ensemble, par session. Aujourd'hui, à la fin d'un lot, l'agent vous donne un prompt à coller dans une session neuve que vous ouvrez. Le 10 novembre, vous avez demandé une solution automatique. Le 23, vous avez fixé un commutateur entre deux modes, que vous changez en le disant à l'agent : la « session programmée », par défaut, où l'agent crée lui-même la session suivante ; le « prompt à copier », pour qui a plusieurs comptes ou veut garder la main. Aujourd'hui, vous avez précisé que ce dépôt resterait au prompt à copier, pour jongler entre vos comptes, le produit gardant la session programmée par défaut.

**La question.** Le 23, vous avez renvoyé la demande précédente sur ce sujet, faute de contexte : elle opposait les deux modes au lieu de les réunir par le commutateur. Celle-ci la remplace. L'essai est fini depuis ce matin ; avant d'écrire le code, il reste à valider comment la session programmée marche : quand la suivante part, quand la chaîne s'arrête sans vous, et comment deux sessions évitent de faire le même travail.

**Les mots.** Une session est une conversation avec l'agent, dans Claude Code, dans le cloud. Une tâche programmée y envoie un message à l'heure dite. Les limites d'usage de votre compte se comptent en points, un pour cent de la limite : la fenêtre de cinq heures et la semaine ; un point de la semaine vaut environ sept de la fenêtre. Le mode `auto` est celui où une session écrit, commite et pousse sans vous demander d'approuver chaque commande. Une pull request regroupe les lots livrés sur une branche jusqu'à sa fusion dans `main`, après la CI (les contrôles automatiques sur GitHub) et la revue (la relecture du lot par un agent sans contexte).

**L'essai**, les 23 et 24 novembre. Deux façons de programmer étaient possibles : B, créer la session vide puis lui programmer son prompt ; A, une tâche qui crée la session à l'heure dite. La règle fixée avant l'essai : B si elle marche, sinon A. Quatre sessions d'essai, qui ne faisaient que lire, montrent que B marche : la session créée reçoit son prompt une à trois minutes après l'heure, même après une nuit ; elle tourne sur le modèle que lui donne la session qui la crée, en mode `auto`, avec l'état du projet ; elle n'a de branche où pousser que si on la lui nomme, ce que fait la spécification ; son niveau de réflexion, la profondeur de raisonnement du modèle, ne s'hérite pas, et la spécification le lui donne ; supprimer la tâche et archiver la session annulent tout.

**Le coût.** Une session programmée coûte ce que coûte une session que vous ouvrez : son démarrage, environ 1,1 point de la fenêtre, puis son travail ; un lot entier, de 8 à 16 points de la semaine, soit de 60 à 115 de la fenêtre. Elle évite le compactage (`/compact`, que vous seul lancez, résume la conversation), environ 8 points de la fenêtre, et la relecture d'une conversation après une pause de plus d'une heure, au prix fort, de 7 à 39 points de la fenêtre.

**Ce que dit la spécification :**

- **Quand.** Le lot livré, la session suivante part tout de suite, mais jamais sur une fenêtre de cinq heures déjà à 15 % ni sur une semaine à 75 % : elle part alors à la remise à zéro, plus cinq minutes. Un lot consommant de 60 à 115 points de la fenêtre, c'est le cas le plus courant ; c'est ce que vous suggériez le 23 : lancé sur une fenêtre entamée, un lot serait coupé en route. À dix points d'une limite (90 % de la fenêtre ou de la semaine), l'agent range et passe la main de même. Avant une attente de plus d'une heure, une CI longue par exemple, la suivante part à sa fin.
- **Les bornes.** Rien n'est programmé, et vous recevez le prompt à copier, quand le lot suivant n'a aucune tâche prête (une décision vous revient, ou rien n'est prêt), quand Claude Code refuse de créer la session, et après deux lots menés sans message de vous, le lot en cours compris : la chaîne dépense donc au plus de 16 à 32 points de la semaine en votre absence.
- **La garde.** La session programmée vérifie d'abord, par une commande du socle, que personne n'a poussé sur sa branche depuis la passation, et qu'aucune autre session n'a écrit la mémoire du projet sur une autre branche ; sinon elle s'arrête, en le disant. La session qui part pousse tout avant de programmer, et plus rien après : le 23 novembre, un commit poussé après la programmation aurait fait refuser la session programmée par sa garde.
- **La pull request ouverte.** Aujourd'hui, une session neuve qui trouve ouverte la pull request d'une autre vous demande de la fusionner ou de l'autoriser à y continuer, et l'agent ne fusionne que la sienne. Une session partie d'un prompt de passation que la garde accepte, programmé ou collé par vous, aura cette autorisation : elle continue la même pull request, qui devient la sienne. Elle ne la fusionne que si la politique d'autonomie du projet, un fichier que vous seul modifiez, le permet à l'agent, comme ici depuis le 10 novembre ; sinon vous fusionnez. Ici, cela change peu : une session fusionne d'ordinaire sa pull request avant de passer la main.
- **Vous voir prévenu.** Chaque session paraît aussitôt dans votre liste de sessions, titrée par exemple « Passation — lot du récap — part le 25 novembre à 10 h 05 » ; son dernier message dit ce qu'elle a fait, pourquoi la chaîne s'arrête ou ce que la garde a refusé, et ce qui vous revient. L'essai n'a pas montré de notification sur votre téléphone. Vous l'arrêtez en écrivant « arrête » dans la session qui l'a programmée, en me disant de changer de mode, ou en supprimant sa tâche et en l'archivant.
- **Où.** Un skill nouveau, `socle-handoff`, une procédure écrite que l'agent charge quand elle sert ; la section « Changer de session » du skill qui mène un lot (`socle-batch`) s'y réduit au rangement. Et une commande, `socle handoff`, qui écrit le prompt et juge la garde.

**Deux tests changent**, dans `tests/test_skills.py`, et `valider` l'autorise : `test_l_installeur_les_pose_et_la_politique_les_protege` et `test_dans_les_deux_langues_ils_passent_leurs_controles` (le français et l'anglais) attendent la liste des skills du produit, `socle-batch, socle-private-memory, socle-request, socle-resume, socle-review` ; elle gagne `socle-handoff` après `socle-batch`.

## Éléments cités

Plus bas : `B-`, un besoin ; `T-`, une tâche ; `L-`, un lot ; `D-`, une demande ou une décision ; `J-`, une entrée du journal ; après @, l'empreinte de la version lue.

- B-0156@90b1e18a — le besoin : une session longue se poursuit sans que vous en ouvriez une neuve à la main, même absent.
- B-0259@e8081dd0 — le besoin de la passation programmée, avec les inconnues de l'essai et sa règle de choix.
- T-0039@8705e56c — la tâche qui soumet la solution pour une conversation qui s'allonge, avec son coût ; cette demande la clôt.
- T-0041@7d2739e2 — la tâche de l'essai, dont cette demande soumet le relevé et la façon B.
- T-0080@a1e4a47d — la tâche de la spécification, que cette demande soumet.
- T-0079@d73995ea — la tâche qui écrira la solution dans les skills du produit.
- T-0081@e649c0eb — la tâche qui implémentera la commande, la garde et le commutateur.
- L-0010@30225967 — le lot en cours : la session longue, et la reprise après une limite d'usage.
- D-0160@33c44c1b — la demande précédente, renvoyée le 23 novembre faute de contexte, que celle-ci remplace.
- D-0161@ec4cc7cd — votre décision du 23 novembre : le commutateur, la session programmée par défaut.
- D-0173@163bc9a2 — votre décision d'aujourd'hui : ce dépôt au prompt à copier, le produit en session programmée.
- J-2026-11-23-J@9b849973 — votre question du 23 novembre sur le moment d'enchaîner, et l'avis rendu.

## Où regarder

- [La spécification](https://github.com/theodubus/memory/blob/f32ff5d054af0b2895722dd68cca232904b87cfb/docs/fabrication/passation-programmee-specification.md) : « Quand », « Les bornes d'une chaîne sans l'humain », « Le prompt et sa garde » et « La pull request ouverte ». Vérifier que les seuils, les bornes et l'autorisation vous conviennent.
- [Le relevé de l'essai](https://github.com/theodubus/memory/blob/f32ff5d054af0b2895722dd68cca232904b87cfb/docs/fabrication/passation-programmee.md) : « Après coup », ce que les sessions d'essai ont montré.

## Options

- La spécification telle qu'écrite (recommandée). Effort : T-0079 et T-0081, de 3 à 4 points de la semaine chacune, et une relecture. Risque moyen : une chaîne de sessions travaille sans vous, dans les bornes ci-dessus. Réversible : le prompt à copier l'arrête à tout moment, et ce dépôt y reste.
- La spécification avec vos changements (répondre `refuser`, en disant ce qui change : un seuil, une borne, l'autorisation). Effort : une réécriture et une demande nouvelle. Risque faible. D'ici là, le prompt à copier reste partout.

## Conséquences

Si vous validez : T-0039, T-0041 et T-0080 se ferment ; T-0079 écrit le skill `socle-handoff` ; T-0081 la commande et sa garde, change les deux tests nommés, et écrit l'autorisation de la pull request dans les instructions et le guide ; une note de version ; chess reçoit la session programmée à sa mise à jour ; ce dépôt reste au prompt à copier. Si vous refusez : la spécification se réécrit sur ce que vous dites et revient en demande ; d'ici là, le prompt à copier reste. Sans réponse : rien ne change, T-0079 et T-0081 attendent, et le lot s'arrête là.

## Recommandation

La spécification telle qu'écrite. Vérifié : les faits de l'essai et les coûts cités, mesurés sur ce compte ; le cas du 23 novembre. Supposé : qu'une session programmée écrive et pousse sans approbation en mode `auto`, l'essai n'ayant fait que lire ; qu'elle reparte d'une branche déjà poussée ; que les bornes suffisent. Les tests de T-0081 vérifieront ce qui se teste sans Claude Code ; le reste se verra au premier usage réel, chess après sa mise à jour.

## Réponses possibles

- `valider` — la spécification telle qu'écrite, et le changement des deux tests nommés ; T-0079 et T-0081 l'implémentent.
- `refuser` — elle ne convient pas : dites ce qui change ; elle se réécrit et revient en demande.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
