<!-- socle: couche=decisions zone=publique -->
# ADR-0041 — Un commit cité, absent du clone, se cherche dans les pull requests de l'origine avant d'être dit absent

> statut : proposée · date : 2026-11-01 · source : D-0063@5371f812, B-0117@4160db6a · lu : decisions@655f507c

## Contexte

L'entrée J-2026-10-31-S@040ddd1e du journal cite, sous la forme `commit:`, la tête
de l'ancienne branche de ce dépôt. Théo a supprimé cette branche ; GitHub
garde le commit dans la PR #10, mais un clone ne récupère que les
branches et les étiquettes, et `memoire.references` le disait absent. Le
journal est en ajout seul : la référence reste. Théo a choisi l'étiquette
(D-0063@5371f812) ; son push a été refusé par le proxy de la session, qui
ne pousse que sur la branche de travail, et n'a pas été retenté. J'ai
alors corrigé le contrôle sans revenir vers Théo (B-0117@4160db6a), et
l'en ai informé après coup : cette décision s'écrit ici, en retard.

## Décision

- Avant de dire absent un commit cité, `memoire.references` récupère une
  fois par processus les têtes des pull requests de l'origine, sous
  `refs/socle/pull/*`, et cherche de nouveau. Sans origine ni réseau,
  rien ne change.
- Le hook de l'agent, qui refuse un SHA écrit de tête, ne change pas : un
  commit qu'il écrit doit exister dans son clone.

## Conséquences

Ce que ça apporte : aucun geste de l'humain, et la même protection pour
un projet qui fusionne en écrasant les commits, dont les branches
s'effacent seules à la fusion.

Ce que ça coûte :
- un accès réseau dans un contrôle, une fois par processus et seulement
  quand un commit cité manque ; la première récupération de toutes les
  pull requests peut peser dans un gros dépôt ;
- les noms `refs/pull/*` sont ceux de GitHub ; une autre forge aurait les
  siens ;
- un commit d'une pull request jamais fusionnée compte comme existant.
  Pour le journal, c'est son histoire ; pour la preuve d'un fait, c'est
  plus faible, et B-0116@a78e9984 garde la prévention.

Pour défaire : retirer la récupération de `verifier_ref`, puis poser
l'étiquette ou restaurer la branche, avec l'humain.
