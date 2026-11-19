<!-- socle: couche=backlog zone=publique -->
# B-0277 — Le relecteur d'une revue reçoit le chemin de son dossier, pas son texte : le dossier recopié dans la conversation qui orchestre s'y relit à chaque appel

> statut : fait · origine : J-2026-11-17-H · ref : D-0129, J-2026-11-19-G · lu : backlog@fc0acdb0

Théo veut dans le produit (D-0129) cette pratique de l'atelier : le
relecteur reçoit le chemin du dossier de la revue, pas son texte. Le
skill `socle-review` fait envoyer au relecteur le dossier tel quel, comme
seul message : son texte reste alors dans la conversation qui
orchestre, et chaque appel suivant le relit (24 Ko pour la passe 3 du
lot L-0013). Le skill `delegate-lot` de l'atelier range déjà le dossier
dans un fichier et n'en donne que le chemin.

Ce qui ne change pas : le relecteur lit le dossier en entier et le suit
tel quel ; rien ne s'ajoute à la consigne, ni ne s'en retire. Les
« points à éprouver » que l'atelier ajoute ne passent pas dans le
produit.

## Satisfait quand

- [x] le dossier d'une revue n'entre plus dans la conversation qui orchestre, et le relecteur le reçoit en entier
