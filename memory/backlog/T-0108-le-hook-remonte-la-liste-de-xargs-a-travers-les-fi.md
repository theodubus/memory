<!-- socle: couche=backlog zone=publique -->
# T-0108 — Le hook remonte la liste de xargs à travers les filtres de lignes (grep sans -r ni -o, sort, uniq, head, tail, cat, tee) jusqu'au find qui la produit

> statut : ouvert · origine : commit:3e83907e · besoin : B-0306 · priorité : haute · lu : backlog@aa725b6b

Un commit : le producteur de la liste d'un `xargs` se cherche en
remontant le pipeline à travers les filtres qui ne font que retirer ou
réordonner des lignes (`grep` sans `-r` ni `-o`, `sort`, `uniq`,
`head`, `tail`, `cat` sans fichier, `tee`), jusqu'au `find` qui la
produit ; ses cas dans `tests/test_garde.py`.

## Fait quand

- [ ] `find .. -maxdepth 0 | grep . | xargs rm -rf` et `find . -type f | grep -v x | xargs rm` sont refusés comme la suppression du projet, de même avec `sort`, `uniq`, `head` ou `tail` entre le `find` et `xargs`, et un test le montre
- [ ] `find build -type f | grep -v keep | xargs rm -f` passe, et un test le montre
