<!-- socle: couche=backlog zone=publique -->
# B-0230 — Le hook de l'agent ne juge xargs et python -c que par les chemins qu'ils citent : la liste qu'un find ou un grep -r donne à xargs, le chemin passé en argument au script

> statut : abandonné · origine : J-2026-11-14-AH · ref : D-0143 · lu : backlog@b4ef8718

B-0206 fait juger `xargs` d'un écrivain et `python -c` par les chemins
protégés qu'ils citent en toutes lettres. Deux usages normaux y
échappent, que la revue du lot 3 a trouvés (J-2026-11-14-AH) :

- `grep -rl foo . | xargs sed -i s/foo/bar/g`, `find . -type f | xargs
  sed -i …` : l'idiome du remplacement global réécrit les fichiers
  protégés, alors que son équivalent en `find -exec` est refusé ;
- `python3 -c "import sys; open(sys.argv[1], 'w')…" .socle/policy.toml` :
  le chemin passe en argument du script, que le hook ne cite pas ; sur
  le fichier de réglages local de Claude Code, que git ne suit pas, rien ne rattrape
  ensuite.

Dans le modèle de la règle 2 de D-0112 (ADR-0080) : des formes qu'un
agent écrit dans son travail. La piste : juger `producteur | xargs
écrivain` par les départs et les filtres d'un `find` producteur, `grep
-r` et `git ls-files` comme un `find` sans filtre ; citer aussi les
arguments qui suivent le script d'un `python -c`.

Abandonné le 20 novembre par D-0143 (ADR-0098) : le hook de l'agent est terminé, et cette entrée ne cite aucune preuve vue dans une session.

## Satisfait quand

- [ ] le remplacement global qu'écrit un agent, par `xargs` derrière un `grep -r` ou un `find`, ne réécrit plus un fichier protégé sans refus du hook, et un `find` dont les filtres l'écartent passe
- [x] un fichier protégé passé en argument au script d'un `python -c` arrête l'agent au hook comme s'il était écrit dans le script
