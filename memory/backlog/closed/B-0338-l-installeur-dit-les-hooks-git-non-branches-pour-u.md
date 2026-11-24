<!-- socle: couche=backlog zone=publique -->
# B-0338 — L'installeur dit les hooks git non branchés pour un core.hooksPath absolu qui désigne ceux de la racine, comme le démarrage avant T-0042

> statut : abandonné · origine : J-2026-11-23-R · lu : backlog@12a10d0c · ref : D-0168

Relevé par la passe 1 de la revue de L-0023 (J-2026-11-23-R), constat 5.
À une mise à jour, l'installeur (`engine/socle/installer.py`, où il
branche les hooks git) n'accepte que le chemin relatif des hooks du
socle, écrit tel quel, et imprime « !! core.hooksPath pointe ailleurs :
hooks git NON branchés » pour le chemin absolu des hooks de la racine :
la fausse alerte que T-0042 a corrigée au démarrage, et les deux disent
maintenant le contraire. Usage normal : une mise à jour dans un
conteneur cloud redémarré.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X2 — imaginé par un relecteur, jamais vu, rattrapé ou bénin » : une fausse alerte de l'installeur, hooks git dits débranchés, à la mise à jour dans un conteneur redémarré. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] une mise à jour dans un dépôt dont `core.hooksPath` désigne les hooks de la racine par leur chemin absolu ne les dit pas débranchés
