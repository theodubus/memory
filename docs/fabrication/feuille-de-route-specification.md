# La feuille de route au format A2-d : spécification

Spécification de B-0364 : `socle roadmap` doit permettre à l'humain de
piloter son projet, lue sur un téléphone. Elle met en œuvre deux
décisions de Théo du 26 novembre : la forme validée remplace les deux
formats actuels, compact et détaillé, partout, dans le terminal, dans la
conversation et dans le résumé de la CI (D-0212) ; cette forme est la
variante A2-d de `docs/fabrication/maquettes-feuille-de-route.md`
(D-0214).

## Ce qui ne va pas aujourd'hui

`socle roadmap` a deux formats. Le compact (`text`) aligne une ligne par
jalon et par lot, en colonnes, avec des identifiants. Le détaillé
(`markdown`) donne une légende de huit symboles et un tableau de tâches
par lot. Sur le téléphone, l'application défait les tableaux cellule par
cellule, les titres sont coupés, le travail en cours hors de tout jalon
passe avant les étapes, et un même besoin paraît deux ou trois fois
(J-2026-11-26-AB). La section du socle installée dit en outre de coller
le format détaillé, quand une consigne d'un projet peut demander le
court.

## La forme

Une seule forme, en quatre parties, dans cet ordre :

```text
La suite de <projet> — <date>

Maintenant
 ▶ <titre du lot en cours>
   reste : <titres de ses tâches ouvertes>

Ensuite
1. [K/N] <titre du premier jalon ouvert>
         ✓ <besoin clos>
         ▶ <besoin en cours>
         · <besoin ouvert>
2. [K/N] <titre du jalon suivant>

Pour toi : <ce que l'humain a à faire ou à décider>
En réserve : <n> besoins, dont <p> prioritaires
```

**L'en-tête.** Le nom du projet, celui du dossier de sa racine, et la
date du jour.

**Maintenant.** Chaque lot `en-cours`, une ligne `▶` chacun, dans
l'ordre d'exécution ; sous lui, `reste :` et les titres de ses tâches
ouvertes, trois au plus, puis « et <n> autres ». Sans lot en cours, la
première tâche prête : `prête : <titre>`. Sans l'une ni l'autre :
`Maintenant : rien en cours`. Le travail hors de tout jalon n'a pas
d'autre place : il est ici, en tête, et nulle part ailleurs.

**Ensuite.** Les jalons ouverts, dans l'ordre d'exécution, numérotés à
partir de 1. Chacun : `[K/N]`, ses besoins clos sur leur total, puis son
titre. Les crochets ont tous la même largeur, comme la maquette : `K` et
`N` prennent la largeur du plus grand total, `K` aligné à droite et `N` à
gauche (`[ 1/4 ]`, `[ 2/12]`) ; les numéros des étapes s'alignent à
droite, et les titres commencent tous à la même colonne. Seul le premier jalon
ouvert, l'étape suivante, est déplié en ses besoins, dans l'ordre de son
`après`, alignés sous son titre : `✓` clos, `▶` servi par une tâche d'un
lot en cours, `·` autre. `--all` déplie tous les jalons. Un projet sans
jalon n'a pas cette partie.

**Pour toi.** Une ligne par geste de l'humain : chaque entrée `pour :
humain` ouverte et chaque demande en attente, par son titre. Rien à
faire : la ligne ne paraît pas.

**En réserve.** Les besoins ouverts hors de tout jalon, comptés, et
parmi eux ceux de priorité haute ; ni ceux qu'un lot en cours sert,
déjà sous « Maintenant », ni ceux pour l'humain, déjà sous « Pour toi ».
Aucun : la ligne ne paraît pas.

**Une alerte**, seulement s'il y en a : une ligne `Attention :` qui dit
un lot ou un besoin bloqué, ou deux lots dont l'ordre n'est pas déduit.
Les besoins à découper et ceux à fermer restent à l'état
(`socle state`), qui sert l'agent ; la feuille de route sert l'humain.

**Un titre** se lit jusqu'à son premier « : » suivi d'une espace, comme
aujourd'hui, hors d'une citation entre guillemets ou d'un code en ligne ;
cette tête se coupe au-delà de 72 caractères, d'un « … ». Dans le
terminal, une ligne passe à la suivante à 48 caractères, la largeur d'un
bloc de code sur un téléphone, sous sa propre colonne ; l'identifiant
reste collé au dernier mot du titre.

## Deux rendus d'une même forme

- **Le terminal** (`socle roadmap`, `--format text`, par défaut) : du
  texte brut, aligné, chaque titre suivi de son identifiant entre
  parenthèses. Une demande en attente se dit par son titre seul, sans
  identifiant : collé dans une réponse, ce rendu ne cite aucune demande
  sans son lien. C'est le rendu que le skill `socle-batch` colle, dans un
  bloc de code, au récap de la clôture d'un lot.
- **La conversation et le résumé de la CI** (`--format markdown`) : les
  mêmes lignes en Markdown, sans identifiant affiché. Chaque titre est un
  lien vers son entrée (le permalien de `socle url`) ; le compte `[K/N]`
  est dans un code en ligne, en police fixe, ce qui garde les titres
  alignés ; les besoins dépliés sont une liste imbriquée. Chaque demande
  en attente est un lien.

Les deux rendus disent la même chose dans le même ordre : seul le moyen
de désigner une entrée change.

## Ce qui disparaît

Le format compact en colonnes, le format détaillé et ses tableaux, la
légende des symboles, la ligne « Hors lot », et l'option `--by`, qui
choisissait de lire par lot ou par besoin : la forme suit les jalons. Pas
de compatibilité avec l'ancien appel (C-0019) : `--by` est refusé comme
une option inconnue.

## Ce qui change avec elle

- **L'état** : sa ligne `la suite : `python3 .socle/socle roadmap``
  perd « (détaillée : `--format markdown`) ».
- **La section du socle installée** garde « coller dans la réponse la
  sortie de `python3 .socle/socle roadmap --format markdown` » : il n'y
  a plus qu'une forme, et la consigne d'un projet qui demande le format
  court ne la contredit plus (le second critère de B-0364).
- **`FORMAT.md`** prend pour exemple de consigne un autre sujet que le
  format de la feuille de route.
- **Le guide** montre la forme, en ses deux rendus.
- **La CI posée** écrit le rendu Markdown dans le résumé de son
  exécution, comme aujourd'hui.
- **Une note de version**, française et anglaise, et son point au prompt
  de la mise à jour de chess.

## Les tests

Le calcul de la suite (`calculer`, l'ordre d'exécution, la fenêtre des
lots) ne change pas, et ses tests restent. Les tests qui lisent le
format compact ou le format détaillé, dans `tests/test_suite_du_projet.py`
(les classes `TestFormats` et `TestLesFormatsValides`, et ceux de
`TestLOrdreDExecution`, `TestCommande` et `TestDeclencheurs` qui lisent
un format ou l'option `--by`), sont remplacés par des tests de la forme.
Supprimer un test ou changer une valeur attendue exige une demande
validée : elle nomme chacun, avec ce qui le remplace, une fois le code
écrit et les tests qu'il change connus.

Les tests nouveaux prouvent, en français et en anglais : l'ordre des
quatre parties ; l'alignement des crochets et des titres, un total à deux
chiffres compris ; le seul premier jalon déplié, et `--all` ; les trois
marques d'un besoin ; le travail hors jalon sous « Maintenant » et nulle
part ailleurs ; aucun identifiant de demande dans le rendu du terminal,
un lien pour chaque demande dans le rendu Markdown ; aucune ligne vide de
« Pour toi » ou de « En réserve » ; aucun tableau.
