<!-- socle: couche=backlog zone=publique -->
# B-0062 — Les actions GitHub des workflows posés tournent sur un Node déprécié

> statut : ouvert · origine : J-2026-10-15-C · lu : backlog@66518ff8

Mesuré le 15 oct., dans les journaux de la CI des cinq projets jetables
sur GitHub : `actions/checkout@v4` et `actions/setup-python@v5`, que posent
les gabarits des workflows (`engine/socle/templates/socle.yml` et
`engine/socle/templates/mutation.yml`, et leurs versions anglaises), visent
Node 20, que GitHub force déjà sur Node 24 en prévenant de sa dépréciation.
Passer aux versions qui visent Node 24, après avoir vérifié lesquelles
existent, puis faire de même pour les actions des adaptateurs
(`setup-node`, `setup-go`, `setup-java`, `setup-ruby`, `setup-php`) ; la CI
de ce dépôt (`.github/workflows/socle.yml`) est protégée et revient à
l'humain.

Le 15 oct., les journaux du balayage sur GitHub ajoutent `setup-node@v4`,
`setup-go@v5` et `setup-java@v4` à la liste (J-2026-10-15-K).
