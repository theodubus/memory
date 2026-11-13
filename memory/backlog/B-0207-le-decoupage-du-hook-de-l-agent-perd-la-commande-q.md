<!-- socle: couche=backlog zone=publique -->
# B-0207 — Le découpage du hook de l'agent perd la commande qui suit un dièse, et ne suit ni ce que lance une substitution entre guillemets, ni l'état d'un eval, d'une fonction ou de CDPATH

> statut : ouvert · origine : J-2026-11-13-H · lu : backlog@f4a491f0

Trouvés en corrigeant la revue de B-0171, voisins de ce qu'elle citait ;
chacun passait avant B-0171 et passe toujours, et seul `protege.fichiers`
attrape ensuite l'écriture d'un fichier protégé :

- `shlex` lit un `#` comme un commentaire même au milieu d'un mot, et ce
  commentaire avale la fin de ligne : après `echo x # note`, la ligne
  suivante `rm .socle/policy.toml` devient des arguments d'`echo` ;
  `echo x#; rm .socle/policy.toml` et `[ $# -eq 0 ]; rm
  .socle/policy.toml` perdent de même la commande qui suit, que le shell
  lance (un `#` n'ouvre un commentaire qu'en tête d'un mot) ;
- ce que lance une substitution entre guillemets ne se juge pas :
  `echo "$(rm .socle/policy.toml)"` (une substitution nue, elle, se juge) ;
- l'état que laissent un `eval`, une fonction ou `CDPATH` ne se suit pas :
  `eval "cd .socle"; echo x > policy.toml`, `f() { cd .socle; }; f; echo x
  > policy.toml`, `CDPATH=.socle; cd git-hooks && echo x > pre-commit`.

Pour rejouer, depuis la racine du dépôt, la commande de B-0206 avec ces
cas pour arguments (un saut de ligne s'écrit `$'…\n…'`).

La piste : `commandes._preparer` lit déjà les guillemets et les
commentaires comme `shlex` ; y retirer lui-même un commentaire, en tête
d'un mot seulement et sans sa fin de ligne, puis ôter à `shlex` ses
commentaires ; mettre de côté une substitution entre guillemets comme une
substitution nue ; suivre l'état d'un `eval` dans le shell courant, et
rendre le dossier inconnu après l'appel d'une fonction définie dans la
commande, ou après un `cd` relatif quand `CDPATH` est posé.

## Fait quand

- [ ] chacune de ces écritures d'un fichier protégé est refusée par le hook, et un test le montre
