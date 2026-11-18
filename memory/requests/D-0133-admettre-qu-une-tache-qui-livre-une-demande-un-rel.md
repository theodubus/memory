<!-- socle: couche=demandes zone=publique -->
# D-0133 — Admettre qu'une tâche qui livre une demande, un relevé ou une entrée de la mémoire se vérifie par ce qu'elle produit, et non par un test

> date : 2026-11-18

## Décision demandée

Admettre qu'une case du critère d'une tâche dont le livrable est une demande posée, un relevé écrit ou une entrée de la mémoire récrite se vérifie par ce qu'elle produit, que la case nomme, et non par un test ; tout autre livrable garde son test.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code entretenu par un agent d'IA : il garde la mémoire du projet (des décisions, un journal daté de ce qui s'est passé, et le backlog, la liste du travail à faire), vérifie ce que l'agent produit, et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Le hook, l'un de ses programmes, refuse à l'agent, avant qu'elle ait lieu, une action que la politique du projet interdit. Chess, votre jeu d'échecs, est le projet pilote.

**Le chantier.** Le 16 novembre, vous avez validé un backlog en quatre formes : le besoin (`B-`), un défaut à corriger ou une fonction à ajouter, dont le critère, « Satisfait quand », dit un résultat ; la tâche (`T-`), un livrable fait en un commit, dont le critère, « Fait quand », une liste de cases à cocher, « se vérifie par des tests, ou, pour une action que vous seul pouvez faire, par ce qu'elle produit » ; le lot (`L-`), des tâches menées et relues ensemble ; le jalon (`JA-`), des besoins qui servent un même but. Le lot en cours, L-0014, a découpé en tâches les besoins du jalon en cours, le travail à finir avant toute fonction nouvelle, et récrit leurs critères.

**La question.** Le relecteur sans contexte du lot, un autre agent chargé de le prendre en défaut, a relevé que dix de ces tâches ont une case qu'aucun test ne peut vérifier, alors que la tâche qui les a écrites, T-0049, disait les critères de toutes « des livrables qu'un test vérifie ». L'exception de votre règle ne les couvre pas : elle vise une tâche marquée comme la vôtre, que vous seul faites ; poser une demande, écrire un relevé ou récrire le backlog, c'est l'agent qui le fait, et votre réponse à une demande n'en est qu'une suite. Il faut soit étendre l'exception, soit récrire ces tâches.

**L'exception proposée.** Elle vaut case par case, pour trois livrables, et pour eux seuls : une demande posée, vérifiée par la demande et votre réponse consignée au journal ; un relevé, le compte rendu écrit d'une mesure ou d'un essai, vérifié par son fichier dans le dépôt ; une entrée de la mémoire récrite (une case du backlog, une décision), vérifiée par ce qu'en montre une commande du socle (`socle show`, qui affiche une entrée, ou `socle roadmap`, la suite du projet). Le code, la documentation du produit, ses gabarits, une spécification gardent leur test. Qu'un relevé dise vrai, aucun test ne le juge, aujourd'hui non plus : c'est le relecteur sans contexte de chaque lot, qui juge le lot contre ses critères, et, pour une demande, vous.

**Les dix tâches**, chacune avec la case visée ; leurs autres cases, quand elles livrent du code, ont leur test.

- Cinq posent une demande et consignent votre réponse, par exemple T-0008 : « une demande soumet à Théo la spécification et le modèle de menace, et sa réponse est consignée au journal ». Les autres : T-0016, T-0039, T-0043, T-0080.
- Quatre écrivent un relevé, par exemple T-0023 : « le relevé dit, pour chacun des trois effets, la couche qui le rattrape, ou qu'aucune ne le fait ». Les autres : T-0041, T-0077, et la première case de T-0034.
- Une fait dire au journal un compte, combien de citations un changement rend périmées : la seconde case de T-0021, un correctif dont la première case a son test.

Votre réponse vaut aussi pour les cases de ces trois formes ailleurs dans le backlog, dont T-0061, d'un lot suivant (« une décision remplace » une autre), et deux tâches que la revue vient d'ouvrir, qui ne récrivent que le backlog, T-0084 et T-0086. La case de T-0049, avant la revue « …et ceux de leurs tâches des livrables qu'un test vérifie », dit désormais, en plus, cette exception et qu'elle vous est soumise ici.

## Éléments cités


Plus bas : `D-`, une demande comme celle-ci ; après @, l'empreinte de la version lue.

- D-0123@61a56e15 — votre validation du 16 novembre de la structure du backlog, dont la règle des critères d'une tâche.
- L-0014@cd0d35b8 — le lot en cours, avec l'historique de sa revue.
- T-0049@22b86335 — la tâche qui a découpé les besoins, dont la case dit maintenant l'exception soumise ici.
- T-0061@8988f16a — le précédent : une tâche d'un lot suivant dont un critère est une décision.
- T-0084@40b78cf0 — une tâche ouverte par la revue, qui ne récrit que le backlog : la remise des copies protégées.
- T-0086@b3eb3b75 — une tâche ouverte par la revue, qui ne récrit que le backlog : une condition de votre réponse d'octobre.
- T-0008@9bed4dbc — une demande sur une action externe validée que le hook laisse passer une fois.
- T-0016@d31fccd7 — une demande sur la tolérance d'un test poussé sous sa demande.
- T-0039@8705e56c — une demande sur la solution du contexte long, avec la mesure de ses essais.
- T-0043@84088b95 — une demande sur deux cas de la reprise après une limite d'usage.
- T-0080@a1e4a47d — une demande sur la spécification de la passation programmée.
- T-0023@ed037ea2 — le relevé de ce qui rattrape un push forcé hors du hook.
- T-0041@7d2739e2 — l'essai de la passation programmée, son relevé puis sa demande.
- T-0077@42d93f82 — le balayage de mutation du socle mesuré contre celui de chess.
- T-0034@51f6067d — la mesure de ce que lit le relecteur à froid d'une demande.
- T-0021@4352c323 — un correctif du lecteur des titres, dont une case est un compte au journal.

## Où regarder

- [Votre validation du 16 novembre](https://github.com/theodubus/memory/blob/28755ed989c8807f3fab1743b89e4ab72dbd6ded/memory/requests/D-0123-valider-la-specification-de-la-structure-du-backlo.md) : le point 1 de la spécification, la phrase sur le critère d'une tâche.

## Options

- Valider : effort nul pour les treize tâches ; l'exception s'écrit dans une décision de ce dépôt, puis une phrase du format de la mémoire, que lisent les agents des projets installés, chess compris, la dit, avec sa note de version ; rien n'y change pour vous. Risque faible : chaque case reste jugée, par sa revue ou par vous. Réversible par une demande nouvelle.
- Refuser : les treize tâches se récrivent, en un commit du backlog au prochain lot ; une demande devient ce qu'un besoin attend avant ses tâches, posée quand il est pris, et un relevé, une étape d'une tâche qui livre du code et son test. Le jalon n'en prend pas de retard sensible. Réversible.

## Conséquences

Si vous validez : l'agent écrit l'exception dans une décision qui complète votre spécification du 16 novembre, ouvre la tâche qui la porte dans le format de la mémoire, et le lot se clôt avec vos deux réponses, à celle-ci et à la demande posée en même temps, sur le changement de neuf tests et de trois copies protégées. Si vous refusez : la case de T-0049 redevient fausse, une tâche récrit les treize, et le lot attend qu'elle soit faite. Sans réponse : le lot reste ouvert sur sa branche.

## Recommandation

Valider. Vérifié : les dix tâches et leurs cases, relues une à une ; aucun test ne peut juger qu'une demande vous a été posée ou qu'un relevé dit vrai ; le contrôle des demandes juge déjà leur forme, et la revue de chaque lot leur fond. Supposé : qu'aucune de ces cases ne cache du code qu'un test devrait juger.

## Réponses possibles

- `valider` — l'exception s'écrit, et les treize tâches restent telles quelles.
- `refuser` — les treize tâches se récrivent pour qu'un test les vérifie, ou se changent en attentes.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
