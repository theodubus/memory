<!-- socle: couche=decisions zone=publique -->
# ADR-0007 — Chaque intervention qui a agi se termine par ce qui revient à l'humain

> statut : acceptée · date : 2026-10-10 · source : J-2026-10-10-M

## Contexte

Théo veut que chaque fin d'intervention dise ce qui l'attend : les décisions,
et les actions que lui seul peut faire, comme supprimer une branche distante
que le hook refuse à l'agent. La liste peut être vide, et l'agent peut
simplement attendre quelque chose (une CI, un match).

## Décision

- « Ce qui revient à l'humain » se calcule (`humain.py`) : les demandes sans
  réponse, les entrées du backlog marquées `pour : humain` et non closes, et
  les branches distantes que la branche par défaut contient en entier. L'état
  dérivé l'affiche à chaque démarrage.
- Une action que seul l'humain peut faire s'inscrit au backlog avec
  `pour : humain` ; elle se ferme, avec sa référence, quand il l'a faite.
- Le hook `Stop` exige, quand le tour a agi (arbre ou commit changé, ou outil
  externe appelé), que le dernier message de l'agent contienne une ligne
  « Pour toi : » ; sinon il bloque une fois, en donnant la liste calculée.
  Il lit ce message dans le transcript de Claude Code ; illisible, il le dit
  sans bloquer.

## Conséquences

- Un tour de pure conversation n'exige rien.
- Le marqueur est en français par défaut ; un projet le change dans sa
  politique (`[human] recap_marker`).
- Dépend du format du transcript de Claude Code ; les autres agents n'ont que
  la consigne d'`AGENTS.md`. Réversible : un appel à retirer du hook.
