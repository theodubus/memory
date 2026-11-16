<!-- socle: couche=backlog zone=publique -->
# B-0209 — La revue juge le lot contre le critère et le modèle de menace de ses sujets : seuls les constats bloquants se corrigent dans le lot

> statut : fait · origine : J-2026-11-13-J · priorité : haute · lu : backlog@33a4d320 · ref : J-2026-11-13-M

Le lot de B-0010 et B-0171, le 13 novembre, a pris quatre revues et
trois corrections pour deux sujets, quand une revue rend d'ordinaire 3 à
7 constats en une passe (J-2026-11-13-J). La revue (le skill
`socle-review` et le dossier de `socle review`) demande au relecteur de
prendre le lot en défaut sans lui dire contre quoi s'arrêter : ni le
critère « Fait quand » des sujets comme barre, ni le modèle de menace d'un
garde-fou, ni la différence entre un constat bloquant et un constat pour
le backlog. Et le skill dit de corriger chaque constat fondé dans le lot.
Sur un sujet sans fond, comme deviner ce qu'une commande de bash écrit
(B-0171), chaque tour trouve une forme de plus, et chaque correction,
faite par un sous-agent sans contexte qui rapièce constat par constat,
ouvre des régressions (sept au second tour de B-0171). Sur B-0010, un tour
a été perdu parce que la répartition de la borne n'a été choisie qu'après
la première revue, faute de spécification avant le code.

Théo l'ouvre en priorité haute, dans l'ensemble à finir avant les
nouvelles fonctions (D-0109@379b5396). Le skill du projet `delegate-lot`
(ses consignes au relecteur et au correcteur, sa règle de seconde revue)
suit le même changement.

## Satisfait quand

- [x] le dossier de `socle review` donne au relecteur le critère « Fait quand » des sujets du lot et, pour un garde-fou, son modèle de menace, et lui demande de classer chaque constat : bloquant (contredit un critère, régression, perte de données, contournement dans le modèle de menace) ou pour le backlog ; un test le montre
- [x] le skill `socle-review` dit que seuls les constats bloquants se corrigent dans le lot, les autres vont au backlog, et qu'une seconde revue ne porte que sur la correction de bloquants lourde
- [x] un sujet qui pose ou change un garde-fou écrit son modèle de menace avant son code, et un sujet dont la conception n'est pas tranchée, sa spécification avant son code
