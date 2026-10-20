<!-- socle: couche=backlog zone=publique -->
# B-0054 — Deux états au démarrage quand le projet a déjà le sien

> statut : fait · origine : J-2026-10-12-Q · lu : backlog@a1cd520a · ref : J-2026-10-20-H

Mesuré à R6 : le projet d'échecs a déjà son état au démarrage
(`chess:tools/etat.sh`), et l'installeur ajoute celui du socle ; chaque
session en reçoit deux, qui se recoupent (branche, commits non fusionnés,
ce qui revient à l'humain). L'installeur pourrait le signaler, et la
documentation dire comment n'en garder qu'un.
