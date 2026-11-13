<!-- socle: couche=decisions zone=publique -->
# ADR-0072 — Le hook de l'agent développe un chemin écrit comme le shell, et refuse ce qu'il ne sait pas développer dans le projet

> statut : acceptée · date : 2026-11-13 · source : B-0171@60f59a60, D-0106@ac61dcae, ADR-0065@88e1a34b, D-0098@8911447c · lu : decisions@8b5a2d9c

## Contexte

Le hook de l'agent jugeait les chemins qu'une commande du shell écrit tels
qu'ils sont tapés : `echo x > $F`, `rm .socle/pol*` ou `pushd .socle &&
echo x > policy.toml` passaient, alors que le shell aurait écrit un fichier
protégé ; seul `protege.fichiers` l'attrapait ensuite, à la fin du tour et
au commit (B-0171, priorité haute validée par D-0106). La remise en état
d'un fichier protégé refusait déjà un chemin qui n'est pas écrit en toutes
lettres (ADR-0065).

## Décision

Un chemin que le hook range parmi les écritures (redirection, `rm`, `mv`,
`cp`, `sed -i`…) se juge au plus près de ce que ferait le shell
(`ecritures_jugees`) :

1. Ce qui se développe se développe, dans l'ordre du shell : les accolades
   (`{a,b}`, `{1..3}`), le `~`, les variables de l'environnement du hook et
   celles que la même commande affecte plus tôt (`F=x;`, `export`,
   `declare`, `local`, `readonly` ; `unset` les vide), `$PWD` étant le
   dossier où la commande s'exécute. Une affectation devant une commande
   (`F=x cmd`) ne vaut que pour elle, comme dans le shell.
2. Un motif (`*`, `?`, `[…]`) se développe contre les fichiers présents,
   depuis ce dossier, sans rendre le `.` qui ouvre un nom ; il se compare
   aussi aux motifs des chemins protégés (`commands.se_croisent`) : un
   fichier protégé absent le reste, et `rm -rf .so*` vise ce qui est sous
   `.socle`.
3. Ce qui ne se développe pas (une variable inconnue du hook, `${…}` avec
   un opérateur, `$(…)`, des accents graves, `read`, `for`) est refusé s'il
   peut tomber dans le projet : quand la part écrite en toutes lettres qui
   le précède le place dans le projet ou au-dessus (`> .socle/$X`,
   `> $HOME/$X` si le projet est sous `$HOME`), ou ne le place nulle part
   (`> $X`, `cd $D && echo > x`). Il passe quand elle le place hors du
   projet (`> /tmp/$X`, `> "$TMPDIR/x"` si `TMPDIR` est connu et hors du
   projet). Le refus dit la part qui ne se développe pas et comment écrire
   le chemin.
4. `pushd <dossier>` se suit comme un `cd`, `popd` ramène au précédent, et
   `cd -` aussi ; une rotation de la pile (`pushd +1`) rend le dossier
   inconnu.
5. Le script d'un `sed -i` ou d'un `perl -i` (`-e`, `-f`, `--expression`)
   n'est pas un chemin écrit : une variable qu'il cite ne fait rien refuser.

Les réglages de Claude Code se jugent de même (`F=.claude/settings.local.json;
echo > $F` est refusé). La remise de D-0098 ne change pas.

## Conséquences

Les faux refus, mesurés avant et après sur les commandes écrites dans le
dépôt (blocs de code des skills, des gabarits, des docs et de la mémoire,
commandes citées en ligne dans la mémoire, étapes des workflows, une
centaine) et sur plus de 250 commandes lancées par les agents de la
session du 13 novembre : deux, dans les gabarits du workflow de mutation
(`>> "$GITHUB_STEP_SUMMARY"`, une variable que seule la CI connaît), que
l'agent ne lance pas. Les autres refus nouveaux sont les contournements
que B-0171 et le journal citent en exemple. Aucun skill n'est refusé par
`skills.commandes`, aucune commande lancée par un agent non plus.

Restent possibles des faux refus que le dépôt ne montre pas : un dossier
temporaire tenu dans une variable (`T=$(mktemp -d); echo > $T/x`), une
variable du profil du shell que l'environnement du hook n'a pas. Ils se
contournent en écrivant le chemin en toutes lettres ; s'ils gênent, la
piste est de reconnaître `$(mktemp …)`, dont le dossier se lit dans ses
options. Le jugement de `skills.commandes` dépend de l'environnement où il
tourne, comme celui du hook. Le hook reste un étage : `protege.fichiers`
juge ce qui est commité. Pour défaire : rendre à `refus_bash` l'ancien
jugement littéral (`ecriture_protegee` sur `ecrits`) ; les tests de
`tests/test_garde.py` et les défauts `protege-developpe` et
`ecriture-illisible` de l'auto-test diront ce qui change.
