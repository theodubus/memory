<!-- socle: couche=backlog zone=publique -->
# B-0204 — Le hook de l'agent ne juge pas une commande précédée d'un mot du shell (then, do, else, !)

> statut : fait · origine : J-2026-11-13-H · ref : J-2026-11-14-AE · lu : backlog@f4a491f0

Le découpage des commandes (`commands.analyser`) ne retire pas les mots
réservés du shell qui précèdent une commande simple : dans `if true; then
rm .socle/policy.toml; fi`, la commande lue est `then rm …`, dont le
programme est `then`, et ni ses écritures ni ce qu'elle a d'irréversible ne
se jugent. `! rm .socle/policy.toml` passe de même, et `for f in *.md; do
sed -i … "$f"; done` n'est pas lu comme un `sed -i`. Les redirections, elles,
se jugent (`{ echo x; } > .socle/policy.toml` est refusé). Vu en mesurant
les faux refus de B-0171 ; un contournement du même garde-fou, que seul
`protege.fichiers` attrape ensuite. La piste : retirer `then`, `do`,
`else`, `elif`, `!`, `{`, `if`, `while`, `until` en tête d'une commande
simple, comme les préfixes.

## Modèle de menace

La règle 2 de D-0112 : le hook juge les formes du shell qu'un agent
coopératif écrit dans son travail. Une condition, une boucle ou un groupe
(`if`, `while`, `until`, `for`, `{ …; }`, `!`) en sont : un agent les
écrit pour traiter plusieurs fichiers ou un cas particulier.

Ce que le changement arrête : une écriture d'un fichier protégé, une action
irréversible ou une commande réservée à l'humain derrière `then`, `else`,
`elif`, `do`, `!`, `{`, `if`, `while` ou `until`, que le hook lisait comme
le programme `then` ; un `cd` ou une affectation dans le corps d'une
condition ou d'une boucle se suivent. Pour ne pas croire pris ce qui ne l'est
peut-être pas, ce qu'une condition ou une boucle change (son dossier, ses
variables) devient inconnu après elle, et dans la branche `else` ou `elif`
qui suit ; une condition ou une boucle dans un pipeline ou en tâche de fond
ne transmet rien à la suite, comme une commande simple. La variable d'un
`for` prend les mots de sa liste, que le jugement lit un à un : le corps se
lit une fois par mot, sa variable liée à ce mot (`for d in .socle memory;
do cd $d; …; done` se juge dans `.socle`, puis dans `memory`), et `for f in
*.md; do sed -i … "$f"; done` se juge par le motif `*.md`. Une boucle
revenue à son dossier le garde, sauf si un `break` ou un `continue` s'y lit
dans un autre dossier que celui où le tour finit : le tour d'après et la
suite de la boucle peuvent alors partir de l'un comme de l'autre, et leur
dossier est inconnu.

Ce qu'il laisse passer : une branche est lue comme prise tant qu'on y est
(un `cd` dans un `then` vaut pour la suite de ce `then`), comme un `cd` qui
échoue (un risque accepté, D-0111) : un saut écrit derrière un `||` qui suit
un `cd` (`cd "$d" || continue`) ne se lit pas ; dans un `while` ou un
`until`, ce qu'un tour change ne se voit que des commandes qui le suivent
dans le corps, pas du tour d'après, comme dans un `for` dont le dépliage
dépasserait sa borne (sa variable y est alors inconnue) ; un `select` ne se
déplie pas, sa variable est inconnue ; les motifs d'un `case` restent lus
comme avant, et le corps d'une fonction se juge sans que ce qu'il change
vaille pour la suite. `protege.fichiers` attrape ensuite l'écriture d'un fichier
protégé.

Ce qu'il refuse de plus, sans contournement : une écriture dans le corps
d'une boucle vers une variable que le hook ne connaît pas (`while read f;
do sed -i … "$f"; done`) se juge désormais, comme `read f; sed -i … "$f"`
hors d'une boucle : un chemin illisible dans le projet est refusé
(ADR-0072).

## Fait quand

- [x] une écriture d'un fichier protégé derrière `then`, `do`, `else` ou `!` est refusée par le hook, et un test le montre
