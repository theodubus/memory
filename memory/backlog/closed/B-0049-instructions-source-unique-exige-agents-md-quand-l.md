<!-- socle: couche=backlog zone=publique -->
# B-0049 — instructions.source-unique exige AGENTS.md quand l'installeur a gardé CLAUDE.md comme source

> statut : fait · origine : J-2026-10-12-M · lu : backlog@ca384505 · ref : J-2026-10-13-C

Mesuré à R6, sur un clone du projet d'échecs : l'installeur garde
CLAUDE.md comme source (35 fichiers du projet le nomment) et y ajoute la
section du socle, mais le contrôle exige AGENTS.md et un CLAUDE.md réduit à
`@AGENTS.md`. En adoption, c'est un avertissement à tort, et permanent. Le
contrôle doit accepter la source que l'installeur a choisie. Le `.gitignore`
posé dans ce cas renvoie lui aussi à AGENTS.md, absent.
