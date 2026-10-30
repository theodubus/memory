<!-- socle: couche=backlog zone=publique -->
# B-0099 — BMAD s'installe avec un profil par défaut que les sessions cloud perdent : nom, langue, niveau

> statut : abandonné · origine : J-2026-10-30-M · lu : backlog@e00eea09 · ref : J-2026-10-30-Q

`--with-bmad` installe BMAD Method sans répondre à ses questions : le
niveau de l'utilisateur reste « intermediate », alors que BMAD propose
« expert — Be direct and technical », et le nom de l'utilisateur n'est pas
celui de l'humain. Ces réponses, de portée personnelle, tombent dans
`_bmad/config.user.toml`, que git ignore : une session cloud neuve ne les a
plus, et BMAD retombe sur ses valeurs de base (`user_name = "BMad"`,
`communication_language = "English"`). Mesuré sur une copie du pilote.

L'installeur devrait écrire ce profil dans `_bmad/custom/config.toml`, qui
se commite et que l'installeur de BMAD ne touche pas : le nom de l'humain
(`--human`), la langue de la mémoire, et un niveau qu'il choisit, « expert »
par défaut pour un humain qui délègue le code sans déléguer les
décisions. À trancher avec la place que Théo garde à BMAD sur le pilote.

Abandonné : BMAD est retiré du socle (D-0051, J-2026-10-30-Q), il n'y a
plus de profil à poser.
