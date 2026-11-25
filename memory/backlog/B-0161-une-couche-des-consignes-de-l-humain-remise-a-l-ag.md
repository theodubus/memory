<!-- socle: couche=backlog zone=publique -->
# B-0161 — Une couche des consignes de l'humain, remise à l'agent au démarrage

> statut : ouvert · origine : J-2026-11-10-N · ref : D-0198, D-0200 · lu : backlog@4f7c8bab · après : B-0126

Les consignes durables de l'humain vivent dans le chantier actif, plein à
98 % de son budget, que chaque mise à jour oblige à resserrer ; le
journal n'est pas injecté au démarrage (constat 7, D-0093@333ad9d0, proposition 3).
Une couche de la mémoire, remise à l'agent au démarrage, où chaque
consigne est en vigueur ou levée, avec son texte exact ; le chantier
actif ne garde que le travail en cours. Sa spécification se soumet à Théo
avant son code.

Le 24 novembre, Théo retient la suggestion 3 de la revue de cap 4 (D-0172) : elle passe en premier après la mise à jour de chess (B-0323), avant la planification (B-0101).

Le 25 novembre, Théo la passe avant la mise à jour de chess (D-0198) : le
chantier actif est à 3 693 octets sur 3 700, ses consignes en font 87 %,
et un changement du format de la mémoire passe mieux dans la seule mise
à jour de chess. B-0323 l'attend.

Le 25 novembre, Théo valide l'intention (D-0200) : chaque consigne a un
identifiant, son texte exact, une ligne de résumé et un statut, en
vigueur ou levée, que seule sa parole lève ; le démarrage donne la ligne
de résumé de chaque consigne en vigueur ; l'agent lit le texte exact
quand il s'appuie sur une consigne, ce que le produit doit assurer. C'est
un changement du produit : chess le reçoit à sa mise à jour.

## Satisfait quand

- [ ] Théo a validé la spécification de la couche
- [ ] les consignes du chantier actif y sont, et l'état les injecte
- [ ] l'agent lit le texte exact d'une consigne avant de s'appuyer dessus, et un test montre ce qui le lui fait lire
