<!-- socle: couche=backlog zone=publique -->
# B-0156 — Le contexte long : une solution automatique, plutôt qu'une session neuve à ouvrir à la main

> statut : ouvert · origine : J-2026-11-10-N · lu : backlog@877a7268

Théo, le 10 novembre (J-2026-11-10-N) : ouvrir une session neuve à chaque
sujet est une friction majeure en session cloud ; il veut une solution
automatique qui retire le contexte inutile : un compactage agressif, une
suppression de contexte, ou l'agent qui crée et initialise la session
suivante et archive la sienne. La proposition 2 de D-0093@333ad9d0, où le compte
rendu proposait une session neuve, se reformule ainsi.

Mesuré ce jour-là : avec une conversation d'environ 500 000 jetons,
chaque appel coûte autour de 1,4 % de la fenêtre de cinq heures, et un
silence de plus d'une heure fait relire toute la conversation au prix
fort. Pistes à essayer : le compactage que l'humain lance d'une commande,
après lequel le socle réinjecte l'état ; le relais de session par
l'agent, avec les outils de la session cloud ; un sous-agent au contexte
neuf par sujet. À cadrer avec Théo, sur un essai.

## Fait quand

- [ ] Théo a choisi la solution sur un essai, et le socle la met en œuvre
