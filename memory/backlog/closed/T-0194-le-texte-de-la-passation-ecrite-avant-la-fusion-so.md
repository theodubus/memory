<!-- socle: couche=backlog zone=publique -->
# T-0194 — Le texte de la passation écrite avant la fusion : socle-handoff, socle-batch, le guide, la note de version et le prompt de chess

> statut : fait · origine : D-0211 · besoin : B-0356 · lu : backlog@cfcbc7c6 · ref : J-2026-11-26-S, J-2026-11-26-R, J-2026-11-26-J, J-2026-11-26-W

Sur la réponse de Théo à la question d'intention de B-0356, « Texte
seul » (D-0211), et l'essai réussi du 26 novembre (J-2026-11-26-S) : le
produit écrit l'ordre éprouvé, sans code ni contrôle neuf.

## Spécification

- **La règle.** Une session qui change de session écrit sa passation
  avant toute fusion de sa pull request : quand l'agent la fusionne
  lui-même, la passation en est le dernier commit, `--waiting` disant la
  fusion à venir. La fusion la porte sur la branche par défaut, où
  `handoff check` la trouve déjà (il lit toutes les branches distantes) ;
  la branche, que l'hébergeur supprime à la fusion, ne se repousse plus,
  rien ne se poussant après elle. Quand l'humain fusionne, rien ne change :
  la passation se pousse sur la branche de la pull request ouverte.
- **Un commit nécessaire après la passation**, avant la fusion (une CI
  rouge), réécrit la passation dans ce même commit, comme avant.
- **Où.** Le skill `socle-handoff`, « Écrire la passation » ; le skill
  `socle-batch`, « Changer de session » (la passation, avant toute
  fusion), dans la marge de 4 octets : le renvoi au skill `socle-handoff`
  de sa première phrase, que sa dernière redit, se retire ; leurs versions
  anglaises ; le guide et sa version anglaise ; la note de version
  2026-11-26-c ; un point du prompt de chess.
- **Ce qui ne change pas.** Le code : la garde trouve déjà la passation
  sur la branche par défaut ; le hook de l'agent (C-0004@00db74e5).

## Fait quand

- [x] les skills `socle-handoff` et `socle-batch`, en français et en anglais, disent la passation écrite avant toute fusion, et le dernier commit de la pull request quand l'agent la fusionne ; leurs copies protégées sont remises par l'installeur
- [x] le guide, en français et en anglais, le dit, avec ce qu'il évite à l'humain : une branche de session à supprimer
- [x] la note de version 2026-11-26-c, en français et en anglais, et un point du prompt de chess le disent
- [x] les tests qui lisent ce texte lisent les phrases nouvelles
