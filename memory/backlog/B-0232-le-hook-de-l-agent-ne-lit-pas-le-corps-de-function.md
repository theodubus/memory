<!-- socle: couche=backlog zone=publique -->
# B-0232 — Le hook de l'agent ne lit pas le corps de function f { … } sans parenthèses : un push forcé ou une suppression du projet y passent

> statut : ouvert · origine : J-2026-11-14-AL · priorité : haute · lu : backlog@1a5a32a1

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

## Fait quand

- [ ] `function f { git push --force origin main; }; f` et `function f { rm -rf ..; }; f` sont refusés par le hook, `function f { ls; }; f` passe, et un test le montre
