---
name: delegate-lot
description: Mener un lot du backlog dans ce dépôt, en orchestrateur : ce qui s'ajoute ici au skill du produit socle-batch (le modèle, la consigne des sous-agents, la revue, la fusion par l'agent, la distribution, le prompt de mise à jour de chess, les mesures de l'atelier). À utiliser dans ce dépôt quand la session annonce un lot, à chaque étape du lot, et à la reprise d'un lot en cours après un compactage ou un changement de modèle.
---

# Mener un lot dans ce dépôt

La procédure est celle du produit, le skill `socle-batch` : lire
`engine/socle/templates/skills/socle-batch/SKILL.md` à ce chemin tant que
sa copie protégée n'est pas posée dans `.claude/skills/`. Ce skill ne dit
que ce qui s'y ajoute ici. Ses raisons : D-0096, J-2026-11-11-G,
ADR-0079.

## L'annonce et la clôture

À l'annonce d'un lot, puis à sa clôture, lancer
`python3 .socle/socle roadmap` et en coller la sortie dans la réponse,
dans un bloc de code :
où le lot se place parmi les jalons et les lots, puis ce qui vient après
lui (B-0274).

## Les sous-agents

Le modèle est celui que dit le chantier actif ; un sous-agent qui doit
tourner sur celui de la session se lance sans `model`, l'alias `opus`
ayant désigné un Opus plus ancien que celui de la session (B-0251). La consigne est celle du
produit, avec, en tête : « Tu implémentes une tâche du socle dans ton
worktree du dépôt memory. AGENTS.md s'applique. » ; dans « À livrer » :
des tests qui échouent sur le commit parent, pour tout code ; pour un
contrôle ou un refus nouveau, son défaut injecté et son témoin sain ; la
tâche rangée (`socle archive`) ; `verify --fast` une fois, à la fin ;
dans « Interdits » : ouvrir
une pull request, lire ou ajouter un autre dépôt ; puis « Économie : lire
ce qui sert, pas les fichiers entiers ; pas de suite complète relancée
sans raison. » Les identifiants des sous-agents lancés vont dans le texte
des réveils.

## La revue

Le dossier du lot se produit dans le worktree du sous-agent et se range
dans le dossier temporaire de la session ; le relecteur est un autre
sous-agent, sans worktree, qui ne reçoit que le chemin du dossier, la
logistique et les points à éprouver. Il classe ses constats (ADR-0073,
la règle de D-0111) ; l'orchestrateur vérifie chaque classement.

## La livraison

- L'agent fusionne lui-même sa pull request (D-0092). L'attente de la CI :
  une boucle en arrière-plan qui cherche `success sur <sha court>` (ou
  `failure sur <sha court>`) dans la ligne « CI » de l'état.
- Après la fusion, vérifier que la distribution a tourné
  (`.github/workflows/distribution.yml`).
- Un lot qui change ce qu'un projet reçoit à la mise à jour complète
  `docs/fabrication/chess/prompt-mise-a-jour.md` (J-2026-11-13-L).
- La réponse de l'humain se commite dans le même push que le changement
  qu'elle autorise, jamais avant (B-0142) ; seul un fichier protégé peut
  la précéder, sous la demande en attente (D-0071).
- Une valeur attendue à changer, un test à supprimer, un fichier protégé
  à rafraîchir : une demande dans le dépôt, relue à froid, poussée, son
  lien donné (J-2026-11-12-F). Sauf un changement mécanique de valeurs
  attendues, des tests qui lisent un format que Théo a validé : une
  question dans la conversation qui nomme chaque test, avec sa valeur
  avant et après, et sa réponse consignée en séance (proposition 2 de
  `docs/fabrication/allegements.md`).

## Les mesures de l'atelier

Ce qui pèse est mesuré dans `docs/fabrication/consommation.md` (B-0173).
Le 13 novembre (J-2026-11-13-E), un sous-agent qui implémente lisait
environ 320 000 jetons, un relecteur 240 000, soit 3 à 4 points de la
semaine chacun : d'où les seuils du skill du produit.

## Changer de session

Le correctif d'un commit pas encore relu va dans un dossier de passation
sous `docs/fabrication/`. Le prompt de la session neuve est celui du
produit, avec « Reprends le travail du socle dans ce dépôt » et le lot
« selon le skill delegate-lot ».
