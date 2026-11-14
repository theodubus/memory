<!-- socle: couche=demandes zone=publique -->
# D-0112 — Écrire dans le produit les deux règles qui bornent le backlog : le tri des remarques non bloquantes de la revue, et la limite du hook de l'agent

> date : 2026-11-14

## Décision demandée

Autoriser l'agent à écrire, dans le moteur que reçoit chaque projet, les deux règles ci-dessous, qui disent quels constats d'une revue et quels trous du hook de l'agent méritent un sujet du backlog ; l'une, l'autre, ou les deux.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui rend fiables la mémoire (les faits, décisions et sujets que l'agent écrit dans le dépôt), la documentation et les tests d'un projet de code entretenu par un agent d'IA. Un projet le reçoit à l'installation, puis à chaque mise à jour ; chess, votre jeu d'échecs, en est équipé, et ce dépôt s'en sert lui-même.

**Le chantier.** Le 14 novembre, vous avez remarqué que le backlog (la liste des sujets à traiter) grossissait plus vite qu'il ne se vidait : 79 sujets ouverts pour 36 fermés du 9 au 14 novembre, contre un solde à peu près nul les semaines d'avant. Deux sources ne s'arrêtent pas seules : les remarques non bloquantes des revues, et les trous du hook de l'agent.

**La question.** Le même jour, dans la conversation, vous avez validé le principe pour les revues : garder au backlog les remarques importantes, écarter les exotiques (votre décision D-0111) ; trois sujets ont été fermés et quatre réduits à leurs points importants. Ce principe ne vaut encore que dans ce dépôt. Vous avez demandé que les deux règles s'écrivent dans le produit, pour qu'elles valent dans chaque projet ; il faut votre accord parce que la règle 1 change celle que vous aviez fixée le 13 novembre (D-0109), et que la règle 2 fixe ce que le hook a le droit de laisser passer.

Les termes. La **revue** : avant de livrer un lot de travail (quelques sujets faits ensemble), l'agent le fait relire par un autre agent sans son contexte, qui cherche à le prendre en défaut ; un constat **bloquant** se corrige dans le lot ; les autres allaient jusqu'ici tous au backlog. Le **hook de l'agent** : un programme qui lit chaque commande de l'agent avant qu'elle tourne, et refuse celle qui écrirait un fichier protégé (les réglages que vous seul changez, les contrôles, la CI, c'est-à-dire les vérifications que GitHub rejoue) ou ferait une action externe irréversible (un push forcé, une publication, une suppression sur GitHub). Pour deviner ce qu'une commande fera, il relit le langage du shell, qui a une infinité de formes ; chaque revue en trouve de nouvelles. Derrière lui, le contrôle `protege.fichiers` compare l'empreinte (le condensé du contenu) de chaque fichier protégé à la fin de chaque réponse de l'agent, au commit et sur GitHub : toute écriture, quelle qu'en soit la forme, y est refusée jusqu'à ce que l'agent remette le fichier à son état, ou que vous l'approuviez. Un **agent coopératif** ne cherche pas à contourner ses garde-fous : ses écarts sont des erreurs.

**Règle 1, la revue.** Aujourd'hui, la procédure de la revue (le skill `socle-review`) dit : « **Pour le backlog** (le reste : un contournement hors du modèle de menace, un critère que le lot ne coche pas, un défaut voisin) : pas corrigé dans le lot ; il va au backlog ». Le texte nouveau, qui la remplace :

> **Pour le backlog** : un constat qui ne bloque pas va au backlog s'il peut se produire dans l'usage normal du projet, ou si rien ne rattrape ensuite son effet ; un sujet par constat, ou un pour plusieurs de même nature. **Écarté** : un constat exotique (un geste rare, une forme qu'on n'écrit que pour contourner, un cas jamais reproduit) dont l'effet est rattrapé, par un contrôle, la CI ou une erreur que l'agent voit aussitôt ; et un constat infondé. Une ligne du récap dit pourquoi chacun est écarté.

Un constat exotique que rien ne rattrape reste donc au backlog. Le même sens s'écrit dans la consigne que reçoit le relecteur et dans la section commune du fichier d'instructions des projets (AGENTS.md). La version anglaise du produit traduit ce texte ; votre accord porte sur le français.

**Règle 2, le hook.** Une décision nouvelle, qui complète celle du 13 novembre (le hook refuse ce qu'il ne sait pas juger, ADR-0072), et le guide d'un projet équipé (HELP.md) l'écrivent :

> Le hook de l'agent arrête les erreurs d'un agent coopératif avant qu'elles agissent. Il juge les formes du shell qu'un agent écrit dans son travail, et, quelle qu'en soit la forme, ce que rien ne rattrape ensuite : supprimer le projet ou un dossier qui le contient, une action externe irréversible, une fuite de la mémoire privée (la part de la mémoire qui ne se publie pas) dans ce qui se publie. Une écriture d'un fichier protégé sous une forme qu'on n'écrit que pour contourner (un `eval`, `IFS`, un chemin construit au vol dans un autre langage) est hors de son modèle : `protege.fichiers` la refuse ensuite, et un trou de cette sorte n'ouvre pas de sujet.

Elle ne change aucun code : le hook refuse toujours ce qu'il sait refuser, et ce qu'il ne sait pas juger. Elle dit seulement quels trous se corrigent.

## Éléments cités

- D-0111@034d5e87 — votre décision prise dans la conversation le 14 novembre, son message entier et les sujets écartés.
- D-0109@379b5396 — votre décision du 13 novembre : seuls les bloquants se corrigent dans le lot, le reste va au backlog.
- ADR-0073@1e48220c — la décision de l'agent qui spécifie la revue, que la règle 1 précise (une ADR est une décision de conception de l'agent ; un D-, la vôtre).
- ADR-0072@1a8b5c2d — la décision de l'agent : le hook refuse ce qu'il ne sait pas juger ; la règle 2 la complète.
- B-0206@2ebfe7b8 — un sujet gardé, des écritures que le hook ne voit pas (`cp -t`, `xargs`, `find -delete`, `python -c`) ; la règle 2 borne `python -c` aux chemins cités en toutes lettres.
- B-0218@be06bed9 — la copie du skill de revue dans ce dépôt, protégée, en retard sur le moteur ; vous la ferez suivre par une demande à part.

Le suffixe après @ est l'empreinte de la version lue.

## Où regarder

- [Votre décision D-0111](https://github.com/theodubus/memory/blob/3b11a9db7db693334ad308e47493fb754b89e940/memory/requests/D-0111-remarques-non-bloquantes.md) : la question posée et votre message entier.
- [Le skill de la revue](https://github.com/theodubus/memory/blob/3b11a9db7db693334ad308e47493fb754b89e940/engine/socle/templates/skills/socle-review/SKILL.md) : la section « Les constats », que la règle 1 change.
- [ADR-0072](https://github.com/theodubus/memory/blob/3b11a9db7db693334ad308e47493fb754b89e940/memory/decisions/ADR-0072-le-hook-de-l-agent-developpe-un-chemin-ecrit-comme.md) : ce que le hook juge aujourd'hui.

## Options

- Écrire les deux règles : effort faible, des textes, la décision du hook et un test de la consigne du relecteur ; risque faible, un constat jugé exotique à tort peut manquer, mais s'il se produit, il n'est plus exotique et rouvre un sujet ; réversible par une demande nouvelle.
- N'en écrire qu'une : même effort pour elle ; l'autre source garde l'ancienne règle dans les projets.
- N'en écrire aucune : aucun effort ; D-0111 ne vaut que dans ce dépôt, et les revues des projets équipés rouvrent des sujets exotiques.

## Conséquences

Si vous validez : l'agent écrit les textes dans le moteur et ses revues les appliquent aussitôt, par sa procédure des lots, qui n'est pas protégée et qu'il met à jour ; les projets les reçoivent à leur mise à jour, chess compris, que l'agent prépare sans geste de votre part. La copie protégée du skill dans ce dépôt attend B-0218. Si vous n'en validez qu'une, seule celle-là s'écrit. Si vous refusez : D-0111 vaut dans ce dépôt seul. Sans réponse : rien ne change, et l'agent continue les autres sujets.

## Recommandation

Valider. Vérifié : appliquée aux sujets ouverts, la règle 1 en a fermé trois et réduit quatre, et en a gardé des points qu'une lecture rapide aurait écartés à tort (D-0111) ; les formes que la règle 2 laisse hors du modèle sont refusées ensuite par `protege.fichiers`. Supposé : que le backlog né des revues et du hook converge sous ces règles ; on le verra au solde des prochaines semaines.

## Réponses possibles

- `valider` — l'agent écrit les deux règles dans le produit.
- `revue-seule` — l'agent n'écrit que la règle 1, celle de la revue.
- `hook-seul` — l'agent n'écrit que la règle 2, celle du hook.
- `refuser` — la règle reste celle de ce dépôt seul (D-0111).
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
