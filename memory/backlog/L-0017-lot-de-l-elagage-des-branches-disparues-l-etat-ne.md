<!-- socle: couche=backlog zone=publique -->
# L-0017 — Lot de l'élagage des branches disparues : l'état ne donne plus à supprimer une branche que GitHub n'a plus

> statut : ouvert · origine : J-2026-11-12-O · après : L-0016, T-0024 · lu : backlog@b1dc0a69

Formé le 18 novembre pour T-0024, tirée de L-0007, après que Théo a
reçu une seconde fois la demande de supprimer deux branches qu'il avait
déjà supprimées (B-0193) : un défaut qui revient à chaque session coûte
plus que l'ordre des lots ne le justifie. Fichiers :
`engine/socle/human.py` (`branches_a_supprimer`) ou le hook de démarrage
qui va déjà chercher l'origine, ses tests, le guide si la ligne de l'état
change, une note de version. Après L-0016, avant L-0015.
