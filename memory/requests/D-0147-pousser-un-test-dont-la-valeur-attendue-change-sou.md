<!-- socle: couche=demandes zone=publique -->
# D-0147 — Pousser un test dont la valeur attendue change sous sa demande en attente, la CI le refusant jusqu'à la réponse, comme un fichier protégé ?

> date : 2026-11-20

## Décision demandée

Un test supprimé, ou dont la valeur attendue change, peut-il se commiter et se pousser dès que la demande qui le nomme est poussée, la CI restant rouge jusqu'à votre réponse, comme on le fait déjà pour un fichier protégé, au lieu de rester non commité dans le conteneur de l'agent ?

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui rend fiables la mémoire, la documentation et les tests d'un projet tenu par un agent de code, et qui ne laisse à l'humain que ce qu'aucun contrôle ne tranche. Les projets qui l'installent reçoivent aussi ce changement.

**Le chantier.** Le lot en cours, L-0006, travaille sur les skills (les fichiers de procédure que l'agent charge, comme « mener un lot » ou « faire relire un lot ») et sur leurs copies protégées : le socle pose ces skills dans chaque projet, et la copie posée ne change qu'avec votre accord. Une des tâches du lot soumet cette question, relevée le 9 novembre : vous vous étiez inquiété qu'un travail qui attend votre réponse ne vive que dans le conteneur de la session, perdu si celui-ci est recyclé. Le 2 novembre, vous avez accepté une tolérance de ce genre pour les fichiers protégés.

**La question.** Deux tâches du lot retirent du texte et du code : le recul des revues (le paragraphe de réflexion obligatoire avant chaque passe de revue de plus, que vous avez fait retirer le 20 novembre), et la procédure qui faisait relever les formes rares de commandes que le hook de l'agent ne juge pas. Des tests qui fixaient l'ancien texte devront donc être supprimés ou changés. Rien n'est bloqué sans votre réponse : la question est où ces tests attendent la vôtre.

Le détail. Le socle refuse qu'un test soit supprimé ou que sa valeur attendue change (la valeur que le test compare au résultat) sans une demande que vous avez validée et qui nomme ce test. Ce contrôle s'appelle `tests.attendus`. Il est vérifié au commit, au push et en CI ; il l'est aussi quand l'agent finit son tour, c'est-à-dire sa réponse. Aujourd'hui, une demande en attente qui nomme le test ne tolère le changement qu'à ce dernier moment : l'agent peut finir sa réponse avec le test changé dans ses fichiers de travail, non commités. Le commit et le push le refusent, donc le changement ne quitte pas le conteneur.

Ce que vous voyez aujourd'hui : la demande nomme chaque test, avec sa valeur avant et après, mais le code changé n'est pas sur GitHub ; vous validez sur ce texte. Si le conteneur est recyclé (il l'est après une période d'inactivité, ou à la fin de la session), le changement est perdu et refait. Pour l'éviter, l'agent range parfois un correctif dans le dépôt, un fichier texte qui décrit le changement, sous un dossier de passation : le contrôle ne juge pas ce fichier, qui n'est pas un test, mais il faut le réappliquer à la main.

La règle du 2 novembre, écrite pour les fichiers protégés qu'une mise à jour du socle change, vaut dans le code pour tout fichier protégé qu'une demande en attente cite avec son empreinte nouvelle (un court code qui identifie la version exacte d'un fichier). Ce fichier se commite et se pousse, et la CI le refuse jusqu'à votre réponse. La demande doit être poussée telle quelle : une demande modifiée après coup ne compte plus. La tolérance ne joue que si la branche par défaut exige la CI du socle avant toute fusion, ce qui est le cas ici : une pull request rouge ne peut pas entrer dans `main`. La proposition est d'appliquer exactement cette règle aux tests, avec la même condition. Vous liriez alors les tests changés dans la pull request, ligne à ligne.

## Éléments cités

Chaque renvoi porte le numéro de l'entrée (B- un besoin, D- une décision, T- une tâche, F- un fait mesuré, L- un lot), suivi de l'empreinte de la version lue.

- B-0140@e83fa00e — le besoin : un changement qui attend une demande ne peut ni se commiter ni se pousser, il ne vit que dans le conteneur, perdu s'il est recyclé.
- D-0071@9b06b40c — votre décision du 2 novembre : les fichiers protégés qu'une mise à jour change se commitent et se poussent sous leur demande en attente, la CI les refusant jusqu'à la réponse.
- T-0016@d31fccd7 — la tâche qui vous soumet cette question.
- T-0075@5229ca33 — la tâche qui l'implémentera si vous validez : le contrôle des valeurs attendues au commit, au push et en CI, avec un essai qui prouve qu'il refuse toujours sans demande ; abandonnée si vous refusez.
- F-0009@aa253eaa — le fait mesuré : GitHub refuse de fusionner dans `main` une pull request dont la CI du socle échoue.
- L-0006@7bbb0f14 — le lot en cours, dont deux tâches changent des tests.
- D-0144@3ca5d3d1 — votre décision du 20 novembre qui retire le recul des revues.
- T-0110@0a0a78de et T-0060@4ff7dafb — les deux tâches du lot qui suppriment ou changent des tests.

## Où regarder

- [La tolérance actuelle des tests](https://github.com/theodubus/memory/blob/1ebfb5e8386eed2b407d85dd461dafc6a642c6da/engine/socle/checks_tests.py#L192-L205) : elle ne joue qu'à la fin de la réponse de l'agent ; vérifier que le commit et la CI le refusent toujours.
- [La tolérance des fichiers protégés](https://github.com/theodubus/memory/blob/1ebfb5e8386eed2b407d85dd461dafc6a642c6da/engine/socle/checks_ratchet.py#L311-L332) : quand elle est appelée pour un commit, elle laisse commiter et pousser si la branche par défaut exige la CI, qui refuse jusqu'à la réponse ; c'est la règle proposée pour les tests.
- [B-0140](https://github.com/theodubus/memory/blob/1ebfb5e8386eed2b407d85dd461dafc6a642c6da/memory/backlog/B-0140-un-changement-qui-attend-une-demande-ne-peut-ni-se.md) : le besoin et sa piste.

## Options

- **Valider : la même tolérance que pour les fichiers protégés.** Un test nommé par une demande en attente, poussée telle quelle, se commite et se pousse ; la CI reste rouge jusqu'à votre réponse. Effort : une tâche de code, petite, qui réutilise le mécanisme du 2 novembre. Risque : un test changé par l'agent arrive sur la branche de travail avant votre réponse ; il n'entre pas dans `main`, la fusion étant bloquée tant que la CI est rouge, et l'agent ne fusionne jamais une pull request rouge. Pendant l'attente, toute la pull request est rouge et ne peut pas se fusionner, avec le reste du travail qu'elle porte, comme sous une demande de fichiers protégés ; le rapport de la CI nomme chaque contrôle qui échoue et chaque fichier en faute, si bien qu'un autre échec reste visible à côté de celui qui attend. Réversible : la tolérance se retire par une tâche.
- **Refuser : garder le chemin actuel.** Le test changé reste non commité jusqu'à votre réponse ; vous validez sur le texte de la demande, qui donne chaque valeur avant et après. Effort : aucun. Risque : un recyclage du conteneur perd le changement, que l'agent refait, ou qu'une session neuve reprend d'un correctif rangé dans le dépôt. Réversible.

## Conséquences

Si vous validez : T-0075 implémente la tolérance dans ce lot, avec sa note de version pour les projets installés. À la fin du lot, une seule demande nommera chaque test que T-0110 et T-0060 suppriment ou changent, avec sa valeur avant et après, et les copies protégées à remettre ; ces tests se pousseront sous elle, et vous les lirez dans la pull request. Si vous refusez : T-0075 s'abandonne, la raison s'écrit dans B-0140, et la même demande de fin de lot vous sera posée, les tests attendant dans le conteneur. Sans réponse : rien ne change, le lot avance, et T-0075 attend.

## Recommandation

Valider. Vérifié : la tolérance des fichiers protégés existe et joue sous la même condition (le code cité plus haut) ; la branche par défaut de ce dépôt exige la CI du socle avant fusion (l'état calculé du projet le dit) ; GitHub refuse une pull request rouge (F-0009). Supposé : le coût de T-0075, une petite tâche, puisqu'elle reprend un mécanisme existant ; et que la pull request rouge pendant l'attente ne gêne pas davantage qu'aujourd'hui sous une demande de fichiers protégés.

## Réponses possibles

- `valider` — la tolérance s'applique aux tests ; T-0075 l'implémente dans le lot L-0006.
- `refuser` — le chemin actuel reste ; T-0075 s'abandonne et B-0140 écrit pourquoi.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
