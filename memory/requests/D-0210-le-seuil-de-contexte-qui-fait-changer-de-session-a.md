<!-- socle: couche=demandes zone=publique -->
# D-0210 — Le seuil de contexte qui fait changer de session à la fin d'un lot : garder 300 000 jetons, le baisser à 150 000, le retirer, ou dire que les mesures ne tranchent pas

> date : 2026-11-26

## Décision demandée

Choisir le seuil au-delà duquel une session, à la fin d'un lot, passe la main à une session neuve au lieu d'enchaîner le lot suivant : le baisser de 300 000 à 150 000 jetons de contexte, comme je le recommande, le garder, le retirer, ou dire que les mesures ne tranchent pas.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, le moteur que reçoit un projet comme chess : mémoire, documentation et tests tenus par des contrôles, des hooks et la CI, pour un agent qui travaille seul sur le backlog. Ses règles de travail sont écrites dans des skills, que chaque projet reçoit.

**Le chantier.** Le jalon en cours corrige le produit avant la mise à jour de chess. Le 25 novembre, tu as retenu une réforme de l'organisation : la session est l'unité de budget, et, à la fin d'un lot, elle enchaîne le suivant si sa conversation reste sous 300 000 jetons de contexte. Le 26, tu as demandé d'où venait ce chiffre, sans vouloir d'« une décision par defaut non reflechie », puis tu as retenu de le trancher sur les mesures déjà prises, sans attendre la réécriture du prompt de chess.

**La question.** Les mesures sont relevées. Le chiffre retenu passe dans le skill `socle-batch`, le guide de l'utilisateur et la page qui décrit l'organisation du travail ; chess les recevra à sa mise à jour.

**Les mots.** Un lot est un groupe de tâches du backlog menées et relues ensemble ; un jalon, un ensemble de besoins. chess est le premier projet qui utilise le socle ; sa mise à jour passe par un prompt, le texte que son agent reçoit. L'atelier est ce dépôt. Une passation est la note qu'une session écrit dans la mémoire avant de s'arrêter ; la reprise, sa lecture par la session neuve. Au prompt à copier, le mode de l'atelier, c'est toi qui ouvres la session neuve et y écris « reprends » : tu jongles ainsi entre tes comptes. Un appel est un appel au modèle ; un jeton, un morceau de mot. Un point de la semaine est 1 % de ce que ton compte permet en sept jours ; un point de cinq heures, 1 % de la limite courte, qui se remet à zéro toutes les cinq heures. Sept points de cinq heures font environ un point de la semaine (55 pour 8, 36 pour 5, plus bas).

**Le coût.** À chaque appel, le modèle relit toute la conversation depuis le cache, une mémoire où relire coûte moins qu'écrire : plus la conversation est longue, plus chaque appel coûte. Une session neuve repart de la mémoire du dépôt, avec environ 70 000 jetons. Le seuil de 300 000 est né de ce raisonnement, à la réforme du 25 novembre, sans mesure. Les mesures, sur Opus 5.5 :

| session | travail | contexte à la fin | semaine | cinq heures |
| --- | --- | ---: | ---: | ---: |
| 25 nov., L-0041 | un lot, la revue de cap 7 | ~300 000 | 8 | 62 |
| 26 nov., L-0043 | deux tâches, une revue, une correction, une demande | 366 000 | 8 | 55 |
| 26 nov., clôture de L-0043 | la revue de cap 8, quatre décisions, sans code | 294 000 | 5 | 36 |
| 26 nov., cette reprise | la passation lue, son commit poussé | ~70 000 | < 1 | 3 |

**Le calcul.** Le 12 novembre, sur Fable, un autre modèle, la relecture faisait 59 % du coût d'un appel à 300 000 jetons. Sur L-0043, 47,2 millions de jetons relus pour 8 points : 59 % de 8 points, soit 4,7, pour 47,2 millions, donc environ 0,1 point par million de jetons relus (0,08 sur la session de clôture) ; je prends 0,09. L-0043 a fait environ 200 appels (47,2 millions relus sur un contexte moyen d'environ 220 000 jetons), relecteur compris ; j'en compte 150 pour la conversation principale. Mener le lot suivant dans une conversation de C jetons, plutôt que dans une session neuve, relit donc (C − 70 000) × 150 jetons de plus :

| contexte à la fin d'un lot | surcoût du lot suivant |
| ---: | ---: |
| 150 000 | 1,1 point |
| 200 000 | 1,8 point |
| 300 000 | 3,1 points |

Changer de session coûte environ 0,9 point : 0,4 pour la reprise, mesurée ce matin (3 points de cinq heures), et 0,5 pour écrire la passation, estimé. Le changement paie donc dès environ 140 000 jetons pour un lot de 150 appels (175 000 si la passation coûte le double), et dès 270 000 pour un lot de 50.

**Ce que le seuil change.** Un lot coûte de 5 à 8 points de la semaine, et de 36 à 62 points de cinq heures : quand le lot suivant ne tient pas dans ce qui reste de la fenêtre de cinq heures, la session change déjà, et la suivante part à sa remise à zéro. Le seuil ne joue que si la fenêtre laisse la place. Des trois sessions mesurées, une seule a fini entre 150 000 et 300 000 jetons : la clôture de L-0043, à 294 000, dont le lot suivant commençait par une question pour toi ; sans elle, il se serait mené dans cette conversation, pour environ 3 points de plus. Hors des jetons, chaque changement te demande un « reprends », et prend quelques minutes à l'agent, dont six ce matin pour pousser son premier commit. La session neuve ne sait que ce que la mémoire porte, mais la règle ne joue qu'à la fin d'un lot, quand tout est commité. Non mesuré : si une conversation longue dégrade le travail.

## Éléments cités

- B-0355@7cab6e0f — le besoin : fonder sur une mesure de l'usage le seuil qui fait changer de session.
- T-0193@5232e7ad — la tâche : te proposer ce seuil sur les mesures déjà prises.
- D-0194@a16d6581 — la réforme de l'organisation du 25 novembre, qui a posé le seuil de 300 000 jetons.
- D-0209@34904647 — les trois suggestions de la revue de cap 8 que tu as retenues, dont trancher ce seuil sans attendre.
- B-0356@269b8400 — le besoin en cours : la passation écrite avant la fusion de la pull request, pour qu'aucune branche de session ne te reste à supprimer.
- L-0041@96f53ba2 — le lot du 25 novembre : les copies des skills suivent leur gabarit sans validation.
- L-0043@819e4810 — le lot du 26 novembre : l'agent supprime ses branches déjà contenues.
- J-2026-11-25-AC@7df3a285 — la mesure de la session de L-0041.
- J-2026-11-26-I@39f2f773 — la mesure de la session de L-0043.
- J-2026-11-26-R@c50e70ee — la mesure de la session de la revue de cap 8.
- J-2026-11-26-S@dec7f1a6 — la mesure de cette reprise.
- C-0003@b3e65851 — ta consigne : l'atelier reste au prompt à copier, pour jongler entre tes comptes.

## Où regarder

- [Le coût d'un appel selon le contexte](https://github.com/theodubus/memory/blob/3cd2f5d01220ec60cc28a09e0a8851ebc322227f/docs/fabrication/consommation.md#L155-L167) : vérifier qu'il croît avec la taille de la conversation.
- [La règle à changer, dans le skill `socle-batch`](https://github.com/theodubus/memory/blob/3cd2f5d01220ec60cc28a09e0a8851ebc322227f/engine/socle/templates/skills/socle-batch/SKILL.md#L97-L103) : le seul chiffre qui bouge, avec sa copie dans le guide.

## Options

- **Baisser à 150 000.** Après un lot d'environ 150 appels, la session change presque toujours. Effort : un chiffre dans le skill, le guide, la page de l'organisation, les tests qui vérifient ce texte, et une note de version. Risque : un « reprends » de plus quand un lot finit entre 150 000 et 300 000 jetons. Réversible.
- **Garder 300 000.** Rien ne change dans le texte ; la mesure reste au journal. Un lot suivant mené au-delà de 150 000 jetons coûte de 1 à 3 points de plus. Réversible.
- **Retirer le seuil.** La session enchaîne tant que la fenêtre de cinq heures et la semaine le permettent, deux lots au plus sans ton message : moins de « reprends », mais un lot commencé vers 400 000 jetons coûte environ 4,5 points de plus. Réversible.
- **Les mesures ne tranchent pas.** 300 000 reste pour chess ; le besoin passe au jalon de la mesure en usage réel, qui vient après chess. Réversible.

Garder, dire que les mesures ne tranchent pas et refuser laissent tous trois 300 000 pour chess : ils ne diffèrent que par le sort du besoin, clos, reporté, ou laissé ouvert.

## Conséquences

Si tu valides, 150 000 s'écrit dans le skill `socle-batch`, le guide et la page de l'organisation, avec une note de version et les tests qui lisent ce texte ; chess le reçoit à sa mise à jour, et B-0355 se clôt. Si tu refuses, rien ne change, et je te demande ce qui manque. Sans réponse, le lot continue avec B-0356, et la mise à jour de chess attend ta réponse.

## Recommandation

Baisser à 150 000. Vérifié : les mesures des sessions, en points de la semaine et en jetons relus, et le coût d'un appel selon le contexte, mesuré le 12 novembre ; le coût de cette reprise. Supposé : la part de la relecture (59 %), mesurée sur Fable et reportée sur Opus 5.5 ; les 150 appels d'un lot, déduits des jetons relus ; le coût d'écriture d'une passation ; l'effet d'une longue conversation sur la qualité, non mesuré.

## Réponses possibles

- `valider` — le seuil passe à 150 000 jetons, dans le skill, le guide et la note de version ; B-0355 se clôt.
- `garder` — le seuil reste à 300 000 jetons, fondé sur ces mesures ; B-0355 se clôt.
- `retirer` — plus de seuil de contexte : seuls la fenêtre et les deux lots sans ton message bornent l'enchaînement ; B-0355 se clôt.
- `ne-tranchent-pas` — 300 000 reste pour chess ; B-0355 passe au jalon de la mesure en usage réel.
- `refuser` — rien ne change, et je te demande ce qui manque.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
