<!-- socle: couche=backlog zone=publique -->
# B-0117 — Un commit cité qui n'est plus que dans une pull request se dit absent du dépôt

> statut : fait · origine : J-2026-11-01-C · lu : backlog@4cc6e0f8 · ref : J-2026-11-01-E

J-2026-10-31-S cite, sous la forme `commit:`, la tête d'une branche
supprimée depuis. GitHub garde ce commit, qui est la tête de la PR #10,
mais un clone ne récupère que les branches et les étiquettes : la CI le
disait absent, et restait rouge. Un projet qui fusionne en écrasant les
commits y butterait à chaque branche effacée.

Correctif : avant de dire absent un commit cité, le contrôle récupère une
fois les têtes des pull requests de l'origine. Sans origine ni réseau,
rien ne change. Un test l'établit, qui échoue sans le correctif.
