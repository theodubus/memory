<!-- socle: couche=decisions zone=publique -->
# ADR-0088 — Une case du critère d'une tâche qui livre une demande posée, un relevé écrit ou une entrée de la mémoire récrite se vérifie par ce qu'elle produit, non par un test

> statut : acceptée · date : 2026-11-18 · source : D-0133@51dbb960, D-0123@61a56e15, ADR-0083@512e719c, J-2026-11-18-M@dbca1fb1, L-0014@cd0d35b8, T-0049@22b86335, T-0061@8988f16a, T-0084@40b78cf0, T-0086@b3eb3b75, T-0087@d4ffd952 · lu : decisions@1d692f46

## Contexte

La spécification du backlog que Théo a validée le 16 novembre
(D-0123@61a56e15, point 1 ; ADR-0083@512e719c) dit que le « Fait quand »
d'une tâche se vérifie par des tests, ou, pour une action que seul
l'humain peut faire, par ce qu'elle produit. La revue du lot L-0014 a
relevé dix tâches dont une case livre une demande, un relevé ou un
compte au journal, qu'aucun test ne peut vérifier. D-0133@51dbb960 lui a
soumis une exception ; il l'a validée le 18 novembre (J-2026-11-18-M).

## Décision

La règle des critères d'une tâche vaut case par case. Une case dont le
livrable est l'un de ces trois se vérifie par ce qu'il produit, que la
case nomme :

- une demande posée : la demande, et la réponse de l'humain consignée au
  journal ;
- un relevé, le compte rendu écrit d'une mesure ou d'un essai : son
  fichier dans le dépôt ;
- une entrée de la mémoire récrite (une case du backlog, une décision) :
  ce qu'en montre une commande du socle (`socle show`, `socle roadmap`).

Tout autre livrable, le code, la documentation du produit, ses gabarits,
une spécification, garde son test. Qu'un tel livrable dise vrai, le
relecteur sans contexte de son lot le juge contre la case ; une demande,
l'humain.

## Conséquences

- Les treize tâches que vise D-0133, dont T-0049, T-0061, T-0084 et
  T-0086, restent telles quelles.
- T-0087 porte l'exception dans le format de la mémoire, que lisent les
  agents des projets installés, et dans la consigne du relecteur, avec sa
  note de version.
- Pour défaire : une demande nouvelle, puis une ADR qui la remplace.
