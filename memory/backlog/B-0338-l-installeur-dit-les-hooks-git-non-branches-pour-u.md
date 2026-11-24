<!-- socle: couche=backlog zone=publique -->
# B-0338 — L'installeur dit les hooks git non branchés pour un core.hooksPath absolu qui désigne ceux de la racine, comme le démarrage avant T-0042

> statut : ouvert · origine : J-2026-11-23-R · lu : backlog@12a10d0c

Relevé par la passe 1 de la revue de L-0023 (J-2026-11-23-R), constat 5.
À une mise à jour, l'installeur (`engine/socle/installer.py`, où il
branche les hooks git) n'accepte que le chemin relatif des hooks du
socle, écrit tel quel, et imprime « !! core.hooksPath pointe ailleurs :
hooks git NON branchés » pour le chemin absolu des hooks de la racine :
la fausse alerte que T-0042 a corrigée au démarrage, et les deux disent
maintenant le contraire. Usage normal : une mise à jour dans un
conteneur cloud redémarré.

## Satisfait quand

- [ ] une mise à jour dans un dépôt dont `core.hooksPath` désigne les hooks de la racine par leur chemin absolu ne les dit pas débranchés
