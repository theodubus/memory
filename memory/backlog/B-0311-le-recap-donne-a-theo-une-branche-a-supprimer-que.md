<!-- socle: couche=backlog zone=publique -->
# B-0311 — Le récap donne à Théo une branche à supprimer que GitHub n'a plus : l'agent la reprend du journal sans la vérifier, le contrôle de l'état ne voit pas le récap

> statut : ouvert · origine : J-2026-11-20-Q · priorité : haute · lu : backlog@76b9b65b · ref : B-0193, ADR-0090, J-2026-11-19-AK

Le 20 novembre, l'agent a demandé plusieurs fois à Théo, dans « Pour
toi », de supprimer la branche distante `ccr-f176849a-qbyj74`, que
GitHub n'avait plus. Théo, mot pour mot : « Pour la branche a supprimer
ça fait plusieurs fois que tu me le demandes alors qu'elle etait deja
supprimée, normalement le fait de check a deja été réglé mais
visiblement pas correctement ».

Le correctif de B-0193@047e5731 (ADR-0090) tient : l'état demande à
l'origine les branches qu'elle a encore, et ne donnait pas celle-ci.
L'agent l'a reprise ailleurs : l'entrée J-2026-11-19-AK, écrite par la
session d'avant, dit de la branche de passation qu'elle « est à
supprimer après la fusion de la pull request », et l'agent l'a recopiée
dans son récap sans la vérifier sur GitHub, contre la consigne du
chantier actif. Le clone gardait aussi sa référence, faute d'élagage :
`git branch -r` la montrait encore. Le contrôle vit dans l'état ; le
récap, que l'agent écrit, n'en a aucun. Quatrième fois au moins que
Théo le relève (B-0193).

Pistes : le hook de fin de tour juge les branches nommées dans « Pour
toi » contre l'origine (`git ls-remote --heads origin`), comme il juge
déjà le lien d'une demande citée ; c'est le hook de l'agent, qui ne
s'ouvre que sur une preuve vue en session (ADR-0098) : celle-ci en est
une. Ou une entrée du journal ne donne pas de geste futur à l'humain,
l'état seul les calculant.

## Satisfait quand

- [ ] un récap ne peut pas donner à l'humain une branche à supprimer que l'origine n'a plus
