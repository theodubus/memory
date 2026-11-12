<!-- socle: couche=decisions zone=publique -->
# ADR-0069 — Le renommage d'un fichier toléré se règle dans la pull request qui renomme, et la clé dit le genre de faute

> statut : acceptée · date : 2026-11-12 · lu : decisions@37139d11

## Contexte

La seconde revue de B-0180@fe4775a9 (B-0189@f5fb31de) trouve six constats sur
ADR-0068@c9c2cfbd, déjà poussée. Le principal : un fichier renommé ne
garde sa tolérance que dans la pull request qui le renomme. Le jugement
suit le renommage en silence, la liste garde l'ancien nom, la pull request
suivante n'a plus de renommage dans sa plage et échoue, et y réparer la
liste ajoute une clé, ce qui exige une demande validée. Ensuite, la clé
d'un chemin cité inexistant est celle d'un lien mort vers la même cible :
le second passe à la place du premier corrigé. Ces corrections durcissent
ou rendent vrai ce que la décision promettait : décidées ici, sans demande.

## Décision

Elle amende les points 1 à 4 d'ADR-0068 ; le reste tient.

1. *Le renommage se règle dans la pull request qui renomme.* Au
   jugement, un constat dont le fichier est renommé dans la plage, et dont
   la liste porte encore la clé sous l'ancien nom, n'est pas toléré en
   silence : il reste une erreur, dont le message dit de renommer la clé
   dans `[adoption.tolerated]`, de l'ancienne à la nouvelle, toutes deux
   écrites en entier. Le cliquet laisse passer une clé renommée avec son
   fichier. Pour les clés de l'adoption, au jugement comme au cliquet, les
   renommages se lisent depuis le point de divergence avec la branche par
   défaut, ajoutés à ceux de la plage de l'étage
   (`Contexte.renommes_adoption`) : la liste corrigée passe au pre-push et à
   la CI d'un push qui ne contient plus le renommage ; sans branche par
   défaut lisible, la plage seule. Ainsi : la liste corrigée rend la CI verte, et la
   pull request suivante n'a plus rien à suivre. Une clé ainsi en attente
   de renommage ne se dit pas « résorbée ».
2. *L'avertissement « résorbé » cite la clé telle qu'elle est dans la
   liste*, celle qu'il faut en retirer, et non sa forme suivie.
3. *Un chemin peut contenir « — ».* `context.cle_renommee` reconnaît le
   fichier d'une clé à son préfixe « ancien nom — », le plus long, au lieu
   de couper au premier tiret long.
4. *La mise à jour d'un projet adopté avant la règle suit les renommages
   de la branche* : les clés de la base passent par les renommages entre
   la base et l'arbre avant d'être comparées aux constats présents ; un
   fichier renommé sur la branche garde ses constats anciens, consignés
   sous son nouveau nom, et l'installeur le dit.
5. *La clé dit le genre de faute quand deux genres citent la même valeur.*
   Un chemin cité inexistant a pour objet `chemin:<cible>` ; celui d'un
   lien mort (la cible) et celui d'un identifiant (l'identifiant) ne
   changent pas, des tests poussés les attendent. Les messages de
   `docs.valeurs` et de `tests.attendus` passent par `trad` et gardent leur
   source française : leur clé ne dépend plus de la langue.

## Conséquences

Renommer un fichier qui porte un constat toléré coûte une ligne de plus
dans la même pull request, que le contrôle dicte. Un chemin cité déjà
consigné sous l'ancien objet (sa cible seule) cesserait d'être toléré :
un constat par chemin cité inexistant ainsi consigné. Rien n'a été
distribué sous cette forme : B-0180 n'est pas encore fusionné.

Limites laissées. L'objet de `tests.creux` reste le nom du test sans sa
classe : deux tests de même nom dans deux classes d'un fichier partagent
une clé, mais l'y ajouter changerait une clé qu'un test poussé attend
(`sans assertion test_rien`). L'objet de `docs.copie` (`copie en <fichier>`)
ne dit pas le paragraphe copié : deux copies vers le même fichier
partagent une clé et se comptent, et un paragraphe copié remplacé par un
autre vers le même fichier passe à sa place. Une clé dont le fichier
renommé `a` est aussi le début d'un autre chemin toléré `a — b` reste
ambiguë : le préfixe le plus long l'emporte. La tolérance se compte par
clé (ADR-0068) : un fichier supprimé dont la clé reste dans la liste, puis
un autre fichier renommé vers ce chemin avec un constat neuf de même
objet, et le constat neuf prend la place de l'ancien, sans que le nombre
de constats tolérés monte. Seul un renommage que git reconnaît se suit :
un `git mv` et une réécriture presque complète dans le même commit, ou à
l'étage agent un `mv` sans `git add`, donnent des erreurs simples, et la
liste corrigée est refusée par le cliquet ; commiter le renommage seul,
avant de modifier le fichier, à défaut corriger le constat, ou une demande
validée.

Pour défaire : rétablir le suivi silencieux au jugement, qui reporte
l'échec à la pull request suivante.
