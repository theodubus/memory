<!-- socle: couche=backlog zone=publique -->
# B-0205 — Le hook de l'agent juge un chemin relatif depuis la racine de la session, pas depuis le dossier courant de l'agent

> statut : fait · origine : J-2026-11-13-H · ref : J-2026-11-14-AD · lu : backlog@f4a491f0

Le hook de l'agent rapporte un chemin écrit relatif à la racine de l'arbre
qu'il juge, quel que soit le dossier courant de l'agent (`cwd` de son
entrée), que l'outil Bash garde d'un appel à l'autre. Après un `cd engine`
lancé seul, `echo x > ../.socle/policy.toml` passe : le hook y voit
`<racine>/../.socle/policy.toml`, hors du projet. Le motif d'une écriture
(B-0171) se développe de même depuis la racine. Vu en mesurant les faux
refus de B-0171 ; seul `protege.fichiers` l'attrape ensuite. La piste :
partir du dossier courant quand il est dans l'arbre jugé, comme le fait
déjà `contournement` pour un `git -C`.

La correction de la revue de B-0171 (J-2026-11-13-H) fait partir du
dossier courant de l'agent les chemins écrits, leurs motifs, `$PWD` et la
remise d'un fichier protégé (`hooks.depart_de`). Reste un chemin relatif
que le hook lit pour juger une fuite de la mémoire privée : le fichier
qu'un `git commit -F`, un `gh … --body-file` ou un `gh api -F champ=@x`
publient se lit toujours depuis la racine (`hooks.textes_publies`) ; après
un `cd engine`, `git commit -F message.txt` fait lire au hook le
`message.txt` de la racine, pas celui du dossier `engine` que git publie.

## Fait quand

- [x] une écriture d'un fichier protégé par un chemin relatif au dossier courant de l'agent, sous la racine, est refusée par le hook, et un test le montre
- [x] le fichier qu'une commande publie (`-F`, `--body-file`) se lit depuis le dossier courant de l'agent, et un test le montre
