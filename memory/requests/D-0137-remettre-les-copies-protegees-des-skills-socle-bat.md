<!-- socle: couche=demandes zone=publique -->
# D-0137 — Remettre les copies protégées des skills socle-batch, socle-review et socle-request au texte de leurs gabarits, que les allégements du 18 novembre ont changés

> date : 2026-11-19

## Décision demandée

Autoriser l'agent à remettre les copies protégées de ce dépôt des skills `socle-batch`, `socle-review` et `socle-request` au texte exact de leurs gabarits, qui portent depuis cette nuit les allégements que vous avez validés le 18 novembre.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code entretenu par un agent d'IA : il garde la mémoire du projet (ses décisions, son journal, son backlog, la liste du travail à faire), vérifie ce que l'agent produit, et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, est le projet pilote.

**Le chantier.** Le 18 novembre, vous avez validé cinq allégements de la façon dont l'agent mène un lot (des tâches menées et relues ensemble), pour qu'il consomme moins des deux limites d'usage de votre abonnement, l'une sur une fenêtre de cinq heures, l'autre sur la semaine : (1) un circuit court pour les petits lots ; (2) des valeurs attendues de tests changées mécaniquement, validées par une simple question dans la conversation ; (3) le hook de fin de tour, le programme qui contrôle chaque fin de tour de l'agent, qui ne recopie plus toute la sortie des tests en échec ; (4) une décision prise dans la conversation qui garde le texte qu'elle approuve ; (5) le coût d'un lot estimé avant son lancement. Vous les avez validés tels quels, le premier sous une condition, que des sous-agents (d'autres agents, lancés par celui qui mène le lot) restent utiles pour implémenter, à laquelle l'agent a répondu oui. Le lot L-0018 les a écrits dans le produit cette nuit ; un relecteur sans contexte, un autre agent chargé de le prendre en défaut, l'a relu, et il est fusionné. Juste avant, le lot L-0016, la vue de la suite du projet (`socle roadmap`), avait précisé une phrase de `socle-batch`.

**La question.** Un skill est une procédure écrite que l'agent charge quand elle sert. Chacun a deux textes : le gabarit, que le produit installe dans chaque projet (chess le recevra à sa mise à jour, quelle que soit votre réponse), et, dans ce dépôt, une copie, celle que charge l'agent d'ici, protégée pour qu'il ne récrive pas ses propres règles : seul votre accord la change. Les trois copies ont le texte de votre dernier accord, le 18 novembre en fin d'après-midi. La proposition 3 ne touche aucun skill ; le workflow de la CI (les vérifications que GitHub lance à chaque envoi), l'autre copie protégée remise ce jour-là, est à jour.

**Ce qui change**, de chaque copie à son gabarit.

`socle-batch`, la conduite d'un lot :

- une petite tâche, moins de 150 lignes de code et de tests (le chiffre de la proposition 1 ; provisoire, à mesurer), s'implémente dans la session qui mène le lot, sans sous-agent, sauf si elle touche un garde-fou (une règle que le socle fait respecter, déclarée dans un réglage que vous seul assouplissez) ou un format que d'autres parties du projet lisent ; avant, seul « un changement de quelques lignes » ;
- à l'annonce, le coût du lot s'estime ; s'il ne tient pas dans ce qui reste de la fenêtre de cinq heures, le lot se découpe, commence plus petit ou attend la remise à zéro de la fenêtre ;
- les coûts se mesurent, et la clôture du lot les note au journal ; un sous-agent se lance si ce qui reste de chaque limite couvre son coût mesuré et le rangement (tout pousser et écrire la mémoire, pour qu'une session neuve reprenne) ; les seuils fixes (85 % de la semaine, 60 % de la fenêtre) ne valent plus que sans mesure ; le rangement commence au plus tard à dix points d'une limite ;
- le compte rendu de la clôture colle la suite du projet « dans un bloc de code » (L-0016) ;
- le texte est resserré pour tenir sous le plafond de 8 000 octets que les garde-fous fixent à un skill : il ne retire que des redites (la ligne sur une attente de plus d'une heure, que deux autres sections disent) et des incises ; trois règles que le premier resserrement avait perdues, relevées par le relecteur, sont rendues : un sous-agent arrêté plus de cinq minutes ne se reprend pas ; près d'une limite, une tâche qui demande plus de réflexion se commence quand même ; un sous-agent qui ne peut recevoir la dernière version de son modèle se dit à l'humain.

`socle-review`, la conduite de la revue :

- un petit lot, moins de 150 lignes de code et de tests en tout, qui ne touche ni un garde-fou ni un format lu ailleurs, reçoit le dossier court (`socle review --short`) : le diff et les critères de ses tâches, que le relecteur juge sans explorer au-delà des fichiers touchés ; l'outil le refuse pour un lot qui touche un fichier protégé ou déclaré par les garde-fous ; tout autre lot garde le dossier complet, qui donne aussi les entrées du backlog et les décisions qu'elles citent ;
- le dossier donne aussi le fichier qu'approuve une décision prise dans la conversation ;
- resserré sous le même plafond ; le détail de ce que le relecteur peut écrire (un dossier temporaire, par son chemin écrit en toutes lettres) n'est plus que dans la consigne en tête du dossier, qu'il reçoit.

`socle-request`, les demandes :

- un contenu que vous validez dans la conversation (un format, un exemple, un texte) s'écrit d'abord dans le dépôt ; la décision le désigne, et les tâches qui en découlent le citent ;
- la variante légère : pour des valeurs attendues changées mécaniquement, des tests qui lisent un format que vous venez de valider, une question dans la conversation qui nomme chaque test, avec sa valeur avant et après, et votre réponse consignée mot pour mot ; tout autre changement de valeur attendue, ou suppression d'un test, garde la demande écrite.

**L'effet de votre réponse.** `delegate-lot`, le skill propre à ce dépôt qui complète `socle-batch`, n'est pas protégé : l'agent le tient seul. Il a reçu cette nuit deux de ces règles, que vous avez validées : le circuit court et la variante légère. Si vous validez, le reste prend effet ici aussi : l'estimation et la mesure des coûts, les seuils qui en dépendent, le dossier court, le contenu validé écrit dans le dépôt. Si vous refusez, ce reste ne s'applique pas dans ce dépôt, et sur les deux règles où les copies contredisent `delegate-lot`, l'agent suit `delegate-lot`, qui porte votre accord le plus récent.

L'installeur, relancé pour poser ces copies, change aussi deux lignes, sans rapport avec ces skills, de la section du socle d'`AGENTS.md`, le fichier d'instructions de l'agent ; non protégée, elle dépasserait alors le plafond de 16 000 octets que les garde-fous fixent à ce fichier : elle reste telle quelle, comme le 18 novembre, jusqu'à la tâche T-0069. Le lot suivant, L-0015, changera encore le gabarit de `socle-review` : sa copie suivra par une demande à la fin de ce lot.

## Éléments cités

- .claude/skills/socle-batch/SKILL.md sha256:6207b6c8d4475971
- .claude/skills/socle-review/SKILL.md sha256:3fe6c31bb11bdb47
- .claude/skills/socle-request/SKILL.md sha256:097ebdc7997f3668

L'empreinte de ces trois lignes est celle que la copie aura, celle de son gabarit : votre accord porte sur ce texte exact. Plus bas : `D-`, une demande comme celle-ci ; `L-`, un lot ; `B-`, un besoin, un résultat à atteindre ; `T-`, une tâche, le livrable d'un commit qui sert un besoin ; après @, l'empreinte de la version lue.

- D-0134@a3f8bf61 — votre validation du 18 novembre des cinq allégements.
- D-0132@d55e4442 — votre accord du 18 novembre qui a remis ces copies pour la dernière fois, avec le workflow de la CI.
- L-0018@372bba8b — le lot clos qui a écrit les allégements dans les gabarits, avec sa revue.
- L-0016@51c4561a — le lot clos de la vue de la suite, qui a changé une phrase de `socle-batch`.
- B-0218@fd498240 — le besoin des copies protégées en retard sur leurs gabarits, qu'aucune vérification du socle ne signale.
- T-0072@f84a75da — la tâche qui remettra toutes les copies en retard, à la fin du lot L-0006@c60c9481, sans date : deux lots passent avant lui.
- T-0069@92a4d3a7 — la tâche qui remettra la section du socle d'`AGENTS.md` sur son gabarit, une fois le fichier resserré.
- L-0015@e1d85670 — le lot suivant, qui touche la revue et le gabarit de `socle-review`.

## Où regarder

- [Les cinq allégements et votre réponse](https://github.com/theodubus/memory/blob/d4d66ac0e3275633bbbcdbafcaa1e9e1dfdf4e95/docs/fabrication/allegements.md) : les propositions 1, 2, 4 et 5, que ces textes mettent en œuvre.
- Le texte nouveau, les gabarits : [`socle-batch`](https://github.com/theodubus/memory/blob/d4d66ac0e3275633bbbcdbafcaa1e9e1dfdf4e95/engine/socle/templates/skills/socle-batch/SKILL.md), [`socle-review`](https://github.com/theodubus/memory/blob/d4d66ac0e3275633bbbcdbafcaa1e9e1dfdf4e95/engine/socle/templates/skills/socle-review/SKILL.md), [`socle-request`](https://github.com/theodubus/memory/blob/d4d66ac0e3275633bbbcdbafcaa1e9e1dfdf4e95/engine/socle/templates/skills/socle-request/SKILL.md) (la fin, « Consigner une décision prise en séance »).
- Les copies actuelles, à remplacer : [`socle-batch`](https://github.com/theodubus/memory/blob/d4d66ac0e3275633bbbcdbafcaa1e9e1dfdf4e95/.claude/skills/socle-batch/SKILL.md), [`socle-review`](https://github.com/theodubus/memory/blob/d4d66ac0e3275633bbbcdbafcaa1e9e1dfdf4e95/.claude/skills/socle-review/SKILL.md), [`socle-request`](https://github.com/theodubus/memory/blob/d4d66ac0e3275633bbbcdbafcaa1e9e1dfdf4e95/.claude/skills/socle-request/SKILL.md).

## Options

- Valider : les trois copies deviennent leurs gabarits, octet pour octet ; effort faible ; risque faible, ce sont les textes relus et fusionnés que chess recevra ; réversible par une demande nouvelle.
- Refuser : les copies gardent le texte du 18 novembre jusqu'à T-0072 ; effort nul ; réversible.

## Conséquences

Si vous validez : l'agent pose les trois copies par l'installeur, sans `AGENTS.md`, et les commite avec votre réponse dans un même push ; il mène ensuite le lot L-0015 avec ces règles. Si vous refusez : rien ne change dans ce dépôt, et l'agent mène L-0015 comme le dit « L'effet de votre réponse ». Sans réponse : de même, la demande restant en attente.

## Recommandation

Valider. Vérifié : les empreintes citées sont celles des fichiers que l'installeur pose, relancé dans un clone jetable de ce dépôt, identiques octet pour octet aux gabarits ; les différences sont celles dites plus haut, lues dans le diff de chaque copie à son gabarit ; la consigne du dossier de la revue dit bien le dossier temporaire écrit en toutes lettres ; les deux lignes d'`AGENTS.md` ne touchent pas ces skills. Supposé : rien.

## Réponses possibles

- `valider` — les trois copies deviennent leurs gabarits, avec votre réponse dans le même push.
- `refuser` — les copies restent telles quelles jusqu'à la remise de toutes les copies.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
