<!-- socle: couche=backlog zone=publique -->
# B-0232 — Le hook de l'agent ne lit pas le corps de function f { … } sans parenthèses : un push forcé ou une suppression du projet y passent

> statut : fait · origine : J-2026-11-14-AL · priorité : haute · ref : J-2026-11-15-M · lu : backlog@1a5a32a1

Le découpage des commandes (`commands._definition`) ne reconnaît une
définition de fonction qu'à ses parenthèses, `nom ( )` ou `function nom (
)`. Écrite `function f { …; }`, sans parenthèses, la commande lue a pour
programme `function`, et rien de son corps ne se juge : `function f { git
push --force origin main; }; f` et `function f { rm -rf ..; }; f` passent
le hook de l'agent, sur la branche par défaut comme après le lot 3. Vu par
la seconde revue du lot 3 ; la première l'avait écarté comme exotique,
mais ADR-0080 (sa première conséquence) ouvre un sujet pour un trou par
lequel passe un push forcé ou la suppression du projet, quelle qu'en soit
la forme : rien ne rattrape leur effet. De priorité haute, comme B-0208.

La piste : lire `function nom {` comme `nom ( ) {`, l'ouverture du corps
d'une fonction, qui se juge et rend en se fermant l'état d'avant lui.

## Modèle de menace

Borné à la règle 2 de D-0112, qu'écrit ADR-0080@bfb13155 : un push forcé,
une action externe irréversible, et la suppression du projet ou d'un
dossier qui le contient sont de ce que rien ne rattrape ensuite, et se
jugent quelle qu'en soit la forme. Le sujet couvre la définition d'une
fonction par le mot réservé `function`, sans parenthèses, telle que bash
la lit (vérifié par `bash -n -c`) :

- `function nom` en tête d'une commande, seul ou derrière des mots
  réservés (`then`, `do`, `!`, `{`, `if`), le nom quel qu'il soit : bash
  admet `function f/x { …; }` ou `function if { …; }`, et les appelle ;
  `function` en argument (`echo function f {`) n'en est pas une ;
- son corps, qui commence au mot qui suit, sur la même ligne ou après des
  sauts de ligne et des commentaires : un groupe `{ …; }` se lit comme
  celui de `nom ( ) { …; }`, chaque commande jugée, l'état d'avant lui
  rendu à sa fermeture (la revue du lot 3, J-2026-11-14-AH) ;
- un autre corps, que la grammaire de bash admet (tout `shell_command` :
  `( … )`, `if`, `while`, `until`, `for`, `select`, `case`, `[[ … ]]`,
  `(( … ))`), se lit comme celui de `nom ( )` : chaque commande jugée
  comme si elle s'exécutait là où elle s'écrit, ce qui refuse plus, jamais
  moins ; ce qu'une condition ou une boucle change devient inconnu après
  elle, et une écriture qui la suit dans le projet est refusée comme
  illisible (ADR-0072, point 6), un sous-shell rend l'état d'avant lui ;
- la définition lue ne vaut que pour la commande qui la suit, par-delà
  des sauts de ligne seulement : un corps sous-shell la consomme, et un
  groupe écrit dans ce sous-shell (`f ( ) ( { cd memory; }; rm -rf
  ../../projet )`) ne se lit plus comme le corps d'une fonction, qui
  rendait à tort l'état d'avant lui ; sans quoi la lecture d'un corps sur
  la ligne suivante ouvrirait ce trou à `function nom`.

Hors du sujet, au backlog : `time` devant une commande composée (`time {
…; }`, `time if …`, `time function f { …; }`), qui la fait lire comme une
commande simple dont le programme est le mot réservé, et les motifs d'un
`case`, que le hook ne suit pas : un `cd` sous un motif qui ne s'applique
pas vaut pour la suite. Le premier laisse passer un push forcé, le second
la suppression du projet, qu'une fonction soit là ou non.

## Fait quand

- [x] `function f { git push --force origin main; }; f` et `function f { rm -rf ..; }; f` sont refusés par le hook, `function f { ls; }; f` passe, et un test le montre
