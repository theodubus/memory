<!-- socle: couche=backlog zone=publique -->
# B-0065 — Passer la CI de ce dépôt aux actions qui tournent sur Node 24

> statut : ouvert · origine : J-2026-10-17-B · pour : humain · lu : backlog@c100e7fc

Les workflows que pose le socle passent aux actions qui tournent sur
Node 24 (B-0062) ; la CI de ce dépôt, fichier protégé que toi seul modifies,
garde les anciennes, que GitHub force déjà sur Node 24 en prévenant de la
dépréciation de Node 20. Dans `.github/workflows/socle.yml` :

1. remplacer `actions/checkout@v4` par `actions/checkout@v5` ;
2. remplacer `actions/setup-python@v5` par `actions/setup-python@v6`.

Puis `python3 .socle/socle approve --text "les actions de la CI sur Node 24"`
et commiter. Rien ne casse en attendant : GitHub n'émet qu'un avertissement.
