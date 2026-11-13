<!-- socle: couche=backlog zone=publique -->
# B-0211 — Le hook de l'agent laisse passer les formes du shell que la seconde revue de B-0171 a trouvées, risques acceptés

> statut : ouvert · origine : J-2026-11-13-H · lu : backlog@c37b771c

La seconde revue sans contexte de B-0171 a trouvé des formes du shell par
lesquelles une écriture d'un fichier protégé passe le hook de l'agent.
Elles ne se corrigent pas dans B-0171 : le hook est une première barrière
contre les erreurs d'un agent coopératif, et la garantie est
`protege.fichiers`, à la fin du tour, au commit et dans la CI, qui les
attrape toutes (J-2026-11-13-J, D-0108@96eeead5, ADR-0072). Chaque tour de
correction en ouvrait d'autres ; elles restent des risques acceptés, à
reprendre si l'une sert à un agent réel. Chacune passe le hook :

- un opérateur entre guillemets ou échappé (`"("`, `\(`, `$'('`, `"&"`)
  est lu comme un vrai opérateur : `_jetons` juge un jeton dont `shlex` a
  retiré les guillemets, et le découpage rend l'état d'avant un sous-shell
  ou une tâche de fond qui n'existent pas ;
- ce que lance une substitution dans `$((…))`, dans les valeurs d'un
  tableau (`T=($(…))`) ou dans un motif étendu (`@($(…))`) ne se juge pas,
  ni `$((rm …) )`, que bash lit comme une substitution qui contient un
  sous-shell ;
- `_fermante` ignore dans `$(…)` les commentaires, les échappements de
  `$'…'` et les motifs de `case` : la substitution se ferme trop tôt ou
  trop tard ;
- `shopt -s lastpipe` n'est pas suivi : le dernier élément d'un pipeline
  tourne alors dans le shell courant (`echo | cd .socle`, `| read F`) ;
- des affectations ne se suivent pas : `((F=0))`, lu comme deux
  sous-shells, `let F=0` et `getopts l F` ;
- l'environnement du hook n'est pas celui du shell de l'agent : Claude
  Code ne pose `CLAUDE_PROJECT_DIR` que pour ses hooks, et le hook développe
  avec lui ce que le shell de l'agent laisse vide ;
- seule la forme développée d'un chemin se juge, jamais sa forme écrite :
  `'.socle/git-hooks/$X'`, entre apostrophes, crée le fichier
  `.socle/git-hooks/$X`, que le hook juge comme `$X` développé ;
- la coupure en mots est incomplète : `unset IFS` se lit comme `IFS=""`,
  et la coupure s'applique aussi aux parts écrites en toutes lettres
  (`IFS=o; F=ox; rm -f .socle/policy.toml$F`) ;
- `bash -O dotglob` et `bash -O nocaseglob` n'élargissent pas les motifs
  jugés, comme `shopt` le fait.

Aucun test ni défaut injecté n'exerce ces formes ; et `tous_refuses`, dans
l'auto-test, juge la concaténation des raisons de tous ses appels : un cas
d'un défaut retombé dans un autre refus que le sien ne le ferait pas
échouer.

Pour rejouer chaque cas, depuis la racine du dépôt (`None` : le hook le
laisse passer) ; le second appel pose `CLAUDE_PROJECT_DIR` comme Claude
Code le pose pour ses hooks :

```sh
python3 -c "import sys; sys.path.insert(0,'engine'); from pathlib import Path; from socle import config, hooks; p=config.Projet.charger(Path('.')); [print(repr(hooks.refus_bash(p,c))[:60],'|',c) for c in sys.argv[1:]]" 'echo "(" ; cd .socle; echo ")" ; echo x > policy.toml' 'echo \( ; cd .socle; echo \) ; echo x > policy.toml' $'echo $\'(\' ; cd .socle; echo $\')\' ; echo x > policy.toml' 'F=/tmp/x; echo "("; F=.socle/policy.toml; echo ")"; echo x > $F' 'cd .socle && echo "&" ; echo x > policy.toml' 'echo $(( $(rm -f .socle/policy.toml; echo 0) + 1 ))' 'T=($(rm -f .socle/policy.toml))' $'shopt -s extglob\nls @($(rm -f .socle/policy.toml))' 'echo $((rm -f .socle/policy.toml) )' $'X=$(echo a # )\ncd /tmp\n); echo x > .socle/policy.toml' $'X=$(echo $\'\\\'\'; cd /tmp; echo $\'\\\'\'); echo x > .socle/policy.toml' 'X=$(case a in a) cd /tmp;; esac); echo x > .socle/policy.toml' '( case a in a) cd /tmp;; esac ); echo x > .socle/policy.toml' 'shopt -s lastpipe; echo | cd .socle; echo x > policy.toml' 'F=/tmp/x; shopt -s lastpipe; echo .socle/policy.toml | read F; echo x > $F' 'F=/../../../tmp/x; ((F=0)); echo x > .socle/git-hooks/$F' 'F=/../../../tmp/x; let F=0; echo x > .socle/git-hooks/$F' 'F=/../../tmp/x; getopts l F -l; echo x > .socle/policy.tom$F' $'X=/../../../tmp/y; echo x > \'.socle/git-hooks/$X\'' 'unset IFS; F=".socle/policy.toml calc.py"; echo x | tee $F' 'IFS=o; F=ox; rm -f .socle/policy.toml$F' "bash -O dotglob -c 'echo x > */policy.toml'" "bash -O nocaseglob -c 'echo x > .socle/POLICY.tom?'"
CLAUDE_PROJECT_DIR="$PWD" python3 -c "import sys; sys.path.insert(0,'engine'); from pathlib import Path; from socle import config, hooks; p=config.Projet.charger(Path('.')); [print(repr(hooks.refus_bash(p,c))[:60],'|',c) for c in sys.argv[1:]]" 'echo x > $CLAUDE_PROJECT_DIR.socle/policy.toml' 'F=${CLAUDE_PROJECT_DIR:+/tmp/x}; echo x > ${F:-.socle/policy.toml}' 'cd "${CLAUDE_PROJECT_DIR:+/tmp}" && echo x > .socle/policy.toml'
```

La piste, si l'une gêne : garder dans `_jetons` l'information qu'un jeton
était entre guillemets, et n'y lire un opérateur que nu ; mettre de côté
une substitution dans `$((…))`, un tableau ou un motif étendu avec sa
commande interne ; faire lire à `_fermante` les commentaires, `$'…'` et
`case` ; suivre `lastpipe`, `((…))`, `let` et `getopts` ; retirer de
l'environnement du hook les variables que Claude Code ne pose que pour
lui ; juger aussi la forme écrite d'un chemin entre apostrophes ; lire
`unset IFS` comme la coupure par défaut ; élargir les motifs après
`bash -O` ; faire juger par `_attrape_par` la raison de chaque appel d'un
défaut.

## Fait quand

- [ ] chacune de ces écritures d'un fichier protégé est refusée par le hook, et un test le montre
- [ ] un défaut injecté de l'auto-test n'est attrapé que si chacun de ses appels l'est par sa raison
