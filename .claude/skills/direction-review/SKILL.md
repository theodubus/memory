---
name: direction-review
description: La revue de cap de ce dépôt : un sous-agent neuf juge si l'effort va là où est le but du socle et rend au plus trois suggestions, preuves à l'appui, que Théo retient ou écarte. À utiliser dans ce dépôt à la clôture du troisième lot depuis la dernière revue de cap, à la clôture d'un jalon, ou quand Théo la demande, avant d'annoncer le lot suivant.
---

# La revue de cap

Le suivi du backlog dit si les tâches avancent, pas si elles servent le
but : un chantier qui tourne en boucle, ou une amélioration évidente que
personne ne propose, ne se voyait qu'à la question de Théo. La revue de
cap le regarde à intervalles fixes. Ses raisons : D-0145, B-0310,
J-2026-11-20-D, J-2026-11-20-E. C'est un essai, sans code ni contrôle.

## Quand

- À la clôture du troisième lot depuis la dernière revue de cap, ou à la
  clôture d'un jalon, avant d'annoncer le lot suivant. La dernière revue :
  l'entrée du journal titrée « Revue de cap » la plus récente
  (`grep -rn "Revue de cap" memory/journal/`) ; les lots clos depuis : ceux
  de `memory/backlog/closed/` dont la `ref` de clôture est plus récente.
- Quand Théo la demande.

## Qui

Un sous-agent neuf, sans worktree, qui ne mène aucun lot : il n'a pas
intérêt à finir celui en cours. Son modèle est celui du relecteur (le
chantier actif) ; sur celui de la session, il se lance sans `model`
(B-0251). Il lit et calcule ; il n'écrit rien dans le dépôt.

## Sa consigne

En tête : « Tu fais la revue de cap du dépôt memory, qui fabrique le
socle. AGENTS.md s'applique ; tu n'écris rien dans le dépôt. » Puis :

- **Le but** : D-0166, mot pour mot, la mesure de tout le reste : la
  mémoire, le bon contexte au bon moment et les tests automatisés qui
  guident l'agent ; rien contre un agent malveillant, ni autre chose.
  Puis D-0165, le cadrage, `memory/archives/cadrage-2026-10-10.md`, et le
  chantier actif, ses consignes et ses prochaines étapes.
- **La convergence, en tête du compte rendu** : depuis la dernière revue
  de cap, les entrées du backlog ouvertes et closes, celles ouvertes par
  une revue, et les besoins ouverts du jalon en cours. Si les ouvertures
  rattrapent les fermetures, c'est la première suggestion (J-2026-11-24-C).
- **La fenêtre** : depuis la dernière revue de cap, l'historique d'avant
  servant à voir les boucles ; pour la première, tout l'historique.
- **Les données**, par leurs commandes :
  - l'effort : `git log` sur `origin/main` (`--shortstat`, par dossier :
    `engine/socle/`, `tests/`, `memory/`, `docs/`) ; les lots clos et
    leurs tâches, dans `memory/backlog/closed/` ;
  - le backlog : `python3 .socle/socle roadmap --format markdown`,
    `python3 .socle/socle show --index backlog`, et le champ `origine` de
    chaque entrée, l'entrée du journal qui l'a ouverte (une revue de lot,
    une session réelle, une question de Théo) ;
  - le journal, `memory/journal/`, par `grep` plutôt qu'en entier ;
  - les décisions et demandes : `python3 .socle/socle show --index
    decisions`, `memory/requests/` (ce que Théo a demandé, refusé) ;
  - les coûts : les paragraphes « Coût » des entrées du journal qui
    closent ou relisent un lot, et `docs/fabrication/consommation.md`.
- **La question** : l'effort va-t-il là où est le but ? Et chaque
  suggestion qu'une revue d'avant a vu garder de côté (son entrée du
  journal, et la réponse de Théo) : tient-elle toujours, preuves
  relancées ?
- **Ce qu'il regarde** : où va l'effort par sujet (commits, lignes, lots,
  coûts) ; les boucles d'un lot à l'autre (un sujet qui revient, la
  correction d'une correction) ; l'origine des entrées, usage réel ou
  revue ; les angles morts : entrées anciennes jamais menées, doublons,
  frictions que le journal redit sans entrée, améliorations évidentes que
  personne ne propose.
- **Ce qu'il rend** : au plus trois suggestions, la plus utile d'abord,
  chacune avec ce qu'il propose, sa preuve (chiffrée, avec les
  identifiants, commits et commandes qui la redonnent) et ce qu'elle
  changerait. « Rien à suggérer » est une réponse. Puis, en quelques
  lignes, ce qu'il a regardé sans rien trouver.
- **Interdits** : écrire dans le dépôt, ouvrir une entrée, lire ou
  ajouter un autre dépôt ; une suggestion sans preuve. Sur le hook de
  l'agent, seule une preuve vue en session vaut (ADR-0098).
- « Économie : lire ce qui sert, pas les fichiers entiers ; compter par
  des commandes plutôt que lire. »

## Ce que l'orchestrateur en fait

1. Il vérifie chaque preuve, en relançant ses commandes ; une preuve qui
   ne tient pas fait tomber sa suggestion, et il le dit.
2. Il donne les suggestions à Théo dans la conversation, chacune
   compréhensible seule (ce que c'est, sa preuve, ce que changerait la
   retenir), et lui demande pour chacune : la retenir ou l'écarter. Rien
   n'entre au backlog sans son accord.
3. Au journal, une entrée « Revue de cap n » : la fenêtre, les
   suggestions et leurs preuves, celles tombées à la vérification, le
   modèle, les jetons et le coût en points de la fenêtre (lus par
   `list_events`). Poussée avant d'attendre la réponse, son lien donné.
4. La réponse de Théo se consigne en séance (skill `socle-request`) ; ce
   qu'il retient entre au backlog, au lot dont la règle s'applique ; ce
   qu'il garde de côté reste au journal et se rejuge à la revue suivante.
   Le journal tient le compte des revues dont il a retenu quelque chose.

## Jugée sur ses résultats

Après trois revues, B-0310 tranche : si Théo en a retenu des
suggestions, la revue de cap passe dans le produit ; sinon elle s'arrête
et ce skill se retire. Son coût visé : à peu près celui d'un relecteur,
tous les trois lots.
