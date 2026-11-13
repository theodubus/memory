<!-- socle: couche=decisions zone=publique -->
# ADR-0072 — Le hook de l'agent développe un chemin écrit comme le shell, et refuse ce qu'il ne sait pas développer dans le projet

> statut : acceptée · date : 2026-11-13 · source : B-0171@60f59a60, D-0106@ac61dcae, ADR-0065@88e1a34b, D-0098@8911447c, J-2026-11-13-H@3cf9faad, B-0204@c680b8d2, B-0205@c8894b89, B-0206@34e2a00d, B-0207@fc0fc971, B-0208@59067330 · lu : decisions@8b5a2d9c

## Contexte

Le hook de l'agent jugeait les chemins qu'une commande du shell écrit tels
qu'ils sont tapés : `echo x > $F`, `rm .socle/pol*` ou `pushd .socle &&
echo x > policy.toml` passaient, alors que le shell aurait écrit un fichier
protégé ; seul `protege.fichiers` l'attrapait ensuite, à la fin du tour et
au commit (B-0171, priorité haute validée par D-0106). La remise en état
d'un fichier protégé refusait déjà un chemin qui n'est pas écrit en toutes
lettres (ADR-0065).

La revue sans contexte du premier jet y a trouvé onze contournements, dont
deux régressions, et deux faux refus (J-2026-11-13-H) : l'état d'un
sous-shell passait à la suite, la cible inconnue d'un `cd` se rattachait
au dossier courant, un `..` après une part inconnue n'était pas vu, `$_`
venait de l'environnement du hook, un chemin relatif partait de la racine
plutôt que du dossier courant de l'agent. Cette décision dit la règle
corrigée.

## Décision

Un chemin que le hook range parmi les écritures (redirection, `rm`, `mv`,
`cp`, `sed -i`…) se juge au plus près de ce que ferait le shell
(`ecritures_jugees`) :

1. Le découpage suit l'état du shell (`commandes.analyser`) : les
   variables affectées (`F=x;`, `F+=y`, `export`, `declare`, `local`,
   `readonly` ; `unset` les vide, pas `unset -f`), le dossier (`cd` et ses
   options, `cd -`, `pushd`, `popd`), chaque cible de `cd` développée avec
   les variables du moment du `cd`, qui pose `PWD` et `OLDPWD`. Un
   sous-shell `( … )`, une substitution (`$(…)`, accents graves, `<(…)`),
   chaque élément d'un pipeline et une tâche de fond (`&`) ne transmettent
   rien à la suite ; ce que lance une substitution nue se juge. Une
   affectation devant une commande (`F=x cmd`) ne vaut que pour elle.
2. Ce qui se développe se développe, dans l'ordre du shell : les accolades
   (`{a,b}`, `{1..3}`), le `~` (`~+`, `~-`, `~nom`), les variables de
   l'environnement du hook et celles de la commande, `${X:-y}` et ses
   voisins (`-`, `+`, `=`, `?`), `$'…'` et `$"…"`. Les variables que le
   shell tient lui-même (`_`, `OLDPWD`, `IFS`, `RANDOM`…) ne se prennent
   jamais dans l'environnement du hook ; `PWD` est le dossier courant de
   l'agent (`cwd` de son entrée), ou la racine s'il n'est pas connu, d'où
   partent aussi les chemins relatifs et les motifs (B-0205). Une valeur
   de variable se juge entière et mot par mot (le découpage ne sait plus
   si des guillemets l'entouraient).
3. Un motif (`*`, `?`, `[…]`, une classe POSIX `[[:alpha:]]`) se développe
   contre les fichiers présents, sans rendre le `.` qui ouvre un nom ; il
   se compare aussi aux motifs des chemins protégés (`commandes.se_croisent`)
   : un fichier protégé absent le reste, et `rm -rf .so*` vise ce qui est
   sous `.socle`. Après un `shopt` ou une affectation de `GLOBIGNORE` dans
   la commande, il se juge comme si `dotglob`, `globstar` et `nocaseglob`
   étaient actifs ; un motif étendu (`@(…)`) est inconnu.
4. Ce qui ne se développe pas (une variable inconnue du hook, une
   référence `declare -n`, un tableau, `$(…)`, des accents graves, un motif
   étendu, `$((…))`, `read`, `for`, une rotation de la pile, des accolades
   au-delà de 256 formes, un `cd` vers un tel chemin) est refusé s'il peut
   tomber dans le projet : le dossier que nomme la part écrite en toutes
   lettres avant lui, remonté d'autant de `..` qu'il en suit (`..` écrit, ou
   un nom de points que l'inconnu compléterait, `..$X`), est dans le projet
   ou le contient (`> .socle/$X`, `> $HOME/$X` si le projet est sous
   `$HOME`, `> /tmp/$X/../..`), ou rien ne le précède (`> $X`, `cd $D &&
   echo > x`). Il passe quand ce dossier est hors du projet (`> /tmp/$X`,
   `> "${TMPDIR:-/tmp}/x"` si `TMPDIR` est connu et hors du projet). Le
   refus dit la part qui ne se développe pas et comment écrire le chemin.
5. Le script d'un `sed -i` ou d'un `perl -i` (`-e`, `-f`, `--expression`,
   séparé ou collé, `-e"s/a/b/"`, `-pe'…'`) n'est pas un chemin écrit : une
   variable qu'il cite ne fait rien refuser ; sans `-i`, rien n'est écrit.

Les réglages de Claude Code se jugent de même (`F=.claude/settings.local.json;
echo > $F` est refusé). La remise de D-0098 ne change pas, ses chemins
relatifs partant aussi du dossier courant de l'agent.

## Conséquences

Les faux refus, mesurés avant et après sur les commandes écrites dans le
dépôt (blocs de code des skills, des gabarits, des docs et de la mémoire,
commandes citées en ligne dans la mémoire, étapes des workflows, une
centaine) et sur plus de 250 commandes lancées par les agents de la
session du 13 novembre : deux, dans les gabarits du workflow de mutation
(`>> "$GITHUB_STEP_SUMMARY"`, une variable que seule la CI connaît), que
l'agent ne lance pas. Les autres refus nouveaux sont les contournements
que B-0171 et le journal citent en exemple. La correction de la revue,
mesurée de même entre le premier jet et elle, sur les 21 blocs des skills,
308 commandes lancées par les agents de la session (chacune dans son
dossier courant) et 91 commandes courantes d'un agent : aucun verdict ne
change, et aucun skill n'est refusé par `skills.commandes`.

Restent des faux refus, qui se contournent en écrivant le chemin en
toutes lettres : un dossier tenu dans une variable que le hook ne connaît
pas (`T=$(mktemp -d); echo > $T/x`, `ROOT=$(git rev-parse
--show-toplevel); echo > $ROOT/x`, `cd "$(git rev-parse
--show-toplevel)" && echo > x`), une variable du profil du shell que
l'environnement du hook n'a pas (`$TMPDIR` dans une session qui ne l'a
pas), une boucle `for` sur une liste écrite (`for i in 1 2; do echo >
out$i.txt; done` : `$i` reste inconnu), un nom calculé (`out$((i+1)).txt`),
un `${X-y}` sans `:` dont `X` est vide (le hook ne distingue pas une
variable vide d'une variable non posée). S'ils gênent, la piste est de
reconnaître `$(mktemp …)` et `$(git rev-parse --show-toplevel)`, et de
juger chaque valeur d'une liste `for`.

Restent des risques acceptés, que seul un analyseur complet du shell
fermerait, et que `protege.fichiers` attrape à la fin du tour et au
commit : une part inconnue qui contient elle-même `..` ou une barre
(`/tmp/$X` avec `X=../..`, le hook ne pouvant savoir combien de dossiers
elle remonte) ; une option du shell posée par le profil plutôt que par la
commande (`dotglob`, `nocaseglob`) ; les mots réservés (`if`, `then`, `{`,
B-0204), ce que lance une substitution entre guillemets, l'état que
laissent `eval`, `source`, une fonction ou `CDPATH`, et un `#` que le
découpage lit à tort comme un commentaire (B-0207) ; les écritures que le
hook ne range pas parmi les écritures (`cp -t`, `xargs`, `find -delete`,
`bash -ec`, `sort -o`, B-0206) et la suppression d'un dossier qui contient
le projet (`rm -rf ..`, B-0208). Le jugement de
`skills.commandes` dépend de l'environnement où il tourne, comme celui du
hook. Le hook reste un étage : `protege.fichiers` juge ce qui est commité.
Pour défaire : rendre à `refus_bash` l'ancien jugement littéral
(`ecriture_protegee` sur `ecrits`) ; les tests de `tests/test_garde.py` et
les défauts `protege-developpe`, `ecriture-illisible`,
`protege-etat-du-shell`, `protege-forme-du-shell`,
`ecriture-illisible-remontee` et `protege-dossier-courant` de l'auto-test
diront ce qui change.
