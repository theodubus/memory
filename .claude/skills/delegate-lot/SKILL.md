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
   attendre la CI du commit de tête, puis la fusionner soi-même (D-0092)
   en donnant le commit de tête attendu. L'attente : une boucle en
   arrière-plan sur la ligne « CI » de `python3 .socle/socle state`, qui
   s'écrit `CI : <workflow> : <résultat> sur <sha court>`, le résultat
   avant le commit ; la boucle cherche donc `success sur <sha court>` (ou
   `failure sur <sha court>`), jamais `<sha> … success`, ni un commit
   d'avant.
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

Ce qui pèse (B-0173, `docs/fabrication/consommation.md`) : chaque appel
relit toute la conversation, et chaque pas de l'orchestration en est un
(lancer un sous-agent, recevoir son compte rendu, intégrer, regarder la
CI) ; après plus d'une heure d'arrêt, la conversation se relit au prix
fort ; un sous-agent repris après plus de cinq minutes aussi. Un
sous-agent ne relit pas la conversation qui l'a lancé.

- Un lot par session : la session courte orchestre à bas prix.
- Deux sous-agents à la fois au plus, un seul quand la semaine dépasse
  75 %. Un petit sujet ou un correctif de quelques lignes, la session le
  fait elle-même.
- Mesuré le 13 novembre (J-2026-11-13-E) : un sous-agent qui implémente
  lit environ 320 000 jetons, un relecteur 240 000, soit 3 à 4 points
  de la semaine chacun. Avant d'en lancer un, et à chaque compte rendu,
  lire les deux fenêtres ; au-delà de 85 % de la semaine ou de 60 % des
  cinq heures, n'en lancer aucun : ranger (« Changer de session »).
- Un sous-agent ne se reprend pas après une pause : un neuf reçoit la
  consigne et les constats.
- Une attente de plus d'une heure (une CI longue, une réponse de
  l'humain, la nuit) ne se fait pas dans une conversation longue : la
  session range et s'arrête.
- Les réveils (skill `socle-resume`) s'arment pendant le lot, pour le cas
  rare où une étape atteint une limite, et se retirent à la fin d'un tour
  où rien ne tourne.

## Changer de session

Quand : un lot est rendu (fusionné) et la fenêtre de cinq heures ne
permet pas d'en faire un autre entier sans être coupé, ou une attente de
plus d'une heure s'annonce. La part consommée de la fenêtre se lit dans
`list_events` (`kinds: ["rate_limit_event"]`, `utilization` de
`five_hour`).

Ranger d'abord, pour qu'une session neuve, sur ce compte ou un autre,
reparte du dépôt seul :

1. tout poussé, rien qui ne vive que dans le conteneur (un commit pas
   encore relu part en correctif, `git format-patch`, dans un dossier
   de passation sous docs/fabrication, retiré quand le lot s'intègre) ;
   la pull request fusionnée ;
2. les worktrees et leurs branches retirés ;
3. le chantier actif dit le lot suivant et ce qui attend (un compte
   rendu, une CI, une demande) ;
4. les réveils retirés.

Puis le dire dans la conversation : qu'il faut changer de session, et
pourquoi, et donner le prompt de la session neuve, dans un bloc de texte
à copier :

```text
Reprends le travail du socle dans ce dépôt, en session neuve.
Avant tout : lis l'état que le démarrage injecte, borné ; une ligne
« !! coupé » dit ce qui y manque et où le lire (l'état dérivé entier :
python3 .socle/socle state --short) : lis-le, puis memory/active.md, et
applique-les.
Le lot : <les sujets, dans l'ordre>, selon le skill delegate-lot.
Ce qui attend : <un compte rendu, une CI, une demande> | rien.
```
