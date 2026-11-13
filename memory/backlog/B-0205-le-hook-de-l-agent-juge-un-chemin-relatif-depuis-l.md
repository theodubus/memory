<!-- socle: couche=backlog zone=publique -->
# B-0205 — Le hook de l'agent juge un chemin relatif depuis la racine de la session, pas depuis le dossier courant de l'agent

> statut : ouvert · origine : J-2026-11-13-H · lu : backlog@f4a491f0

Le hook de l'agent rapporte un chemin écrit relatif à la racine de l'arbre
qu'il juge, quel que soit le dossier courant de l'agent (`cwd` de son
entrée), que l'outil Bash garde d'un appel à l'autre. Après un `cd engine`
lancé seul, `echo x > ../.socle/policy.toml` passe : le hook y voit
`<racine>/../.socle/policy.toml`, hors du projet. Le motif d'une écriture
(B-0171) se développe de même depuis la racine. Vu en mesurant les faux
refus de B-0171 ; seul `protege.fichiers` l'attrape ensuite. La piste :
partir du dossier courant quand il est dans l'arbre jugé, comme le fait
déjà `contournement` pour un `git -C`.

## Fait quand

- [ ] une écriture d'un fichier protégé par un chemin relatif au dossier courant de l'agent, sous la racine, est refusée par le hook, et un test le montre
