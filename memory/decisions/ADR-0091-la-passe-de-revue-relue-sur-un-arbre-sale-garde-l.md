<!-- socle: couche=decisions zone=publique -->
# ADR-0091 — La passe de revue relue sur un arbre sale garde l'empreinte de ses changements, et la même passe s'y reconnaît

> statut : acceptée · date : 2026-11-19 · source : T-0054@103f3b8d, ADR-0084@df557d83 · lu : decisions@388fbc44

## Contexte

Le dossier de `socle review` juge l'arbre de travail : son diff part de
l'ancêtre commun et va jusqu'aux fichiers suivis modifiés, commités ou
non. La passe, elle, ne gardait que ses commits, `Commits :
<début>..<tête>` (ADR-0084@df557d83, point 2), et « la même passe » se
reconnaissait en comparant l'arbre au commit de tête. Sur un arbre sale,
une relance sans aucun changement était prise pour une passe nouvelle,
refusée sans recul, et la ligne disait `X..X` quand rien n'était commité,
comme si la passe n'avait rien relu (T-0054@103f3b8d).

## Décision

Quand l'arbre de travail change des fichiers suivis hors de la mémoire,
la passe garde, au bout de sa ligne, l'empreinte de ces changements :
`Commits : <début>..<tête> + arbre de travail <empreinte>` (`+ working
tree` en anglais), les douze premiers caractères hexadécimaux du SHA-256
du diff de la tête à l'arbre, hors de la mémoire. La même passe est celle
dont la tête existe et dont l'empreinte de l'arbre, mesurée depuis cette
tête, est la sienne, ou nulle pour une passe sans empreinte : un arbre
sale inchangé, puis ce même état commité, redonnent la même passe. Aucun
objet git n'est écrit, et une passe d'avant se lit comme avant.

## Conséquences

La ligne `Commits` ne dit plus `X..X` à tort : elle dit l'arbre relu. Le
format de la mémoire documente le suffixe et son mot. Un fichier non
suivi n'entre pas dans l'empreinte, comme il n'entre pas dans le diff du
dossier. Le défaire : retirer le suffixe à l'écriture et revenir à la
comparaison au seul commit de tête ; le lecteur garde le suffixe
facultatif, que les passes déjà écrites portent.
