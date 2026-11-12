---
name: delegate-lot
description: Mener un lot du backlog en orchestrateur, un sous-agent par sujet dans un worktree, relu par un autre avant tout push, puis intégré, poussé et fusionné. À utiliser dans ce dépôt quand la session annonce un lot et le confie à des sous-agents, à chaque étape du lot, et à la reprise d'un lot en cours après un compactage ou un changement de modèle.
---

# Mener un lot par des sous-agents

La session principale orchestre : elle annonce le lot, écrit les consignes,
fait relire, intègre et livre. Elle n'implémente pas, sauf un changement de
quelques lignes, qu'elle fait elle-même plutôt que de reprendre un
sous-agent. Ce skill dit comment faire ; l'organisation et ses raisons sont
dans la mémoire (D-0096, J-2026-11-11-G).

## Avant de lancer

1. Lire chaque sujet du lot (`python3 .socle/socle show B-NNNN`) et
   annoncer le lot à l'humain : les sujets, leur taille, le jalon servi.
2. Armer les réveils (skill `socle-resume`).
3. Partir d'une branche de travail propre et poussée : chaque sous-agent
   la rattrape en commençant.

## Un sous-agent par sujet

Outil `Agent`, type `general-purpose`, `isolation: "worktree"`, en
arrière-plan ; le modèle est celui que dit le chantier actif. Sa consigne
se lit seule, il n'a pas la conversation :

```text
Tu implémentes un sujet du socle dans ton worktree du dépôt memory.
AGENTS.md s'applique. Commence par : git merge --ff-only <branche de travail>

Sujet : python3 .socle/socle show B-NNNN, puis ce que l'orchestrateur
ajoute (le choix déjà fait, les fichiers où regarder, les pièges connus).

À livrer, en UN commit, sans push :
- le code, et ses tests qui échouent sur le commit parent ;
- pour un contrôle ou un refus nouveau, son défaut injecté et son témoin sain ;
- la documentation touchée ; une ADR si une décision de conception est prise ;
- une entrée de journal ; le sujet coché, clos et rangé (socle archive)
  si tous ses critères sont tenus ;
- python3 .socle/socle verify --fast, une fois, à la fin.

Interdits : pousser, ouvrir une pull request, toucher un réveil, écrire
dans un fichier protégé, lire ou ajouter un autre dépôt, changer une
valeur attendue ou supprimer un test (le signaler à la place), corriger
un défaut voisin (un sujet au backlog).

Économie : lire ce qui sert, pas les fichiers entiers ; pas de suite
complète relancée sans raison.

Compte rendu : le commit, les fichiers, ce que les tests prouvent, les
choix faits, ce qui reste ou gêne.
```

Les identifiants des sous-agents lancés vont dans le texte des réveils.

## La revue, avant tout push

Skill `socle-review`. Le dossier du lot se produit dans le worktree du
sous-agent et se range dans le dossier temporaire de la session ; le
relecteur est un autre sous-agent, sans worktree, qui ne reçoit que le
chemin du dossier, la logistique et les points à éprouver. Ses constats
retournent au sous-agent qui a implémenté (`SendMessage`), tant que son
worktree existe ; sinon à un sous-agent neuf, avec la consigne et les
constats. Un lot dont la correction est lourde se fait relire une seconde
fois avant le push.

## Intégrer, pousser, fusionner

1. Depuis la branche de travail : `git merge --ff-only <branche du
   sous-agent>` si son commit suit la tête de la branche de travail, sinon
   `git merge --squash` puis un commit qui reprend son message. Deux lots
   menés ensemble se heurtent sur les lettres du journal et les numéros
   d'ADR : le second intégré se renumérote (B-0176).
2. Retirer le worktree et sa branche, puis `python3 .socle/socle verify --fast`.
3. Pousser, ouvrir la pull request s'il n'y en a pas (une seule ouverte),
   attendre la CI du commit de tête (une boucle en arrière-plan sur la
   ligne « CI » de `python3 .socle/socle state`, jamais sur un commit
   d'avant), puis la fusionner soi-même (D-0092) en donnant le commit de
   tête attendu.
4. Après la fusion : `git fetch origin main`, `git rebase origin/main`,
   pousser ; vérifier que la distribution a tourné ; mettre à jour le
   chantier actif et le journal.

## Ce qui ne se rattrape pas après un push

Le contrôle d'avant push juge la plage qui part contre la tête de la
branche distante : une fois poussées, une ADR, une entrée de journal et
une valeur attendue ne se réécrivent plus, elles se complètent.

- Un lot ne part qu'après les corrections de sa revue.
- La réponse de l'humain à une demande se commite dans le même push que
  le changement qu'elle autorise, jamais avant (B-0142).
- Une valeur attendue à changer, un test à supprimer, un fichier protégé
  à rafraîchir : une demande dans le dépôt, relue à froid, poussée, son
  lien donné ; jamais une question dans la conversation.
- Avant d'ouvrir un sujet, relire le backlog
  (`python3 .socle/socle show --index backlog`).

## La consommation

En attendant la mesure de B-0173 :

- demander à l'humain de compacter à la fin de chaque lot et avant une
  attente longue : après une heure d'arrêt, toute la conversation se
  relit au prix fort ;
- ne pas reprendre un sous-agent après une pause longue quand un neuf,
  avec sa consigne et les constats, suffit ;
- attendre une CI ou un sous-agent sans sonder : leur fin relance la
  session.
