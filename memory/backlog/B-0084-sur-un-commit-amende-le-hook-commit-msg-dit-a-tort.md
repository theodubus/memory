<!-- socle: couche=backlog zone=publique -->
# B-0084 — Sur un commit amendé, le hook commit-msg dit à tort qu'un correctif n'a pas de test

> statut : ouvert · origine : commit:c198ed9 · lu : backlog@42b2ad8b

Le commit c198ed9 (le lint de D-0040) change `tests/test_demandes.py`.
Amendé pour y ajouter la doc d'architecture, il a fait dire au hook
`commit-msg` : « ce correctif n'ajoute ni ne change aucun test […] la CI
le refusera ». Le hook a comparé l'index au commit amendé, qui portait
déjà les tests, au lieu de le comparer à son parent. Le push et la CI
jugent la plage et ont passé : l'avertissement est faux, mais il pousse
à ajouter un test inutile. Le hook `prepare-commit-msg` reçoit `commit`
en second argument lors d'un `--amend` : de quoi juger contre `HEAD^`.
