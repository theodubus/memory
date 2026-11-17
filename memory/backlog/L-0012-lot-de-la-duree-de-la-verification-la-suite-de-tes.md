<!-- socle: couche=backlog zone=publique -->
# L-0012 — Lot de la durée de la vérification : la suite de tests sur plusieurs cœurs, la durée des étapes rapides dite et sous un seuil

> statut : en cours · origine : J-2026-11-16-I · après : L-0013, T-0044, T-0045 · lu : backlog@c0a47b1b · ancien : B-0266

Placé par Théo juste après L-0011, avant L-0005 (J-2026-11-16-I) :
`verify --fast` dure près de douze minutes sur un seul cœur, et chaque
lot en paie le prix (chaque push de plus de dix minutes, un implémenteur
qui ne finit pas sa vérification, le cache d'un sous-agent réécrit à
chaque attente). Ses deux sujets touchent la même étape, que juge une
seule revue : B-0257, la suite de tests de ce dépôt sur plusieurs cœurs,
dont le changement de `.socle/adapter.toml`, protégé, passe par une
demande à Théo ; B-0258, la durée de chaque étape dite et soumise à un
seuil, dont la spécification se soumet à Théo avant son code.

## Revues

### Passe 1 — 2026-11-17

Commits : cac8a20..8520f6a

- Bloquant : les liens de D-0130 sur un commit que la passation a réécrit, jamais poussé
- Bloquant : le point 3 de la spécification promet un avertissement en fin de tour et à l'envoi, que la marque des étapes déjà passées rend muet
- Bloquant : le seuil, un garde-fou nouveau, sans modèle de menace
- Ouvre : B-0281, T-0066, T-0067, T-0068
