<!-- socle: couche=backlog zone=publique -->
# L-0017 — Lot de l'élagage des branches disparues : l'état ne donne plus à supprimer une branche que GitHub n'a plus

> statut : en cours · origine : J-2026-11-12-O · après : L-0016, T-0024 · lu : backlog@b1dc0a69

Formé le 18 novembre pour T-0024, tirée de L-0007, après que Théo a
reçu une seconde fois la demande de supprimer deux branches qu'il avait
déjà supprimées (B-0193) : un défaut qui revient à chaque session coûte
plus que l'ordre des lots ne le justifie. Fichiers :
`engine/socle/human.py` (`branches_a_supprimer`) ou le hook de démarrage
qui va déjà chercher l'origine, ses tests, le guide si la ligne de l'état
change, une note de version. Après L-0016, avant L-0015.

## Revues

### Passe 1 — 2026-11-18

Commits : 169b8b4..e5fe77f
- Bloquant : un test de L-0016 exige que la note du rendu reste la plus récente, et la note 2026-11-18-d le fait échouer
- Bloquant : une branche inactive que l'origine n'a plus ne dit plus d'étiqueter le commit cité que sa référence garde seule
- Ouvre : B-0292, T-0101

Recul : c'est la première passe du lot, sans bloquant d'avant à qui
comparer. Le premier bloquant vient d'un test du lot précédent, L-0016,
qui liait son assertion à la place de sa note plutôt qu'à son
identifiant ; le second, d'un filtre ajouté au calcul des branches sans
suivre l'un de ses usages, l'étiquette d'un commit cité (B-0116). Les
deux ont des causes distinctes. Le lot ferme T-0024 ; il ouvre B-0292 et
T-0101, un défaut voisin de même cause que B-0193 : une référence que
l'origine n'a plus, ici la branche de travail poussée. Les lots clos qui
ont touché `engine/socle/human.py` (B-0145, B-0112, B-0116) ont ouvert
des entrées de la même famille, chacune une lecture des branches
distantes. La correction tient en quelques lignes et un test, sans
conception nouvelle : pas de passe de plus. Décision : continuer
