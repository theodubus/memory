<!-- socle: couche=backlog zone=publique -->
# B-0278 — La consigne des sous-agents de socle-batch ne dit rien de l'économie : lire ce qui sert, pas les fichiers entiers, ni relancer la suite complète sans raison

> statut : ouvert · origine : J-2026-11-17-H · ref : D-0129 · lu : backlog@1df796e8

Théo veut dans le produit (D-0129) la ligne « Économie » que le skill
`delegate-lot` de l'atelier ajoute à la consigne des sous-agents :
« lire ce qui sert, pas les fichiers entiers ; pas de suite complète
relancée sans raison ». La consigne du skill `socle-batch` n'en dit rien,
alors qu'un sous-agent qui implémente lit environ 320 000 jetons, 3 à 4
points de la semaine, et qu'une suite complète relancée sans raison
coûte des minutes à chaque fois.

## Satisfait quand

- [ ] la consigne des sous-agents que donne le produit leur dit d'économiser leur lecture et leurs vérifications
