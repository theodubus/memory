<!-- socle: couche=demandes zone=publique -->
# D-0120 — Borner le hook de l'agent aux formes qu'un agent écrit, y compris pour ce que rien ne rattrape, et ne plus bloquer un lot sur la régression d'une forme exotique

> date : 2026-11-16

## Décision demandée

Remplacer la règle du hook validée le 14 novembre par une règle bornée à la forme : le hook juge les commandes qu'un agent écrit dans son travail, pour tout effet ; une forme exotique n'ouvre plus de sujet et ne bloque plus un lot, elle s'inscrit d'une ligne dans une liste des formes connues non jugées.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui rend fiables la mémoire (faits, décisions, sujets que l'agent écrit dans le dépôt), la documentation et les tests d'un projet de code entretenu par un agent d'IA. Chess, votre jeu d'échecs, le recevra à sa prochaine mise à jour ; ce dépôt s'en sert lui-même.

**Le chantier.** Le 13 novembre, vous avez demandé de finir une liste d'étapes avant toute nouvelle fonction ; le 15, elle a été découpée en sept lots (un lot : quelques sujets du backlog, la liste des choses à faire, menés ensemble puis relus par un agent sans contexte qui cherche à les prendre en défaut). Le premier, B-0234, devait fermer deux trous du hook : une fonction du shell écrite sans parenthèses, et la suppression du projet par d'autres programmes que `rm` ; les deux sont fermés, la troisième passe de sa revue est en cours. Le 14 novembre, vous avez validé deux règles pour borner le backlog : la revue écarte un constat exotique dont l'effet est rattrapé (règle 1, qui reste) ; le hook juge les formes qu'un agent écrit, et, « quelle qu'en soit la forme », ce que rien ne rattrape ensuite (règle 2). La demande d'alors notait comme supposé, à vérifier : « que le backlog né des revues et du hook converge sous ces règles ».

**La question.** Le 13 novembre déjà, après trente contournements trouvés en deux revues, le hook avait été réglé pour refuser ce qu'il ne sait pas lire, plutôt que de chercher à tout lire. Vous demandez, le 16, si l'on ne retombe pas dans un interpréteur du shell qui ne converge jamais, et si la règle 2 suffit. Deux jours de mesures disent qu'elle ne suffit pas.

Les termes. Le **hook de l'agent** lit chaque commande de l'agent avant qu'elle tourne, et refuse celle qui écrirait un fichier protégé (vos réglages, les contrôles, la CI), supprimerait le projet, ou ferait une action externe irréversible (un push forcé, une publication). Il relit pour cela le **shell**, le langage des commandes, aux formes infinies. Un **trou** : une forme qui passe alors qu'elle devrait être refusée. **Ce que rien ne rattrape** : un effet qu'aucun contrôle ne répare ensuite, au contraire d'un fichier protégé écrit, que le contrôle `protege.fichiers` refuse à la fin de chaque réponse de l'agent. Un **agent coopératif** ne cherche pas à contourner ses garde-fous. Un **bloquant** : un constat de la revue qui se corrige avant de livrer le lot. Une **forme exotique** : rare, qu'on n'écrit que pour contourner, ou qu'aucun agent n'a écrite dans son travail.

Ce qui est mesuré. Depuis le 14 novembre, onze sujets du hook de priorité haute (ceux qui passent avant les autres dans les lots) ont été ouverts : B-0232, puis dix par le lot B-0234 ; deux sont fermés (B-0232, B-0250), neuf restent, cités plus bas. Chacun vient d'un relecteur ou d'un implémenteur (le sous-agent qui écrit le code) qui cherchait les formes que le hook manque, aucun d'une commande écrite par un agent dans son travail. B-0234, parti de deux sujets, a demandé trois passes de revue et corrigé six bloquants.

Deux boucles ne s'arrêtent pas. La première : « quelle qu'en soit la forme », dans un langage infini, donne un sujet par forme ; le critère porte sur l'effet, pas sur la vraisemblance. La seconde : chaque correction change la lecture du shell, et une forme que l'ancienne lecture refusait par accident, en la lisant de travers, passe ensuite ; la revue compte cela comme une régression, donc un bloquant. Les six bloquants du lot étaient tous de cette sorte.

Le point où se joue le risque. Le hook refuse déjà ce qu'il sait ne pas savoir lire (une variable inconnue, une substitution), et cela ne change pas. Les neuf trous sont des formes qu'il lit de travers, en croyant les comprendre : elles passent aujourd'hui, et la règle proposée les laisse passer tant qu'aucun agent ne les écrit.

La règle proposée, à la place de la règle 2 :

> Le hook de l'agent arrête les erreurs d'un agent coopératif avant qu'elles agissent. Il juge les formes du shell qu'un agent écrit dans son travail, pour tout effet ; pour ce que rien ne rattrape ensuite (supprimer le projet ou un dossier qui le contient, une action externe irréversible, une fuite de la mémoire privée, la part de la mémoire qui ne se publie pas), il refuse aussi ce qu'il ne sait pas lire. Un trou ouvre un sujet si sa forme est de celles qu'un agent écrit dans son travail : vue dans une session d'agent, un skill (une procédure écrite pour l'agent) ou une documentation courante. Une autre forme s'inscrit d'une ligne dans la liste des formes connues que le hook ne juge pas, sans sujet ; dans la revue d'un lot du hook, elle n'est pas un bloquant, même refusée avant le lot par accident.

Le relecteur propose le classement, l'agent le vérifie ; la liste s'écrit dans le guide d'un projet équipé, que vous pouvez relire et que chess reçoit. Le risque restant viendrait de couches qui ne lisent pas le shell, à étudier dans un sujet : la protection de la branche par défaut sur GitHub, qui refuse un push forcé côté serveur (active ici pour la CI ; pour le push forcé, à vérifier) ; le push de chaque fin de réponse, que l'environnement cloud exige déjà, qui laisse le projet entier sur GitHub. Rien ne borne aujourd'hui la perte d'un dossier qui contient le projet hors du projet lui-même.

## Éléments cités

- ADR-0080@bfb13155 — la décision (une ADR : une décision de conception de l'agent) qui écrit la règle 2.
- D-0112@c8501606 — votre demande validée du 14 novembre, ses deux règles, dont l'hypothèse de convergence.
- B-0234@97238e0d — le lot du hook en cours.
- B-0232@fcc3458b — le sujet fermé de la fonction sans parenthèses, l'un des deux du lot.
- B-0250@180cb00a — un sujet ouvert puis fermé dans le lot : l'appel d'une fonction dans un `eval`.
- J-2026-11-15-O@97e152cd — l'entrée du journal de la première revue du lot.
- J-2026-11-16-B@332169d9 — l'entrée du journal de la seconde revue.
- B-0235@738569b0 — le lot suivant du hook, les écritures qu'il juge mal.

Les neuf sujets ouverts, chacun passant aujourd'hui, avec le sort que l'agent leur propose (supposé, à confirmer en les relisant) :

- B-0244@bba1deb1 — `time` devant une commande composée : à la liste.
- B-0245@9c775aa7 — les motifs d'un `case` : à la liste.
- B-0246@1e83d064 — la suppression du projet par `xargs rm` ou `python -c` : gardé pour `find … | xargs rm`, qu'un agent écrit.
- B-0247@7ae3d2f9 — `find -exec` derrière `sudo` : à la liste.
- B-0248@1b70392d — `coproc`, `uv run`, `poetry run` : gardé pour `uv run` et `poetry run`.
- B-0253@6d4cc3c0 — un `return`, un appel indirect, une fonction nommée comme une commande : à la liste.
- B-0254@3c879493 — un push forcé dont l'option vient d'une variable ou d'une fonction d'aide : gardé.
- B-0255@8dc5ba83 — `git --config-env` qui cache la sous-commande : à la liste.
- B-0256@f1fd9b01 — ce qu'un `eval` change : à la liste.

Le suffixe après @ est l'empreinte de la version lue.

## Où regarder

- [ADR-0080](https://github.com/theodubus/memory/blob/829fe86520f14ff648422ddc2d09445b027a1974/memory/decisions/ADR-0080-le-modele-de-menace-du-hook-de-l-agent-les-erreurs.md) : la règle 2, et sa première conséquence, qui ouvre un sujet pour toute forme.
- [Le journal](https://github.com/theodubus/memory/blob/829fe86520f14ff648422ddc2d09445b027a1974/memory/journal/2026-11-5.md), entrées J-2026-11-15-O et J-2026-11-16-B : les constats des deux premières revues, et pourquoi chacun est bloquant ou au backlog.

## Options

- Valider : les deux changements, la règle bornée et la régression exotique qui ne bloque plus. Ils s'écrivent dans le produit (la décision qui remplace la règle 2 d'ADR-0080, le guide, la consigne du relecteur) au prochain lot ; les neuf sujets se relisent, trois gardés en partie, le reste à la liste ; un sujet étudie les couches qui ne lisent pas le shell. Effort : des textes, aucun code du hook. Risque : une forme jugée exotique à tort laisse passer la suppression du projet ; une forme vue en usage cesse d'être exotique et rouvre un sujet. Réversible.
- `a-venir-seul` : la même règle pour les constats à venir ; les neuf sujets restent, soit environ deux lots du hook devant le reste (supposé). Réversible.
- `bloquants-seuls` : seule la régression exotique ne bloque plus un lot ; la règle 2 reste pour les sujets, qui continuent de s'ouvrir. Réversible.
- Refuser : rien ne change ; B-0234 se finit sous la règle 2, quitte à corriger d'autres bloquants, et B-0235 risque le même cycle. Réversible.

## Conséquences

Si vous validez : dès la réponse, la revue de B-0234 classe selon la règle nouvelle ; la règle s'écrit dans le produit au prochain lot, que chess reçoit à sa mise à jour ; les neuf sujets se relisent ; le sujet d'étude s'ouvre. Avec `a-venir-seul`, de même, sans relire les neuf. Avec `bloquants-seuls`, seule la revue change. Si vous refusez, ou sans réponse : rien ne change, et la demande reste en attente.

## Recommandation

Valider. Vérifié : les comptes ci-dessus, relevés au backlog et au journal ; les six bloquants du lot étaient des formes que l'ancien hook refusait en les lisant de travers ; aucun des neuf sujets ne vient d'une commande écrite par un agent dans son travail. Supposé : qu'un agent coopératif écrit un ensemble étroit de formes, ce que les sessions réelles pourront mesurer ; le sort proposé des neuf sujets ; que les couches qui ne lisent pas le shell couvrent le risque restant.

## Réponses possibles

- `valider` — la règle bornée et la régression exotique non bloquante, dès ce lot ; les neuf sujets se relisent.
- `a-venir-seul` — la même chose pour les constats à venir ; les neuf sujets restent.
- `bloquants-seuls` — seule la régression exotique ne bloque plus un lot.
- `refuser` — la règle du 14 novembre reste.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
