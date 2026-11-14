<!-- socle: couche=demandes zone=publique -->
# D-0114 — Poser la copie protégée du skill socle-batch et changer deux valeurs attendues de tests/test_skills.py, qui comptent les skills du socle

> date : 2026-11-14

## Décision demandée

Autoriser l'agent à poser dans ce dépôt la copie protégée du skill nouveau `socle-batch`, identique à son gabarit, et à changer les deux valeurs attendues de `tests/test_skills.py` qui listent les skills que le socle pose, pour qu'elles le nomment : les deux vont ensemble, l'un sans l'autre fait échouer ces tests.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui rend fiables la mémoire, la documentation et les tests d'un projet de code entretenu par un agent d'IA. Le moteur, « le produit », est ce qu'un projet reçoit à l'installation ; ce dépôt s'en sert lui-même, comme premier projet équipé.

**Le chantier.** Avant de revenir aux nouvelles fonctions du produit, l'agent finit une liste de sujets du backlog (la liste des sujets à traiter, chacun nommé B-NNNN) que vous avez fixée le 13 novembre, en six lots : quelques sujets menés ensemble, relus par un autre agent sans contexte, puis fusionnés par une pull request. Le 13 novembre, vous avez demandé que tout ce qui est utile entre dans le produit ; le 14, que le socle apprenne à réunir les sujets qui se traitent ensemble. Le deuxième lot est relu et part aujourd'hui dans la pull request #49, sauf la part que cette demande couvre : il range les lots au backlog, chacun lié à ses sujets, et l'état (le résumé calculé à chaque démarrage) montre le prochain.

**La question.** La part qui reste fait de la procédure des lots un skill du produit, `socle-batch`. Un skill est une procédure écrite que l'agent charge quand il en a besoin ; celle-ci n'existait que dans ce dépôt, dans le skill `delegate-lot`. Le moteur garde de chaque skill un gabarit, le texte de référence qu'il recopie dans chaque projet ; dans le projet, la copie est protégée : l'agent ne la crée ni ne la modifie sans votre accord. Et deux tests figent la liste des skills que l'installeur (la commande du moteur qui pose ou met à jour ses fichiers dans un projet) pose ; la politique du projet vous réserve le changement d'une valeur qu'un test attend, pour qu'un agent n'affaiblisse pas un test afin de le faire passer.

Ce que dit le skill, en six parties : former un lot des sujets prêts (ceux dont les prérequis sont faits) qui touchent les mêmes fichiers, le même garde-fou (un contrôle ou un refus automatique) ou les mêmes tests, et le garder au backlog ; un sous-agent par sujet, deux à la fois au plus, chacun dans une copie isolée du dépôt ; la revue sans contexte avant tout envoi sur GitHub, dont seuls les défauts bloquants se corrigent dans le lot ; l'intégration, la CI (l'intégration continue sur GitHub, qui rejoue tous les contrôles) et la fusion, faite par l'humain sauf si les instructions du projet la confient à l'agent, comme ici ; le chantier actif et le journal écrits avant la fusion, rien envoyé après elle sans travail neuf (cela recréait une branche que GitHub venait de supprimer) ; les seuils de l'usage de l'abonnement de l'agent : un seul sous-agent au-delà de 75 % du quota de la semaine, aucun au-delà de 85 % de la semaine, ou de 60 % de la fenêtre de cinq heures ; enfin le changement de session, le travail pas encore relu rangé en fichier correctif (un patch) dans le dépôt, avec le message qui lance la session suivante. Sans sous-agents, l'agent mène le lot seul, dans le même ordre. La revue a trouvé deux défauts bloquants, corrigés dans ce texte : la clôture du lot après la fusion, et, dans `delegate-lot` réduit, la perte de votre consigne du 12 novembre (une valeur attendue passe par une demande comme celle-ci, jamais par une question dans la conversation).

Le reste de la part, commité avec votre réponse : le gabarit du skill en français et en anglais ; `delegate-lot` réduit à ce qui est propre à ce dépôt (le modèle des agents, la fusion par l'agent, la publication du moteur, le prompt de mise à jour de chess, les mesures de consommation) ; le skill nommé dans les instructions que l'installeur pose ; son entrée dans les notes de version ; trois tests neufs du skill (posé, protégé, sans rien de ce dépôt) ; B-0199 clos.

Les deux valeurs. Dans `test_l_installeur_les_pose_et_la_politique_les_protege`, la liste attendue `["socle-private-memory", "socle-request", "socle-resume", "socle-review"]` devient `["socle-batch", "socle-private-memory", "socle-request", "socle-resume", "socle-review"]`. Dans `test_dans_les_deux_langues_ils_passent_leurs_controles`, la ligne attendue `skills du socle posés dans .claude/skills : socle-private-memory, socle-request, socle-resume, socle-review` devient `skills du socle posés dans .claude/skills : socle-batch, socle-private-memory, socle-request, socle-resume, socle-review`. Seul s'ajoute le nom du skill nouveau ; les tests restent aussi stricts.

## Éléments cités

- .claude/skills/socle-batch/SKILL.md sha256:0a03e52f59883f1d

Les identifiants : B-NNNN, un sujet du backlog ; ADR-NNNN, une décision de conception que l'agent écrit seul quand elle est réversible ; J-…, une entrée du journal ; le suffixe après @, l'empreinte de la version lue.

- B-0199@528031a5 — le sujet : la conduite d'un lot dans le produit ; ses trois critères (le skill posé et protégé, `delegate-lot` réduit, les lots dans la mémoire) sont tenus avec cette part.
- ADR-0079@d9cd58c2 — la décision de l'agent : un lot se garde au backlog comme un sujet qui attend ses sujets, et sa conduite est le skill `socle-batch`.
- ADR-0017@4ce8d68e — la décision qui réserve à l'humain le changement d'une valeur attendue dans un test.
- J-2026-11-14-X@95b2e546 — le compte rendu de la revue du lot : ses constats, leur classement et les deux corrections.
- #49 — la pull request ouverte de ce dépôt, qui porte le lot 2 relu, sans la part de cette demande.

La première ligne : le fichier à créer, et les seize premiers caractères de l'empreinte SHA-256 qu'il aura, celle du gabarit ; votre accord porte sur ce texte exact, que le premier lien donne en entier.

## Où regarder

- [Le skill, tel qu'il sera posé](https://github.com/theodubus/memory/blob/7406d6f2f45ec2a4a5c4baef662e8ee4bfd7eb5e/docs/fabrication/passation/2026-11-14-lot-2/socle-batch-SKILL.md) : son texte entier ; vérifier qu'il dit la procédure telle que vous la voulez pour tout projet.
- [Les deux tests](https://github.com/theodubus/memory/blob/7406d6f2f45ec2a4a5c4baef662e8ee4bfd7eb5e/tests/test_skills.py#L121-L150) : les deux valeurs recopiées plus haut.
- [La passation du lot](https://github.com/theodubus/memory/blob/7406d6f2f45ec2a4a5c4baef662e8ee4bfd7eb5e/docs/fabrication/passation/2026-11-14-lot-2/README.md) : la part en attente, en correctif, et ce que l'agent fera après votre réponse.

## Options

- Valider : le skill est posé ici, et dans tout projet à sa prochaine installation ou mise à jour du socle ; ce dépôt suit la procédure de son produit. Effort : une demi-heure d'agent, surtout les vérifications. Risque faible : le texte est relu et ses tests passent. Réversible : une nouvelle demande retire la copie et rétablit les valeurs ; aucun autre projet ne le reçoit avant la mise à jour de chess, le seul projet équipé, prévue une fois les six lots finis.
- Refuser : le skill reste hors du produit ; `delegate-lot` garde la procédure entière pour ce dépôt seul, et ADR-0079 est remplacée par une décision qui garde la conduite des lots propre à ce dépôt. Effort nul ; un projet équipé n'a pas de procédure de lot. Réversible : la demande peut se reposer.

## Conséquences

Si vous validez : l'agent commite la part en attente, pose la copie par l'installeur, change les deux valeurs, et envoie votre réponse avec ce changement, dans le même push : la CI ne compte une validation que dans le push qui la porte. B-0199 se clôt et le lot 2 est fini. Si vous refusez : rien de cette part n'est commité, et la pull request #49, déjà relue, n'en dépend pas ; l'agent ouvre un sujet selon la raison de votre refus, que vous pouvez dire dans la conversation. Sans réponse : la part attend en correctif dans le dépôt, et l'agent passe au lot suivant.

## Recommandation

Valider. Vérifié : avec cette part, seuls ces deux tests échouent, et sur ces deux valeurs ; l'empreinte citée est celle du gabarit relu et corrigé ; la revue sans contexte est faite. Supposé : que la procédure servira aux projets équipés comme à ce dépôt, où elle mène les lots depuis le 11 novembre.

## Réponses possibles

Répondez dans la conversation par l'un de ces mots ; l'agent consigne votre texte exact.

- `valider` — l'agent pose la copie, change les deux valeurs et envoie votre réponse avec ce changement.
- `refuser` — rien n'est posé ; l'agent ouvre un sujet selon la raison de votre refus.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
