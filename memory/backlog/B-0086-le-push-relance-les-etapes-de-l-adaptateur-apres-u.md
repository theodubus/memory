<!-- socle: couche=backlog zone=publique -->
# B-0086 — Le push relance les étapes de l'adaptateur après un commit qui ne change pas le code

> statut : ouvert · origine : J-2026-10-29-B · lu : backlog@b8f4fad9

Relevé par l'essai à blanc sur chess. Les étapes rapides de l'adaptateur
(la compilation et les tests, en minutes sur chess) ne se relancent pas
sur un arbre qui les a déjà passées ; mais l'empreinte de l'arbre contient
le SHA du commit. Après la fin de tour, un commit qui ne change rien au
contenu, ou qui ne change que la mémoire, les relance au push. Les étapes
ne lisent pas la mémoire, que les contrôles du socle jugent de leur côté :
l'empreinte doit être celle du contenu, mémoire mise à part.
