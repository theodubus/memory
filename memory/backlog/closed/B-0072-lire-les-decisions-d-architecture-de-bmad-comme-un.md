<!-- socle: couche=backlog zone=publique -->
# B-0072 — Lire les décisions d'architecture de BMAD comme une couche de décisions du socle

> statut : fait · origine : J-2026-10-20-A · lu : backlog@9b2e2382 · ref : J-2026-10-20-J

Laissé pour plus tard par la décision du mariage (ADR-0032@294aa890) : le document
d'architecture de BMAD porte des décisions numérotées (AD-1, AD-2…), à
identifiants stables, que son propre script vérifie. Le socle les lirait
comme une couche de décisions : dans l'index de l'état, avec la lecture
prouvée (`AD-n@empreinte`) avant de s'appuyer sur l'une, et la règle « on
ne rouvre pas une décision sans fait nouveau ». Les ADR du socle restent
pour les décisions hors de l'architecture. À régler : le format exact des
décisions de BMAD, qu'un essai réel de son workflow d'architecture
montrera.
