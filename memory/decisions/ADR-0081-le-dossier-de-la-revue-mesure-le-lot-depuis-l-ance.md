<!-- socle: couche=decisions zone=publique -->
# ADR-0081 — Le dossier de la revue mesure le lot depuis l'ancêtre commun de sa base et de HEAD, refuse une référence qu'il ne peut mesurer, et ne prend pour barre que les sujets dont le lot change le statut ou le « Fait quand »

> statut : acceptée · date : 2026-11-15 · source : B-0213@8d5cff54, ADR-0075@831cdb1a, ADR-0073@1e48220c, ADR-0042@c8fe8e02, D-0111@034d5e87 · lu : decisions@c07371eb

## Contexte

Le dossier de `socle review` compare l'arbre à sa base par `git diff
<base>` (ADR-0042@c8fe8e02). Quand la base a avancé sans la branche (la
branche par défaut a reçu d'autres fusions, la branche distante un commit
poussé d'ailleurs), ses changements entrent dans le lot, à l'envers, et
les sujets qu'elle seule a touchés deviennent la barre du relecteur.
ADR-0075@831cdb1a n'a pris l'ancêtre commun que pour le lot déjà poussé,
et renvoie le cas général à B-0213@8d5cff54. Le même sujet relève qu'une
référence inconnue donne « rien à relire », code 0 ; qu'un `--since` qui
n'est pas un ancêtre de HEAD montre des changements étrangers ; qu'un
sujet touché en passant (un `après` changé, un constat ajouté, un sujet
clos rangé par `socle archive`) est donné en entier comme barre ; et, de
la revue de B-0212@11c126ca, des notes fausses ou muettes. Cette
décision est la spécification de B-0213, écrite avant son code.

## Décision

**La mesure.** Le lot se mesure depuis l'ancêtre commun de sa base et de
HEAD, quelle que soit la base : la branche distante, la branche par
défaut, l'ancêtre commun d'ADR-0075@831cdb1a ou un `--base` donné. Le
diff (l'arbre compris, la mémoire mise à part), les sujets et les
décisions que le lot écrit en partent. Quand cet ancêtre n'est pas la
base elle-même, le titre du diff le dit. Une branche distante qui a
reçu d'ailleurs un commit que HEAD n'a pas n'entre donc plus dans le
lot, ni à l'endroit ni à l'envers ; et elle contient le lot dès que rien
de HEAD et de l'arbre ne manque, hors de la mémoire, depuis cet ancêtre.

**Les refus.** `socle review` refuse, code 2, le message sur la sortie
d'erreur : un `--base` ou un `--since` que le dépôt ne connaît pas ; un
`--since` qui n'est pas un ancêtre de HEAD (il désigne le commit relu
par la première revue, que la branche contient) ; une base sans ancêtre
commun avec HEAD (un clone superficiel, une autre histoire). Un `--base`
qui n'est pas un ancêtre de HEAD reste admis : il se mesure depuis
l'ancêtre commun, c'est le cas de la branche par défaut qui a avancé.

**La barre.** Un sujet que le lot touche n'est donné en entier, comme
barre, que si le lot change son statut ou son « Fait quand », ses cases
ou leur texte, depuis l'ancêtre commun, ou s'il est nouveau et clos ; un
sujet nouveau encore ouvert garde son titre seul (ADR-0073@1e48220c). Un
sujet dont le lot ne change que le reste, ses métadonnées (un `après`),
sa description, ou sa place (`socle archive`), n'est pas dans le
dossier : ce n'est pas ce que le lot prétend faire.

**Les notes.** Sans `--base`, le dossier dit ce qu'il ne montre pas :
- la branche distante porte déjà des commits hors de la mémoire depuis
  l'ancêtre commun de HEAD et de la branche par défaut (un lot poussé en
  partie, ou des lots qui précèdent) : combien, et la commande pour un
  lot qui commence plus tôt ;
- la branche distante contient déjà le lot (ADR-0075@831cdb1a) : sur
  combien de commits porte la mesure depuis l'ancêtre commun ; ou, s'il
  n'y en a pas, la vraie raison : la branche par défaut n'est que
  devinée, HEAD n'a pas d'ancêtre commun avec elle dans ce clone, ou
  elle contient aussi le lot ;
- sous `--since`, la commande qu'elle propose garde `--since`.

La branche distante d'avant le dernier push (`<amont>@{1}`) n'est pas
proposée comme base : un fetch la déplace aussi, et un lot poussé en
plusieurs fois, une fin de tour chacune en session cloud, la ferait
commencer au milieu du lot. Ce serait une relecture partielle que rien
ne rattrape, pire que la relecture de trop qu'elle éviterait ; la note
et le skill `socle-review` disent de donner `--base <le commit d'avant
le lot>`, que l'agent connaît : la tête d'où le lot est parti.

**Le rapport aux décisions d'avant.** Cette décision complète
ADR-0075@831cdb1a, qui reste acceptée : sans `--base`, la base est
toujours choisie comme elle le dit, et un `--base` donné reste la base,
sans repli sur l'ancêtre commun avec la branche par défaut ; elle se
mesure seulement, comme toute base, depuis son ancêtre commun avec HEAD.
Elle précise « les sujets que le lot touche » d'ADR-0073@1e48220c.
Restent écartés, sur la décision de Théo (D-0111@034d5e87) : le lot de
mémoire seule, que la revue ne relit pas, et le `--since` posé sur la
branche par défaut.

## Conséquences

Le diff, les sujets et les décisions du dossier sont ceux du lot, même
quand sa base a avancé ; une faute de frappe dans une option se voit
aussitôt, au lieu d'un dossier vide qu'un relecteur jugeait sans constat.
Un sujet dont le lot ne change que le texte ou l'ordre ne fait plus la
barre : un lot qui avance un sujet sans en cocher de case ni en changer
le statut ne le donne plus à juger. La mesure coûte une lecture de la
mémoire à l'ancêtre commun. Se défait en revenant à `git diff <base>`
et à la seule liste des fichiers touchés dans `engine/socle/review.py`.
