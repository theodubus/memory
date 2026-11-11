<!-- socle: couche=backlog zone=publique -->
# B-0164 — Dans un worktree, le hook de l'agent juge les références contre la mémoire de la copie principale

> statut : fait · origine : J-2026-11-11-E · lu : backlog@9cfef466 · ref : J-2026-11-11-L

Un sous-agent qui travaille dans un worktree de ce dépôt crée une entrée
de mémoire (`socle new`) dans le worktree, puis veut l'écrire par l'outil
d'édition : le hook avant outil juge ses références contre la mémoire de
la copie principale du dépôt, où l'entrée n'existe pas encore, et la
refuse comme référence inventée. Les sous-agents la contournent en
écrivant la mémoire par des scripts lancés par le shell, que le hook ne
juge pas. Le hook devrait juger un fichier contre la mémoire du worktree
qui le contient.

Fait quand :
- [x] une entrée créée dans un worktree s'écrit par l'outil d'édition sans refus pour référence inventée, et un test le montre
