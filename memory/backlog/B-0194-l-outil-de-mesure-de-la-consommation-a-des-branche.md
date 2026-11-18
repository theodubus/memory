<!-- socle: couche=backlog zone=publique -->
# B-0194 — L'outil de mesure de la consommation a des branches qu'aucun test n'exerce

> statut : ouvert · origine : J-2026-11-12-N · priorité : basse · lu : backlog@d4ceca3b

La seconde revue de la mesure de B-0173 a trouvé, dans
`bench/consumption.py`, des branches que des mutations changent sans
qu'aucun des tests de `tests/test_banc_consommation.py` n'échoue : la
coupure des suites de relevés quand la fenêtre repart à zéro
(`_segments`) ; dans `fourchette`, un poids impossible, une borne haute
infinie et l'appariement des bornes du point ; le contrôle hors
échantillon qu'un compactage empêche, et la valeur par défaut des autres
modèles ; le plafond et la garde du contexte nul de `presence_socle` ;
une fenêtre qui repart à zéro dans `points_de_semaine` ; un sous-agent
sans appel dans `concurrence` ; l'en-tête anglais de la section du socle.
L'outil est de l'atelier et ses chiffres sont recalculés par deux
revues ; ces tests protègent ses mesures à venir.

## Satisfait quand

- [ ] une mutation de l'outil de mesure de la consommation, dans les branches que la revue a nommées, ne passe plus inaperçue
