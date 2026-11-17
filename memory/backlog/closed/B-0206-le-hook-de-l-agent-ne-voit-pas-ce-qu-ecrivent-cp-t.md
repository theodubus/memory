<!-- socle: couche=backlog zone=publique -->
# B-0206 — Le hook de l'agent ne voit pas ce qu'écrivent cp -t, xargs, find -delete, bash -ec, sort -o ou python -c

> statut : fait · origine : J-2026-11-13-H · ref : J-2026-11-14-AG · lu : backlog@f4a491f0

Le hook de l'agent ne range pas parmi les écritures ce que ces commandes
écrivent ; une écriture d'un fichier protégé y passe le hook, et seul
`protege.fichiers` l'attrape ensuite, à la fin du tour et au commit :

- `cp -t .socle/git-hooks x` et `install -t .socle/git-hooks x` :
  `ecrits_bruts` prend la destination dans le dernier argument, jamais
  dans `-t` ;
- `echo .socle/policy.toml | xargs rm` : les arguments que `xargs` lit sur
  son entrée ne se voient pas ;
- `find .socle -name policy.toml -delete`, et `-exec rm {} +` ;
- `bash -ec 'rm .socle/policy.toml'`, `bash -lc '…'`, `bash -c -- '…'` :
  `commandes.analyser` n'ouvre un `bash` que si `-c` y est écrit seul ;
- `sort -o .socle/policy.toml x`, et `python3 -c` qui ouvre le fichier en
  écriture : une écriture par une option, ou par un autre langage.

Vu par la revue sans contexte de B-0171 (son constat 15) : chacun passait
avant B-0171 et passe toujours après la correction de sa revue. Sans
priorité, par la décision de Théo (D-0108@96eeead5) ; la suppression d'un dossier
qui contient le projet, du même constat, va à B-0208, en haute. Pour
rejouer chaque cas, depuis la racine du dépôt (`None` : le hook le laisse
passer) :

```sh
python3 -c "import sys; sys.path.insert(0,'engine'); from pathlib import Path; from socle import config, hooks; p=config.Projet.charger(Path('.')); [print(repr(hooks.refus_bash(p,c))[:60],'|',c) for c in sys.argv[1:]]" 'cp -t .socle/git-hooks /tmp/x' 'install -t .socle/git-hooks /tmp/x' 'echo .socle/policy.toml | xargs rm' 'find .socle -name policy.toml -delete' 'find .socle -name policy.toml -exec rm {} +' "bash -ec 'rm .socle/policy.toml'" "bash -lc 'rm .socle/policy.toml'" "bash -c -- 'rm .socle/policy.toml'" 'sort -o .socle/policy.toml /tmp/x' "python3 -c \"open('.socle/policy.toml','w').write('x')\""
```

La piste : lire la destination de `-t` (`--target-directory`), ouvrir
`bash` quel que soit le groupe qui porte `c` (`-ec`, `-lc`) et sauter `--`,
ranger `find -delete`, `find -exec <écrivain>`, `xargs <écrivain>` et
`sort -o` parmi les écritures (`xargs` : ce qu'il écrit ne se lit pas, donc
refusé dans le projet, comme un chemin inconnu), et juger `python -c` par
les chemins protégés qu'il cite.

Le 14 novembre, Théo veut ce sujet traité s'il ne génère pas lui aussi
des cas sans fin (D-0111, J-2026-11-14-L). La liste est finie ; seul
`python -c` ouvre un langage entier. Il se borne par son modèle de
menace : un écrivain que le hook ne sait pas lire (`python -c`, `xargs`)
est jugé par les chemins protégés qu'il cite en toutes lettres ; un chemin
construit au vol dans un autre langage est hors du modèle, un risque
accepté que `protege.fichiers` attrape ensuite, et n'ouvre pas de sujet.

## Modèle de menace

La règle 2 de D-0112 : le hook juge les formes du shell qu'un agent
coopératif écrit dans son travail. `cp -t`, `install -t`, `find -delete`,
`find -exec rm {} +`, `xargs rm`, `bash -ec`, `sort -o` et `python3 -c` en
sont ; la liste de ce sujet est finie (D-0111).

Ce que le changement arrête :

- `cp`, `ln` et `install` écrivent le dossier de `-t` (`-tDIR`, `-rt DIR`,
  `--target-directory`), et non leur dernier argument ; `sort` écrit le
  fichier de `-o` (`--output`) ;
- `bash`, `sh`, `zsh` et `dash` ouvrent leur commande quel que soit le
  groupe d'options qui porte `c` (`-ec`, `-lc`, `-o pipefail -c`), `--`
  sauté ;
- `find -delete`, et `find -exec` (`-execdir`, `-ok`, `-okdir`) d'un
  écrivain de `{}` (`rm`, `sed -i`…), suppriment ce que nomment leurs
  points de départ et leurs filtres (`-name`, `-path`), jugés contre les
  motifs des chemins protégés à toute profondeur : `find .socle -name
  policy.toml -delete` et `find . -name '*.toml' -delete` sont refusés,
  `find . -name '*.pyc' -delete` passe ; un `!`, `-not` ou `-regex` rend
  le filtre inconnu, et la suppression de tout ce qui est sous le départ ;
- deux écrivains que le hook ne sait pas lire se jugent par les chemins
  protégés qu'ils citent en toutes lettres : `xargs` d'un écrivain de ce
  qu'il lit, par ceux de la commande entière (`echo .socle/policy.toml |
  xargs rm`), et `python -c`, par ceux de son script, qu'il les lise ou
  les écrive. Un chemin cité vaut s'il est protégé, ou s'il est un dossier
  qui en contient, écrit avec une barre oblique ou un point de tête
  (`.socle`, `memory/requests`) ; ni la racine, ni un dossier qui la
  contient, ni un mot sans barre ni point (`memory`, un nom de module)
  n'en sont.

Ce qu'il laisse passer : un chemin construit au vol dans un autre langage
(`Path('.socle') / 'policy' + '.toml'` ne cite pas le fichier), hors du
modèle par la règle 2 ; ce que lit `xargs` sur un fichier (`-a`) ou par
une redirection ; ce que `find` écrit par `-fprint` ou `-exec sh -c` ; un
script python lu sur son entrée (`python3 - <<EOF`), qui n'est pas dans
cette liste et va au backlog. `protege.fichiers` attrape ensuite
l'écriture d'un fichier protégé.

Ce qu'il refuse de plus : un `python -c` qui lit un fichier protégé qu'il
cite (`open('.socle/policy.toml')`), que le hook ne distingue pas d'une
écriture : un fichier protégé se lit par `cat` ou par l'outil de lecture.

## Satisfait quand

- [x] chacune de ces écritures d'un fichier protégé est refusée par le hook, et un test le montre
