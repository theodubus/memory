<!-- socle: couche=backlog zone=publique -->
# B-0266 — Lot de la durée de la vérification : la suite de tests sur plusieurs cœurs, la durée des étapes rapides dite et sous un seuil

> statut : ouvert · origine : J-2026-11-16-I · forme : lot · après : B-0269, B-0257, B-0258 · lu : backlog@c0a47b1b

Placé par Théo juste après B-0264, avant B-0235 (J-2026-11-16-I) :
`verify --fast` dure près de douze minutes sur un seul cœur, et chaque
lot en paie le prix (chaque push de plus de dix minutes, un implémenteur
qui ne finit pas sa vérification, le cache d'un sous-agent réécrit à
chaque attente). Ses deux sujets touchent la même étape, que juge une
seule revue : B-0257, la suite de tests de ce dépôt sur plusieurs cœurs,
dont le changement de `.socle/adapter.toml`, protégé, passe par une
demande à Théo ; B-0258, la durée de chaque étape dite et soumise à un
seuil, dont la spécification se soumet à Théo avant son code.
