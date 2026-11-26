<!-- socle: couche=backlog zone=publique -->
# T-0200 — La migration du backlog laisse ses renommages hors de l'index

> statut : fait · origine : J-2026-11-26-AA · besoin : B-0357 · lu : backlog@35e9325c · ref : J-2026-11-26-AL

`migration.migrer_backlog` renomme les lots et les jalons, puis les met
dans l'index (`git add -A -- avant apres`) : le commit de la demande
seule les emporte. Il ne les y met plus ; `git add -A`, au commit des
fichiers de la mise à jour, les prend avec le reste, et git reconnaît
les renommages à la lecture du diff, non à l'indexation.

## Fait quand

- [x] un test migre un backlog suivi par git et vérifie que l'index est inchangé (`git diff --cached` vide), les fichiers renommés présents dans l'arbre
