<!-- socle: couche=decisions zone=publique -->
# ADR-0029 — Ce que le moteur relit s'écrit dans la langue du projet et se lit dans les deux ; le nom du travail de CI ne change pas à la mise à jour

> statut : acceptée · date : 2026-10-14 · lu : decisions@c92d474a

## Contexte

ADR-0028@b2a6af9a met les messages du moteur dans la langue du projet, par
un catalogue dont la clé est le message français. B-0059@7616358e relève ce qu'un
projet anglais lit encore en français, hors de ce catalogue : des textes
écrits dans les adaptateurs, les workflows de CI, et des marques que le
moteur écrit puis relit lui-même (le marqueur d'une valeur liée, la raison
d'un plafond de mutation mesuré). Ces marques, et le nom du travail de CI
qu'une protection de branche exige, ne peuvent pas simplement changer de
langue : ce qui les relit, le moteur ou GitHub, les attend sous un nom.

## Décision

- Les textes écrits ailleurs que dans le code (textes `absent` et
  `replacement` des adaptateurs, noms de leurs étapes de CI, descriptions
  des défauts et des témoins de l'auto-test) restent en français à leur
  source et passent par le catalogue à l'affichage ; un test exige que
  chacun y soit.
- Les workflows de CI ont un gabarit par langue (`socle.en.yml`,
  `mutation.en.yml`).
- Ce que le moteur écrit puis relit s'écrit dans la langue du projet et se
  lit dans les deux : `<!-- valeur:… -->` ou `<!-- value:… -->`, `mesuré le …
  : N survivant(s)` ou `measured on …: N survivor(s)`.
- Le statut d'une demande reste une valeur interne, comparée par le
  moteur ; seul son affichage suit la langue.
- Le nom du travail de CI est celui qu'une protection de branche exige : une
  mise à jour garde celui qui est en place, quelle que soit la langue du
  gabarit, et le dit.

## Conséquences

Un projet anglais neuf ne lit plus de français dans ce que le socle pose ou
affiche. Un projet existant garde son nom de travail : sa protection de
branche ne casse pas ; pour l'aligner sur la langue, l'humain renomme le
travail et sa règle ensemble. Un adaptateur écrit par un projet garde ses
propres textes, que le catalogue ne connaît pas : ils s'affichent tels quels.
Pour défaire : retirer les gabarits anglais et les traductions ; les
marques anglaises déjà écrites resteraient lues tant que les expressions
régulières les acceptent.
