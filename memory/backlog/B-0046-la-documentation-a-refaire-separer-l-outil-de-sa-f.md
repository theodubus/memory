<!-- socle: couche=backlog zone=publique -->
# B-0046 — La documentation à refaire : séparer l'outil de sa fabrication, et la rendre intuitive

> statut : ouvert · origine : J-2026-10-12-F · lu : backlog@19253d8c

Signalé par Théo, texte exact : « la doc mélange la doc/tests relatif au
repo (ce qui permet de construire l'outil de cadrage) et l'outil de cadrage
lui meme, + la doc est pas intuitive pour comprendre ni installer, à refaire
(si c'est pas clair en quoi c'est pas bien pour toi, tu pourra me demander
> backlog) ». Ce que j'en comprends : le README et `docs/` mêlent la
documentation du socle, pour qui l'installe et s'en sert, et le matériel
de sa fabrication dans ce dépôt (architecture, bancs, relevés,
inventaire de `chess`) ; il faut les séparer, et réécrire la première pour
qu'elle se comprenne et s'installe sans effort : ce que c'est en un
paragraphe, l'installation en quelques commandes qui marchent telles
quelles, une première session, l'usage courant, puis la référence. Avant
de commencer, vérifier cette lecture avec Théo, et lui demander où il
s'est perdu. Reprend B-0035, clos trop tôt.

Le 20 oct., Théo précise sa lecture et la priorité (J-2026-10-20-Q) : la
documentation passe avant le projet pilote ; elle distingue ce qui est
copié dans un projet de ce qui fabrique l'outil, et explique simplement le
fonctionnement, les principes et l'installation, avec des schémas si
besoin. Le plan :

1. Le README dit dès le début, avec un schéma, que le dépôt a trois parts :
   le produit (`engine/socle/`, ce que l'installation copie ou pose dans
   un projet), sa fabrication (`tests/`, `bench/`, la documentation de
   fabrication), et le socle appliqué à ce dépôt lui-même (`memory/`, le
   dossier `.socle`, `AGENTS.md`), exactement ce qu'un projet reçoit, ici
   rempli par le développement de l'outil.
2. La documentation du produit : le README (ce que c'est, comment ça
   marche, l'installation en quelques commandes, ce qu'un projet reçoit),
   et un document du fonctionnement et des principes, qui remplace
   l'ancien document du socle (fondu depuis dans le README et le guide
   d'utilisation, D-0038) ; le guide de l'humain (`engine/socle/HELP.md`) reste
   celui que l'installation pose.
3. La documentation de fabrication rejoint un dossier à part : architecture,
   bancs, passe de recul, parcours, et l'histoire des échecs (le socle est
   né des garde-fous écrits à la main dans le projet d'échecs de Théo).
4. Des schémas que GitHub dessine (mermaid) : les trois parts du dépôt, ce
   que l'installation pose, la boucle agent, contrôles, humain, le trajet
   d'une demande.
