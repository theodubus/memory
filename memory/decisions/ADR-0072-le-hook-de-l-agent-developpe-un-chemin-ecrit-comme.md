<!-- socle: couche=decisions zone=publique -->
# ADR-0072 — Le hook de l'agent développe un chemin écrit comme le shell, et refuse ce qu'il ne sait pas développer dans le projet

> statut : acceptée · date : 2026-11-13 · source : B-0171@60f59a60, D-0106@ac61dcae, ADR-0065@88e1a34b, D-0098@8911447c, J-2026-11-13-H@3cf9faad, B-0204@c680b8d2, B-0205@c8894b89, B-0206@34e2a00d, B-0207@fc0fc971, B-0208@59067330, J-2026-11-13-J@940ad1d7, B-0211@4aed31c0 · lu : decisions@8b5a2d9c

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
plutôt que du dossier courant de l'agent. Une seconde revue en a trouvé
dix-neuf autres, dont le hook qui laissait passer quand il plantait ou
dépassait son délai ; la poursuite des formes exotiques s'arrête là
(J-2026-11-13-J) : chaque tour de correction en ouvrait d'autres. Cette
décision dit la règle telle que le code la tient.

## Décision

Le hook est une première barrière, au mieux, contre les erreurs d'un agent
coopératif ; il ne modélise pas tout bash. La garantie est
`protege.fichiers`, qui juge ce qui change à la fin du tour, au commit et
dans la CI, quelle que soit la commande qui l'a écrit. Un chemin que le
hook range parmi les écritures (redirection, `rm`, `mv`, `cp`, `sed -i`…)
se juge au plus près de ce que ferait le shell (`ecritures_jugees`) :

1. Le découpage suit l'état du shell (`commandes.analyser`) : les
   variables affectées (`F=x;`, `F+=y`, `export`, `declare`, `local`,
   `readonly` ; `unset` les vide, pas `unset -f`), le dossier (`cd` et ses
   options, `cd -`, `pushd`, `popd`), chaque cible de `cd` développée avec
   les variables du moment du `cd`, qui pose `PWD` et `OLDPWD`. Le hook
   suppose qu'un sous-shell `( … )`, une substitution (`$(…)`, accents
   graves, `<(…)`), chaque élément d'un pipeline et une tâche de fond (`&`)
   ne transmettent rien à la suite, et juge ce que lance une substitution
   nue qu'il a su délimiter. Une affectation devant une commande (`F=x
   cmd`) ne vaut que pour elle.
2. Ce qui se développe se développe, dans l'ordre du shell : les accolades
   (`{a,b}`, `{1..3}`), le `~` (`~+`, `~-`, `~nom`), les variables de
   l'environnement du hook et celles de la commande, `${X:-y}` et ses
   voisins (`-`, `+`, `=`, `?`), `$'…'` et `$"…"`. L'environnement du hook
   n'est pas celui du shell de l'agent : Claude Code pose pour ses hooks
   des variables (`CLAUDE_PROJECT_DIR`) que le shell de l'agent n'a pas, et
   le profil du shell de l'agent des variables que le hook n'a pas. Les
   variables que le shell tient lui-même (`_`, `OLDPWD`, `IFS`, `RANDOM`…)
   ne se prennent jamais dans l'environnement du hook ; `PWD` est le
   dossier courant de l'agent (`cwd` de son entrée), ou la racine s'il
   n'est pas connu, d'où partent aussi les chemins relatifs et les motifs
   (B-0205). Une valeur de variable se juge entière et mot par mot (le
   découpage ne sait plus si des guillemets l'entouraient) ; une valeur
   développée de plus de 10 000 caractères, que seule une variable
   dupliquée rend (`F=$F$F`), est inconnue.
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
   `perl -0` et `perl -l` ne prennent que les chiffres qui les suivent
   (`-0777`, `-0x1FF`, `-l015`) : `-lpi`, `-0pi` et `-pli` réécrivent leurs
   fichiers.
6. Ce que le hook ne sait pas juger ne passe pas, s'il peut écrire : un
   hook qui plante ou dépasse son délai laisse passer la commande. Il
   refuse, avant de la découper, une commande de plus de 10 000 caractères
   hors du corps de ses heredocs ou de plus de 32 parenthèses ou accolades
   ouvertes à la fois (`commandes.demesure`) ; puis celle dont le
   découpage ou le jugement des écritures lève (`RecursionError`, `eval`
   répété) ou prend plus de 5 secondes (`DELAI_JUGEMENT` : deux jugements,
   dans deux worktrees, tiennent sous les 20 s du hook). « Peut écrire »
   se lit sur le texte seul : une redirection, ou le nom d'un écrivain
   (`peut_ecrire`). Chaque `cd` ne développe plus que les variables
   affectées depuis le précédent : 500 `cd` se jugent en moins d'une
   seconde, et non en plus de vingt.

Les réglages de Claude Code se jugent de même (`F=.claude/settings.local.json;
echo > $F` est refusé). La remise de D-0098 ne change pas, ses chemins
relatifs partant aussi du dossier courant de l'agent.

## Conséquences

Les faux refus, mesurés avant et après chaque tour sur les blocs des
skills, les commandes écrites dans le dépôt, celles que les agents de la
session ont lancées (735 au dernier tour, chacune dans son dossier
courant) et 91 commandes courantes d'un agent : deux au premier jet, dans
les gabarits du workflow de mutation (`>> "$GITHUB_STEP_SUMMARY"`, que
l'agent ne lance pas), puis aucun verdict changé par les deux
corrections ; aucun skill refusé par `skills.commandes`, et la plus longue
commande fait 1 861 caractères hors heredoc, loin du seuil
(J-2026-11-13-H). Une commande qui peut écrire et passe un seuil (un long
`python3 -c`) est refusée : la découper, ou passer son script dans un
fichier ou un heredoc.

Restent des faux refus, qui se contournent en écrivant le chemin en
toutes lettres : un dossier tenu dans une variable que le hook ne connaît
pas (`T=$(mktemp -d); echo > $T/x`, `cd "$(git rev-parse
--show-toplevel)"`), une variable du profil du shell que l'environnement
du hook n'a pas (`$TMPDIR`), une boucle `for` sur une liste écrite, un
nom calculé (`out$((i+1)).txt`), un `${X-y}` sans `:` dont `X` est vide.
La piste, s'ils gênent : reconnaître `$(mktemp …)` et `$(git rev-parse
--show-toplevel)`, juger chaque valeur d'une liste `for`.

Restent des risques acceptés, au backlog sans priorité, que
`protege.fichiers` attrape à la fin du tour, au commit et dans la CI :

- une part inconnue qui vaut elle-même `..` (`/tmp/$X` avec `X=../..`) ;
  une option du shell posée par le profil (`dotglob`, `nocaseglob`) ;
- venus avec B-0171 (B-0211) : un opérateur entre guillemets ou échappé
  lu comme un vrai ; ce que lance une substitution dans `$((…))`, un
  tableau ou un motif étendu ; une substitution que `_fermante` ferme mal
  (un commentaire, `$'\''`, `case`) ; `lastpipe` ; `((…))`, `let`,
  `getopts` ; la différence d'environnement du point 2
  (`$CLAUDE_PROJECT_DIR`) ; la forme écrite d'un chemin entre
  apostrophes ; `unset IFS` ; `bash -O` ;
- d'avant B-0171 : les mots réservés (B-0204) ; une substitution entre
  guillemets, `eval`, `source`, une fonction, `CDPATH`, un `#` dans un
  mot, un `cd` qui échoue, `env -C`, un heredoc vu à tort, `"<"`,
  `"$(…"…")"`, les options abrégées de sed (B-0207) ; `cp -t`, `xargs`,
  `find -delete`, `bash -ec`, `sort -o` (B-0206) ; `rm -rf ..` (B-0208) ;
- une commande qui ne peut rien écrire, à en juger par son texte, et dont
  le jugement plante ou passe le délai : le hook plante, sans juger ses
  autres refus.

Le jugement de `skills.commandes` dépend de l'environnement où il tourne,
comme celui du hook. Pour défaire : rendre à `refus_bash` l'ancien
jugement littéral (`ecriture_protegee` sur `ecrits`) ; les tests de
`tests/test_garde.py` et les défauts `protege-developpe`,
`ecriture-illisible`, `protege-etat-du-shell`, `protege-forme-du-shell`,
`ecriture-illisible-remontee`, `protege-dossier-courant` et
`commande-injugeable` de l'auto-test diront ce qui change.
