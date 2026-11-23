<!-- socle: couche=demandes zone=publique -->
# D-0160 — La solution du contexte long : un lot par session, et la suivante programmée par l'agent

> date : 2026-11-23

## Décision demandée

Retenir pour le contexte long la passation programmée : un lot par session ; à la fin d'un lot, ou avant une attente longue ou une limite d'usage, l'agent range puis programme lui-même la session suivante, au lieu de vous donner un prompt à coller ou de vous demander de compacter.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code tenu par un agent d'IA : il garde la mémoire du projet, vérifie ce que l'agent produit, et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, qui l'a déjà, recevra ces changements à sa prochaine mise à jour.

**Le chantier.** Le jalon en cours corrige et stabilise le produit avant cette mise à jour. Son lot L-0010, un ensemble de tâches relues ensemble, traite le contexte long : une conversation qui coûte de plus en plus à relire à mesure qu'elle s'allonge, et la friction d'en ouvrir une neuve. Le 10 novembre, vous avez demandé une solution automatique, puis retenu le compactage que vous lancez et un sous-agent par tâche, la passation restant une piste. Le 12, vous avez voulu que l'agent dise quand changer de session et donne le prompt de la suivante. Le 16, vous avez fait inscrire la passation programmée ; le 21, vous l'avez laissée dans ce lot, sans l'avancer.

**La question.** Les essais sont mesurés, sauf un, qui se lit demain matin : il reste à choisir la solution, que la tâche T-0079 écrira dans un skill, une procédure écrite que l'agent charge quand elle sert, celui qui mène un lot (`socle-batch`), que chess recevra aussi. Elle doit dire ce que fait l'agent quand vous n'êtes pas là pour compacter : aujourd'hui rien ne le dit.

**Les mots.** Une session est une conversation avec l'agent ; celle qui orchestre mène le lot et lance des sous-agents, des agents neufs qui font une tâche et ne rendent que leur résultat. Compacter (`/compact`, que vous seul lancez) résume la conversation. Ranger : tout commiter et pousser, écrire la mémoire, retirer les réveils. Les limites d'usage se comptent en points, un pour cent de la limite : la fenêtre de cinq heures et la semaine ; un point de la semaine vaut environ sept de la fenêtre. Après une pause de plus d'une heure, la conversation se relit « à froid », au prix fort.

**Les coûts mesurés**, sur ce compte :

| Geste | Coût |
| --- | --- |
| Démarrer une session neuve, que vous l'ouvriez ou que l'agent la programme (essai du 23 novembre) | 1,1 point de la fenêtre, plus ce qu'elle lit pour reprendre |
| Compacter une conversation chaude | 8 points de la fenêtre |
| Relire à froid après une pause | 7 points à 100 000 jetons, 20 à 300 000, 39 mesurés à 576 000 |
| Une tâche par un sous-agent ; le relecteur d'un lot | 3 à 4 points de la semaine ; 3 |
| Un lot entier | 8 à 16 points de la semaine |

La session qui mène ce lot, sans compactage, relit 244 000 jetons par appel en médiane. Passation programmée et prompt à copier coûtent pareil : ils ne diffèrent que par votre geste et par le travail fait en votre absence.

**La passation programmée.** L'agent crée la session suivante et programme son prompt : tout de suite à la fin d'un lot ; à la fin d'une attente longue (une CI, la nuit) ; près d'une limite, à sa remise à zéro plus cinq minutes, celle de la semaine si c'est elle. La session neuve repart de la mémoire du dépôt, en mode `auto`, celui où la session d'aujourd'hui écrit, commite et pousse sans vous demander d'approuver chaque commande. Elle fait ce que fait une session que vous ouvrez : sa branche, sa pull request, et la fusion de celle-ci seulement aux conditions de votre accord du 10 novembre (CI verte, revue faite, aucune demande en attente) ; jamais un push sur `main`.

**Ses bornes, proposées pour sa spécification.** La chaîne s'arrête dès qu'une décision vous revient, après deux lots menés sans message de vous, et avant 90 % de la semaine : elle ne repart alors qu'à votre retour. Chaque session programmée s'affiche dans votre liste de sessions, avec un titre qui dit ce qu'elle est et quand elle partira ; vous l'arrêtez en écrivant « arrête » dans la session en cours, ou en supprimant sa tâche programmée.

**Ce que votre réponse ne tranche pas.** La façon de programmer : en deux appels, une session créée vide puis son prompt programmé, ou en un, une tâche qui crée la session à l'heure dite. L'essai de la première a réussi sauf un point, qui se lit demain matin : qu'une session laissée vide une nuit reçoive encore son prompt. La demande qui suivra vous soumettra le choix. Si aucune façon ne tient, le prompt à copier reste malgré votre accord, et je vous le dis. Viendront ensuite la spécification, avec ses gardes contre deux sessions qui mèneraient le même lot, et un commutateur entre « session programmée » et « prompt à copier », pour les jours où vous passez sur un autre compte Claude, que l'agent ne peut pas programmer.

## Éléments cités

Plus bas : `JA-`, un jalon ; `L-`, un lot ; `T-`, une tâche ; `B-`, un besoin ; `D-`, une demande ; `J-`, une entrée du journal ; après @, l'empreinte de la version lue.

- B-0156@90b1e18a — le besoin : une session longue se poursuit sans que vous en ouvriez une neuve à la main, même absent.
- B-0259@e8081dd0 — le besoin de la passation programmée, inscrit le 16 novembre.
- T-0039@8705e56c — la tâche qui pose cette demande.
- T-0079@d73995ea — la tâche qui écrira la solution dans le skill `socle-batch`.
- T-0041@7d2739e2 — la tâche de l'essai, dont la demande suivra.
- T-0080@a1e4a47d — la tâche de la spécification et du commutateur.
- T-0081@e649c0eb — la tâche du mode « session programmée ».
- L-0010@9054c455 — le lot de la session longue et de la reprise, en cours.
- JA-0005@1a6ff5b2 — le jalon : le produit corrigé et stabilisé avant la mise à jour de chess.
- D-0155@34c3792a — votre réponse du 21 novembre, la passation laissée dans ce lot.
- J-2026-11-10-O@74460f36 — le 10 novembre : le compactage et un sous-agent par tâche retenus.
- J-2026-11-12-P@7557c894 — le 12 novembre : changer de session, avec le prompt de la suivante.
- J-2026-11-12-N@0d72078a — la mesure du compactage et des relectures à froid.
- J-2026-11-13-E@4a804f02 — la mesure d'un sous-agent et d'un relecteur.
- J-2026-11-23-D@c2d7f19f — la troisième revue de cap, un bilan de direction, qui chiffre un lot.

## Où regarder

- [Le relevé de l'essai](https://github.com/theodubus/memory/blob/1b399e7c66c6244da37aff1cffe5b2b844143964/docs/fabrication/passation-programmee.md) : ce que les sessions créées par l'agent ont fait, et leur coût.
- [La mesure de la consommation](https://github.com/theodubus/memory/blob/a68f5bc0c33b035623d38de1c6c5178b6a20444e/docs/fabrication/consommation.md), « Ce que la mesure suggère pour les règles » : le compactage, la relecture à froid, les sous-agents.
- [Le skill `socle-batch`](https://github.com/theodubus/memory/blob/a68f5bc0c33b035623d38de1c6c5178b6a20444e/engine/socle/templates/skills/socle-batch/SKILL.md), « La consommation » et « Changer de session » : ce que la solution remplacera.

## Options

Dans les trois, un sous-agent mène les grosses tâches et la session qui orchestre les petites, comme aujourd'hui.

- La passation programmée (recommandée). Effort : T-0079, T-0080 et T-0081, l'essai presque fini. Risque moyen : une chaîne de sessions travaille sans vous, dans les bornes ci-dessus. Réversible : le commutateur ramène au prompt à copier.
- Le prompt à copier, tel qu'aujourd'hui : vous ouvrez chaque session. Absent, la session range et attend. Effort : T-0079 seule. Risque faible ; la friction reste. Réversible.
- Le compactage : une seule session enchaîne les lots, et vous la compactez à la fin de chacun. Absent, l'agent range et attend votre retour, qui coûte une relecture à froid, jusqu'à une quarantaine de points de la fenêtre. Effort : T-0079 seule. Réversible.

## Conséquences

Si vous validez : T-0079 écrit la passation programmée dans le skill, en français et en anglais, avec une note de version ; la façon de programmer vous est soumise après l'essai de la nuit, puis la spécification avec ses bornes ; d'ici là, le prompt à copier reste. Si vous refusez : le skill garde le prompt à copier et dit le cas où vous êtes absent ; la passation programmée s'abandonne, B-0156 se ferme sur ce choix. Si vous choisissez le compactage : le skill le dit, la passation programmée s'abandonne, B-0156 se ferme de même. Sans réponse : rien ne change, et T-0079 attend.

## Recommandation

La passation programmée. Vérifié : les coûts cités, mesurés sur ce compte ; une session créée vide a reçu son prompt programmé, a démarré sur le modèle demandé (Opus 5.5) avec l'état du projet, et a lancé ses commandes de lecture sans attendre d'approbation. Supposé : qu'une session laissée vide une nuit reçoive encore son prompt (lu demain matin) ; qu'elle écrive et pousse sans approbation, comme celle d'aujourd'hui en mode `auto` ; que les bornes proposées suffisent, ce que la spécification éprouvera.

## Réponses possibles

- `valider` — la passation programmée, écrite au skill par T-0079 ; la façon de programmer et la spécification vous viennent ensuite.
- `refuser` — le prompt à copier reste ; le skill dit le cas où vous êtes absent.
- `compactage` — une seule session enchaîne les lots, compactée par vous à la fin de chacun.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
