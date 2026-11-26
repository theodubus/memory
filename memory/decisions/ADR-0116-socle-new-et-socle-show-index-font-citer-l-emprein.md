<!-- socle: couche=decisions zone=publique -->
# ADR-0116 — socle new et socle show --index font citer l'empreinte de l'index du dernier commit, et affichent celui de l'arbre

> statut : acceptée · date : 2026-11-26 · source : B-0362@d8be54cc, T-0202@9cc245ed, ADR-0023@38e556cb, ADR-0083@512e719c · lu : decisions@7b329a15

## Contexte

Le point 1 du retour d'usage de chess du 26 novembre (B-0362@d8be54cc) :
`socle new` et `socle show --index` font citer l'empreinte de l'index de
l'arbre de travail, les entrées du tour déjà écrites comprises.
`memoire.lectures` accepte une citation d'index qui désigne la base, un
commit de la plage ou l'arbre, sans l'entrée qui cite, ni celles du même
type ajoutées après elle, ni celles que la plage ajoute dans d'autres
formes (ADR-0023@38e556cb, ADR-0083@512e719c). Dès qu'une ligne de
l'index change avant le commit, un statut passé à « en-cours », une
décision « proposée » devenue « acceptée », un titre retouché, l'index de
l'arbre que citaient les entrées écrites avant ce changement n'existe
plus nulle part : elles sont refusées. Former un lot le déclenche à
chaque fois, et deux `socle new need … --task …` à la suite aussi, les
formes alternant. Le seul contournement, recopier l'empreinte courante
dans chaque entrée, vide la preuve de lecture de son sens.

## Décision

1. L'empreinte que `socle new` écrit dans une entrée du backlog ou une
   décision (`lu : backlog@…`, `lu : decisions@…`), et celle que
   `socle new` et `socle show --index` impriment en tête de l'index, est
   celle de l'index du dernier commit (`HEAD`). Ce commit est la base du
   travail ou un commit de la plage : le contrôle l'accepte toujours, quoi
   que l'arbre change avant le commit suivant. Sans base de travail, sans
   commit ou sans branche par défaut, c'est celle de l'arbre, comme avant :
   le hook de l'agent ne juge alors que l'arbre.
2. Les lignes imprimées restent celles de l'arbre : un doublon écrit dans
   le tour s'y voit. L'en-tête le dit quand les deux diffèrent.
3. Le besoin et sa tâche que crée `socle new need … --task …` citent tous
   deux cette empreinte.
4. Le contrôle et le hook ne changent pas : la preuve de lecture d'un
   index reste celle d'ADR-0023@38e556cb, qu'il a été consulté, pas une
   version de son contenu.

## Conséquences

Les entrées écrites dans un tour passent `memoire.lectures` quoi qu'il
change avant le commit, sans retouche de leur empreinte. Ce qu'une entrée
prouve ne s'affaiblit pas : l'index du dernier commit est une version que
l'agent a lue, avec en plus les lignes de son tour. La lecture de la
mémoire au dernier commit coûte une lecture git de plus à chaque
`socle new` et `socle show --index`. Pour défaire : rendre à
`cli._texte_index` et à `cli.cmd_new` l'empreinte de l'arbre.
