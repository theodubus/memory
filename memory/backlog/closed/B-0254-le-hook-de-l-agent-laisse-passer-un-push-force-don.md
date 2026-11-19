<!-- socle: couche=backlog zone=publique -->
# B-0254 — Le hook de l'agent laisse passer un push forcé dont l'option vient des arguments d'une fonction ou d'une variable

> statut : fait · origine : J-2026-11-16-B · priorité : haute · lu : backlog@1e6f341a · ref : J-2026-11-19-U, J-2026-11-19-AM

La seconde revue du lot L-0004 (J-2026-11-16-B) : `irreversible`
(`engine/socle/hooks.py`) lit l'argv d'un `git push` tel qu'il est écrit,
et aucun autre étage ne refuse un push forcé (le hook avant envoi ne le
cherche pas). Passent, avant le lot comme après : `f() { git push "$@";
}; f --force origin travail`, `F=--force; git push $F origin travail`,
`git push "$X" origin travail`. Le modèle de menace du hook (ADR-0080)
juge un push forcé quelle qu'en soit la forme, et celui de B-0232 le
nomme par une fonction : un sujet, de priorité haute.

La piste : juger l'argv développé (les variables connues de la commande),
refuser un push dont un argument est inconnu (une variable qu'il ne
connaît pas, `"$@"` dans le corps d'une fonction), comme ADR-0072 juge un
chemin inconnu, et lire les arguments de l'appel d'une fonction dont le
corps pousse.

## Satisfait quand

- [x] un push forcé arrête l'agent au hook même quand son option vient d'une variable ou des arguments d'une fonction, et un push ordinaire dont la branche vient d'une variable connue passe
