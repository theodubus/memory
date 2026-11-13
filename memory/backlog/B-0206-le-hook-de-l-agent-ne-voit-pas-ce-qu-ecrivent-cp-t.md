<!-- socle: couche=backlog zone=publique -->
# B-0206 — Le hook de l'agent ne voit pas ce qu'écrivent cp -t, xargs, find -delete, bash -ec, sort -o ou python -c

> statut : ouvert · origine : J-2026-11-13-H · lu : backlog@f4a491f0

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

## Fait quand

- [ ] chacune de ces écritures d'un fichier protégé est refusée par le hook, et un test le montre
