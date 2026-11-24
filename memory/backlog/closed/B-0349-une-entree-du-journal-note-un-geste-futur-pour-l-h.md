<!-- socle: couche=backlog zone=publique -->
# B-0349 — Une entrée du journal note un geste futur pour l'humain, que l'agent recopie plus tard sans le vérifier : seul l'état calcule ce qui revient à l'humain

> statut : fait · origine : J-2026-11-24-AR · lu : backlog@e0df6c02 · ref : J-2026-11-24-AW, T-0175

Le 20 novembre, l'agent a donné à Théo une branche à supprimer que
GitHub n'avait plus, recopiée de J-2026-11-19-AK, qui la disait « à
supprimer après la fusion de la pull request » (B-0311). Le contrôle de
fin de tour la refuse désormais après coup (T-0126, D-0178). Théo a
demandé si l'on pouvait agir en amont ; aucun hook de Claude Code ne
voit le message final avant qu'il s'écrive, mais la fausse information
peut ne pas entrer dans la mémoire : une entrée du journal ne note
aucun geste futur pour l'humain, l'état seul calculant ce qui lui
revient, vérifié. Théo l'a validé en séance (D-0179), en plus du
contrôle.

## Satisfait quand

- [x] l'agent qui écrit une entrée du journal sait qu'elle ne note aucun geste futur pour l'humain, ce que l'état calcule
