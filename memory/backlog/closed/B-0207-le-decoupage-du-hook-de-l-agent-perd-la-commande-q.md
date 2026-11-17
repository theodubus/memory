<!-- socle: couche=backlog zone=publique -->
# B-0207 — Le découpage du hook de l'agent perd la commande qui suit un dièse, et ne suit ni ce que lance une substitution entre guillemets, ni l'état d'un eval, d'une fonction ou de CDPATH

> statut : fait · origine : J-2026-11-13-H · ref : J-2026-11-14-AF · lu : backlog@f4a491f0

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

La seconde revue sans contexte de B-0171 y ajoute six cas du même
découpage, qui passaient eux aussi avant B-0171 :

- un `cd` qui échoue n'est pas vu : `cd /tmp/absent; echo x >
  .socle/policy.toml` écrit le fichier depuis le dossier de départ, que le
  hook croit quitté ;
- `env -C` et `env --chdir` ne se suivent pas ;
- `sans_heredocs` voit un heredoc où il n'y en a pas (`"<<EOF"` entre
  guillemets, `'<<EOF'` en argument, `$(( 1 << 2 ))`) et avale les lignes
  qui suivent jusqu'à un `EOF` ; et ce que lit `bash <<FIN` sur son entrée
  ne se juge pas ;
- un `"<"` entre guillemets saute le jeton qui le suit ;
- `"$(…"…")"` désaccorde les guillemets : la commande qui suit la
  substitution est perdue ;
- les options longues abrégées de sed (`--expr=`, `--in-pl`) ne se
  reconnaissent pas.

Pour les rejouer, depuis la racine du dépôt (`None` : le hook le laisse
passer) :

```sh
python3 -c "import sys; sys.path.insert(0,'engine'); from pathlib import Path; from socle import config, hooks; p=config.Projet.charger(Path('.')); [print(repr(hooks.refus_bash(p,c))[:60],'|',c) for c in sys.argv[1:]]" 'cd /tmp/absent; echo x > .socle/policy.toml' "env -C .socle sh -c 'echo x > policy.toml'" $'echo "<<EOF"\necho x > .socle/policy.toml\nEOF' $'grep -c \'<<EOF\' calc.py\necho x > .socle/policy.toml\nEOF' $'echo $(( 1 << 2 ))\necho x > .socle/policy.toml\nEOF' $'bash <<FIN\necho x > .socle/policy.toml\nFIN' 'echo "<"; rm -f .socle/policy.toml' 'X="$(echo "; cd /tmp; ")"; echo x > .socle/policy.toml' 'sed --expr=s/O/X/ -i .socle/policy.toml' 'sed --in-pl s/O/X/ .socle/policy.toml'
```

Leur piste : rendre le dossier inconnu après un `cd` dont la cible
n'existe pas, suivre `env -C`, ne lire un heredoc qu'hors des guillemets
et hors de `$((…))`, juger comme une commande le corps d'un heredoc que
lit un shell, n'ouvrir une redirection que sur un `<` nu, lire les
guillemets d'une substitution comme le shell (déjà la piste ci-dessus), et
reconnaître les préfixes uniques des options longues de sed.

Réduit le 14 novembre, sur la décision de Théo (D-0111, J-2026-11-14-L) :
ne restent que les formes qu'un agent coopératif écrit dans son travail,
le dièse (un commentaire en fin de ligne fait perdre la commande
suivante) et la substitution aux guillemets imbriqués (`"$(cmd "arg")"`,
une forme courante, désaccorde les guillemets et perd la commande qui
suit). Les autres (substitution entre guillemets qui écrit, `eval`,
fonction, `CDPATH`, `cd` qui échoue, `env -C`, heredoc vu à tort, `"<"`,
options abrégées de sed) restent des risques acceptés, que
`protege.fichiers` attrape ensuite.

## Modèle de menace

La règle 2 de D-0112 : le hook juge les formes du shell qu'un agent
coopératif écrit dans son travail. Un commentaire en fin de ligne, `$#`, un
`#` dans une adresse ou un format (`--format="%h # %s"`), et une
substitution entre guillemets dont l'argument a ses propres guillemets
(`"$(git log -1 --format="%s")"`, `"$(dirname "$F")"`) en sont.

Ce que le changement arrête : une écriture d'un fichier protégé, une action
irréversible ou une commande réservée à l'humain sur la ligne qui suit un
commentaire, après un `#` au milieu d'un mot (`x#`, `$#`), ou après une
substitution aux guillemets imbriqués : le découpage retire lui-même un
commentaire, seulement en tête d'un mot et sans sa fin de ligne, et lit les
guillemets d'une substitution entre guillemets comme le shell, accents
graves compris. Un `cd` qu'une telle substitution cite entre ses propres
guillemets (`"$(echo "; cd /tmp; ")"`) n'est plus lu comme une commande.

Ce qu'il laisse passer : ce que lance la substitution entre guillemets
elle-même (`echo "$(rm …)"`), et les autres formes de ce sujet (`eval`,
fonction, `CDPATH`, `cd` qui échoue, `env -C`, heredoc vu à tort, `"<"`,
options abrégées de sed), qui restent des risques acceptés (D-0111) ; un
`${…}` aux guillemets imbriqués entre guillemets, et un commentaire dans
le corps d'une substitution, qu'on n'écrit guère. `protege.fichiers`
attrape ensuite l'écriture d'un fichier protégé.

## Satisfait quand

- [x] une écriture d'un fichier protégé après un commentaire en fin de ligne, ou après une substitution aux guillemets imbriqués, est refusée par le hook, et un test le montre
