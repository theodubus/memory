<!-- socle: couche=demandes zone=publique -->
# D-0205 — T-0191 : en session cloud, le proxy refuse à l'agent de supprimer une autre branche que la sienne ; clore T-0191 sur ce refus éprouvé, et ouvrir un besoin pour le cas cloud ?

> date : 2026-11-26

## Décision demandée

Clore T-0191 alors que son dernier critère, la suppression réelle de `ccr-c196a77f-s8vzo6`, a été refusé par le proxy de la session cloud, et ouvrir un besoin pour ce cas.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, le moteur que reçoit un projet comme chess : mémoire, documentation et tests tenus par des contrôles, des hooks et la CI, pour un agent qui travaille seul sur le backlog.

**Le chantier.** Le lot en cours fait supprimer à l'agent ses propres branches distantes déjà contenues dans `main` ou dans sa branche de travail, au lieu de les donner à supprimer à l'humain à chaque fin de lot. Tu as retenu le 25 novembre « 1A 2A » : seulement les branches de l'agent, et par défaut dans le produit. Le 26 novembre, tu as laissé `ccr-c196a77f-s8vzo6` à la commande. La commande `socle prune-branches` est écrite, testée, relue, et la revue a trouvé un défaut, corrigé.

**La question.** Lancée ici, la commande a bien tenté de supprimer `ccr-c196a77f-s8vzo6` et `ccr-5ee489f7-ukpvc6`. Le proxy de la session cloud a refusé les deux pushes (HTTP 403). Une session cloud ne pousse que sur sa propre branche ; sa documentation dit de ne pas retenter un tel refus. Le dernier critère de T-0191 ne peut donc pas être tenu dans une session cloud.

La commande a suivi le chemin prévu pour un refus. Rien n'est supprimé. Le refus est gardé dans le clone avec la tête refusée, et l'état te redonne les deux branches, avec la raison : « l'origine a refusé à l'agent de la supprimer (error: RPC failed; HTTP 403 …) ». Hors du cloud, sur ta machine, rien ne bride le push : la suppression se fait, comme les tests le montrent sur des dépôts d'essai.

Par conséquent, dans tes sessions cloud au prompt à copier, où chaque session neuve a sa branche, la branche de la session d'avant te reviendra encore. En session programmée, la session suivante reprend la même branche, et rien n'est à supprimer. GitHub supprime déjà la branche d'une pull request à sa fusion : celle de cette session a disparu à la fusion de sa pull request, le 26 novembre, puis le push suivant l'a recréée. La branche qui reste est donc celle qu'une session repousse après la fusion, pour sa passation, comme `ccr-5ee489f7-ukpvc6` : le besoin du cas cloud peut partir de là.

## Éléments cités

- T-0191@eec89007 — la tâche de la commande `socle prune-branches`, dont le quatrième critère est la suppression de `ccr-c196a77f-s8vzo6` dans ce dépôt.
- B-0351@bf78a534 — le besoin : une branche de l'agent déjà contenue ailleurs se supprime sans geste de l'humain.
- J-2026-11-26-B@e230e1b1 — l'entrée du journal où tu laisses `ccr-c196a77f-s8vzo6` à la commande.
- ADR-0114@679f6e04 — la décision du mécanisme : vérification sur l'origine, suppression sous bail, refus gardé et rendu à l'humain.

## Où regarder

- [La spécification et son modèle de menace](https://github.com/theodubus/memory/blob/744178ec3bf454db9e3aaf4110522e1e3b1dc0df/docs/fabrication/branches-de-l-agent-specification.md) : vérifier qu'« une origine qui refuse » y est prévue, sans rien supprimer, la branche rendue à l'humain.
- [La commande](https://github.com/theodubus/memory/blob/744178ec3bf454db9e3aaf4110522e1e3b1dc0df/engine/socle/branches.py) : `elaguer`, et le refus gardé.

## Options

- **A, clore et ouvrir un besoin.** T-0191 se clôt : son quatrième critère est noté « refusé par le proxy cloud, le chemin du refus éprouvé en usage réel ». B-0351 se clôt aussi, satisfait hors du cloud. Un besoin neuf porte le cas cloud, hors du jalon de chess : par exemple une passation qui ne repousse pas la branche après la fusion, ou la session programmée, qui garde la même branche. Le prompt de mise à jour de chess, qui attend B-0351, devient prêt. Effort : quelques lignes de mémoire. Risque : nul, le code ne change pas. Réversible.
- **B, attendre une session sur ta machine.** T-0191 reste ouverte jusqu'à ce qu'une session locale lance la commande ici et voie la branche supprimée. B-0351 reste ouvert avec elle, et le prompt de chess, qui l'attend, aussi : la mise à jour de chess attend cette session. La pull request se fusionne quand même. Effort : une session de ta part. Réversible.

## Conséquences

Si tu valides (A), je clos T-0191 et B-0351, j'ouvre le besoin du cas cloud hors du jalon de chess, le lot se clôt, et le prompt de chess devient la suite. Les deux branches restent à toi : tu les supprimes sur GitHub. Si tu refuses, T-0191 reste ouverte comme en B, et je te demande ce qui la clora. Sans réponse, T-0191 reste ouverte, et la suite attend. La pull request du lot se fusionne de toute façon : son code ne dépend pas de ta réponse.

## Recommandation

A. Vérifié : le refus du proxy (403, deux fois), la branche rendue dans l'état avec sa raison, les tests et l'auto-test de la suppression réelle sur des dépôts d'essai. Supposé : qu'une session sur ta machine supprimerait la branche, puisque rien ne bride son push ; que chess tourne aussi en session cloud, auquel cas la commande ne lui supprimera rien non plus.

## Réponses possibles

- `valider` — option A : T-0191 et B-0351 se closent sur le refus éprouvé, un besoin neuf porte le cas cloud, le lot se clôt, le prompt de chess suit.
- `attendre-une-session-locale` — option B : T-0191 reste ouverte jusqu'à une session sur ta machine.
- `refuser` — T-0191 reste ouverte, et je te demande ce qui la clora.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
