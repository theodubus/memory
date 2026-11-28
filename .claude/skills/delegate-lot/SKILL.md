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
lui (B-0274). Après la clôture du troisième lot depuis la dernière revue
de cap, ou d'un jalon, la revue de cap passe avant le lot suivant : le
skill `direction-review` (D-0145).

La question d'intention d'un besoin qui agit sur l'origine (pousser,
supprimer, étiqueter) dit ce que la session cloud permet : elle ne pousse
que sur sa branche et n'en supprime aucune autre (J-2026-11-01-E). Plus
de code qui supprime des branches distantes : une branche qui reste se
prévient (D-0209).

## Les sous-agents

L'orchestrateur implémente, sauf quand un sous-agent paie, selon
`socle-batch` (D-0194, la page validée
`docs/fabrication/organisation-proportionnee.md`) : une tâche qui ne
change que le texte d'un skill reste à l'orchestrateur. Plusieurs tâches
de code qui touchent les mêmes fichiers peuvent aller à un seul sous-agent, un
commit chacune : son coût fixe ne se paie qu'une fois.

Le modèle est celui que dit le chantier actif ; un sous-agent qui doit
tourner sur celui de la session se lance sans `model`, l'alias `opus`
ayant désigné un Opus plus ancien que celui de la session (B-0251). La consigne est celle du
produit, avec, en tête : « Tu implémentes une tâche du socle dans ton
worktree du dépôt memory. AGENTS.md s'applique. » ; dans « À livrer » :
des tests qui échouent sur le commit parent, pour tout code ; pour un
contrôle ou un refus nouveau, son défaut injecté et son témoin sain ; la
tâche close (`socle close`) ; `verify --fast` une fois, à la fin ;
dans « Interdits » : ouvrir
une pull request, lire ou ajouter un autre dépôt ; le dossier temporaire
commun, nommé par son chemin. Les identifiants des sous-agents lancés
vont dans le texte des réveils.

## La revue

Une revue adversariale quand le lot la justifie (`socle-review`,
« Quand ») ; sinon, l'orchestrateur relit lui-même son diff, et le récap
le dit. Le dossier du lot se produit sur la branche d'intégration, jamais dans le
worktree d'un sous-agent, où la passe que `socle review` écrit dans le lot
se perdrait : la passe s'y commite, et le dossier se range dans le dossier
temporaire de la session (T-0055) ; le relecteur est un autre
sous-agent, sans worktree, qui ne reçoit que le chemin du dossier, la
logistique et les points à éprouver. Il classe ses constats (ADR-0073,
la règle de D-0111) ; l'orchestrateur vérifie chaque classement.

Ce qui entre au backlog, ici, se juge par `docs/fabrication/but-et-tri.md`
(D-0167) : la consigne du relecteur lui donne ce chemin, et un constat
qui ne bloque pas n'y entre que s'il passe ses trois tests ; sinon il
s'écarte, d'une ligne au journal, et revient s'il est vu. L'orchestrateur
l'applique de même à toute entrée qu'il ouvre et à la formation des lots.
Avant d'abandonner des entrées, il en donne le récap à Théo, chacune avec
sa raison.

Un lot qui touche le hook de l'agent (`engine/socle/hooks.py`,
`engine/socle/commands.py`) ne s'ouvre que sur une preuve (ADR-0098). Son
relecteur ne cherche pas de contournements : il vérifie que le lot ne
casse rien de ce qui marchait, et sa consigne le lui dit ; un
contournement qu'il trouve s'écarte d'office, sans entrée au backlog.

## La livraison

- L'agent fusionne lui-même sa pull request (D-0092). L'attente de la CI :
  une boucle en arrière-plan qui attend que toutes les exécutions du
  commit attendu soient conclues (`gh run list --commit <sha>`), puis dit
  leurs conclusions ; la ligne « CI » de l'état suit la tête locale,
  qu'un commit fait pendant l'attente déplace (J-2026-11-24-AS). Sans
  `gh` authentifié, l'état le dit : un réveil à l'heure probable de la
  fin, revérifié à chaque tour.
- Après la fusion, vérifier que la distribution a tourné
  (`.github/workflows/distribution.yml`).
- Un lot qui change ce qu'un projet reçoit à la mise à jour complète
  `docs/fabrication/chess/prompt-mise-a-jour.md` (J-2026-11-13-L). Le
  prompt ne fait pas écrire un même texte dans deux entrées, que
  `docs.copie` refuse : il dit laquelle le porte, l'autre y renvoyant ;
  il ne fait pas vérifier sur un clone fabriqué ce qu'un test joue déjà
  (J-2026-11-28-A) ; il fait nommer un fichier que git ne suit pas, le
  journal local des hooks par exemple, sans accents graves, que le
  contrôle de fin de tour refuserait (J-2026-11-28-D).
- Le prompt de mise à jour de chess ne se donne que sur une CI où
  `tests/test_mise_a_jour_rejouee.py` passe ; après la mise à jour de
  chess, sa constante `MOTEUR_DE_CHESS` avance au commit dont chess a reçu
  le moteur (B-0368), dans le premier lot qui change ensuite `engine/` :
  avant, la mise à jour rejouée n'a rien à changer, et le test échoue
  (J-2026-11-28-A).
- La réponse de l'humain se consigne, se commite et se pousse dès qu'elle
  est donnée ; la tâche qui fera le changement la cite, et la couvre tant
  qu'elle est ouverte et que ce qu'elle nomme n'a pas bougé (D-0189).
- Un lot qui change le gabarit d'un skill du produit
  (`engine/socle/templates/skills/`) remet sa copie protégée de
  `.claude/skills/` avant sa clôture : l'installeur relancé en mode amont,
  sans demande. La copie identique à son gabarit passe, comme les tests
  qui ne perdent que des phrases que le gabarit a quittées (D-0197,
  ADR-0110) ; ce que l'installeur réécrit d'autre suit ses règles, la
  section du socle d'`AGENTS.md` remise à son état commité.
- Une valeur attendue à changer, un test à supprimer, un fichier protégé
  à rafraîchir, hors de ce qui précède : une demande dans le dépôt, relue à froid si elle passe
  la moitié de son budget, poussée, son lien donné (J-2026-11-12-F). Sauf un changement mécanique de valeurs
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

La session est l'unité de budget (D-0194) : à la clôture d'un lot, elle
enchaîne le suivant selon `socle-batch` ; sinon elle range, et son récap
dit comment reprendre (J-2026-11-20-AD).

Le correctif d'un commit pas encore relu va dans un dossier de passation
sous `docs/fabrication/`. À l'intégration d'une passation, après
l'application de ses correctifs (`git am`), la branche de passation se
fusionne dans la branche de travail (`git merge --no-edit`), puis son
dossier se retire : l'état la donne alors à supprimer après la fusion de
la pull request (B-0293). Ici, le mode est le prompt à copier (D-0173) :
la passation écrite, commitée et poussée (skill `socle-handoff`), le
récap dit à Théo d'écrire « reprends » dans une session neuve, où le lot
se mène selon ce skill (D-0190).
