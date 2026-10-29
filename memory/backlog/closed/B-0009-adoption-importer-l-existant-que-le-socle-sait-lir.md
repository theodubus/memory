<!-- socle: couche=backlog zone=publique -->
# B-0009 — Adoption : importer l'existant que le socle sait lire

> statut : fait · origine : J-2026-10-10-F · ref : J-2026-10-29-D

Les plafonds de mutation de chess ont été repris à la main
(`docs/fabrication/chess/mutation-caps.toml`). L'adoption pourrait proposer cette
reprise, et celle des tables « Ce qui tourne tout seul ».

Rouvert le 29 oct. (J-2026-10-29-B) : l'essai à blanc sur chess montre que
les plafonds qu'un projet a déjà mesurés se perdent à l'adoption, jusqu'au
premier balayage, qui prend des heures sur chess. L'abandon du 22 oct.
supposait qu'un balayage les remesure vite. Reste à faire : que
l'installation en adoption reprenne des plafonds mesurés ailleurs, d'un
fichier que l'humain donne, au lieu de poser ces modules « à mesurer ».
