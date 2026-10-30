<!-- socle: couche=backlog zone=publique -->
# B-0098 — Une session cloud neuve part de la branche par défaut : avant la fusion de l'installation, elle n'a pas le socle

> statut : fait · origine : J-2026-10-30-G · ref : J-2026-10-30-G · lu : backlog@e00eea09

Une session cloud de Claude Code démarre sur une branche neuve tirée de la
branche par défaut. Tant que la pull request qui installe le socle n'est
pas fusionnée, cette branche n'a ni le socle ni ses hooks : la session n'a
pas d'état au démarrage, et ses hooks ne tirent pas. Mesuré sur le
pilote : la session neuve est partie de `main`, qui n'avait que le README,
et s'est arrêtée.

L'ordre se dit donc là où l'installation se décrit : la session qui
installe ouvre une pull request ; l'humain la fusionne ; puis seulement une
session neuve. Fait dans le README et le guide, avec B-0097.
