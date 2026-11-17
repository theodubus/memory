<!-- socle: couche=backlog zone=publique -->
# B-0183 — L'installeur ne signale pas un hook de fin de tour du projet qui double celui du socle

> statut : ouvert · origine : J-2026-11-12-A · priorité : basse · lu : backlog@df947470

À l'installation sur chess (`docs/fabrication/chess/installation-2026-11-12.md`, point 4) : l'installeur signale un
second état de démarrage, pas un second hook de fin de tour. chess avait le
sien, qui lance les mêmes douze étapes : 123 s pour lui et 122 s pour celui
du socle, à chaque fin de tour où un fichier de code attend son commit.
Relancé sur le même arbre, celui du socle ne prend que 3 s.

## Satisfait quand

- [ ] le « Fait quand » de T-0030 est tenu
