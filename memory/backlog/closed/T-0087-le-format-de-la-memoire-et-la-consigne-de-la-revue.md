<!-- socle: couche=backlog zone=publique -->
# T-0087 — Le format de la mémoire et la consigne de la revue disent l'exception de D-0133 : une case qui livre une demande, un relevé ou une entrée de la mémoire se vérifie par ce qu'elle produit

> statut : fait · origine : J-2026-11-18-M · besoin : B-0265 · lu : backlog@d531d84b · ref : J-2026-11-19-H

ADR-0088 écrit l'exception que Théo a validée par D-0133 : une case du
critère d'une tâche qui livre une demande posée, un relevé écrit ou une
entrée de la mémoire récrite se vérifie par ce qu'elle produit. Le format
de la mémoire (`engine/socle/FORMAT.md`, la tâche, vers la ligne 159) dit
encore la règle d'avant, et la consigne du relecteur (`engine/socle/review.py`)
ne lui dit pas comment juger ces cases. Le livrable, un commit : le format
et la consigne disent l'exception, dans les deux langues, avec une note de
version, et le prompt de mise à jour de chess le reprend.

## Fait quand

- [x] le format de la mémoire dit l'exception d'ADR-0088, et un test le lit
- [x] la consigne du dossier de la revue dit comment juger une case de ces trois livrables, dans les deux langues, et un test le lit
