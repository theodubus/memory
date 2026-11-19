<!-- socle: couche=decisions zone=publique -->
# ADR-0096 — La garde d'une action d'un find est une disjonction de conjonctions de filtres, et le motif d'un -path se lit sur son départ

> statut : acceptée · date : 2026-11-19 · source : B-0231@dffbca68, T-0003@3abbf8f0, ADR-0082@beb85978, ADR-0095@d1b09f89 · lu : decisions@ce0859f2

## Contexte

`_expression_find` (`engine/socle/hooks.py`) fusionnait les filtres des
branches d'une expression en un seul tuple, et `_supprime_par_find`
jugeait chaque filtre seul : `find . -name '*.json' -path './build/*'
-delete` était refusé parce que `-name '*.json'` seul croiserait un
réglage de Claude Code, et `find build -path '*.toml' -delete` parce que
l'étoile de tête d'un `-path` se lisait depuis la racine du projet
(B-0231@dffbca68). Des faux refus dans un nettoyage ciblé, qu'un agent
écrit dans son travail.

## Décision

- **La forme d'une garde.** Une disjonction de conjonctions de filtres :
  `-a` joint chaque conjonction de l'une à chacune de l'autre, `-o` et
  `,` les mettent côte à côte, une conjonction vide laisse passer sans
  filtre. Au-delà de 64 conjonctions, une garde se lit plus large (`-a` :
  l'une des deux gardes seule, hors d'une garde libre ; `-o` : chaque
  filtre seul) : un refus de trop, jamais un trou.
- **Le jugement.** Chaque conjonction se juge à part : chacun de ses
  filtres se lit comme des motifs depuis la racine (un nom à toute
  profondeur sous le départ, un chemin par ce qui peut suivre le départ),
  et un fichier protégé n'est visé que s'il répond à un motif de chacun.
  Un fichier présent se compare à chaque motif ; un motif de chemin
  protégé, à tous les motifs à la fois (`commandes.se_croisent_tous`, un
  parcours du produit des motifs, au plus 200 000 états, au-delà dits se
  croiser). Au-delà de 32 combinaisons d'un motif par filtre, une
  conjonction ne garde que ses premiers filtres, plus large.
- **Le motif d'un `-path`.** Il se lit sur ce que `find` écrit devant un
  chemin du projet (son départ, et ce qui mène de lui à la racine), part
  par part, sans égard à la casse ; chaque reste qui peut suivre vise ce
  qui est sous le départ, et rien d'autre (`_motifs_de_chemin`). Une classe
  ou un `?` lus dans le départ y rendent tout caractère.

## Conséquences

- La sortie d'un `find` qu'un `xargs` lit (ADR-0095@d1b09f89) se garde de
  la même forme.
- Le croisement de deux motifs garde son parcours à deux suites, sans
  borne d'états : le jugement de tout chemin écrit n'en paie pas le coût.
- Pour défaire : revenir à un seul tuple de filtres, chacun jugé seul,
  plus large ; rien de ce qui est refusé aujourd'hui ne passerait.
