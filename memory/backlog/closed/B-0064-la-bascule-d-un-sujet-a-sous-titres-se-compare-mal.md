<!-- socle: couche=backlog zone=publique -->
# B-0064 — La bascule d'un sujet à sous-titres se compare mal à une base d'avant la migration au format 3

> statut : fait · origine : J-2026-10-15-D · lu : backlog@4ee6266e · ref : J-2026-10-17-C

Constaté le 15 oct. en écrivant les tests du rangement des sujets clos :
un sujet qui a des sous-titres, migré du format 2 au format 3 (ses titres
remontent d'un niveau) puis basculé en privé, fait refuser
`memoire.ajout-seul` (« sa copie privée n'en reprend ni le titre ni le
texte ») quand la base comparée est d'avant la migration : le texte de la
base a ses sous-titres un niveau plus bas. Rare (migration et bascule dans
la même plage). Comparer les corps sans tenir compte du niveau des
sous-titres, avec un test qui échoue sans.
