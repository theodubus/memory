<!-- socle: couche=demandes zone=publique -->
# D-0044 — Valider le retrait du repli vers la section [code] de l'adaptateur maintenu, et la réécriture de son test (B-0076)

> date : 2026-10-22 · lu : decisions@d14040a2

## Décision demandée

Valider que je retire le dernier code de compatibilité du moteur, le repli
vers la section `[code]` de l'adaptateur maintenu, et que je réécrive sous
un nom nouveau le test qui le prouvait.

## Contexte

Le contrôle qui exige qu'une fonction publique ajoutée soit nommée par un
test lit, dans l'adaptateur du projet, la section `[code]` : quels fichiers
sont du code, lesquels n'en sont pas, et à quoi se reconnaît une fonction
privée. Quand un adaptateur n'a pas cette section, le moteur prend
aujourd'hui celle de l'adaptateur maintenu du même langage ; sans
adaptateur maintenu, il prend les sources hors fichiers de test, toute
fonction comptant comme publique.

Ce repli ne servait qu'aux projets installés avant que la section existe,
dont ce dépôt. Théo vient d'ajouter la section à l'adaptateur de ce dépôt.
Le repli peut partir, comme le reste du code de compatibilité retiré le 20
octobre. Mais un test le prouve, et le retirer change ses valeurs
attendues : sans section, les exclusions ne sont plus celles de
l'adaptateur maintenu, et plus aucune fonction n'est reconnue privée. La
demande du 20 octobre sur la compatibilité parlait de ce repli, mais ne
nommait pas ce test, et sa réponse ne validait rien.

Ce qui change :

- dans le moteur, la fonction qui lit la section `[code]` perd sa branche
  qui lit l'adaptateur maintenu ; sans section, elle rend les sources hors
  fichiers de test, comme elle le fait déjà sans adaptateur maintenu ;
- le test `test_section_code_de_l_adaptateur_maintenu_a_defaut` est
  supprimé ; à sa place, `test_sans_section_code_les_sources_hors_fichiers_de_test`
  vérifie ce cas restant : les sources pour chemins, les fichiers de test
  et le dossier du socle pour exclusions, aucun motif de fonction privée.

## Éléments cités

- B-0076@6645f88b — le sujet du backlog qui demandait à Théo la section
  `[code]` de l'adaptateur de ce dépôt, et annonçait le retrait du repli.
- D-0033@43487fd4 — la demande du 20 octobre sur le retrait du code de
  compatibilité, qui parlait de ce repli sans nommer son test.
- D-0043@8296fd66 — l'approbation de Théo pour son ajout de la section
  `[code]`, écrite par sa commande `socle approve`.
- bd1fc51 — le commit de Théo qui ajoute la section `[code]` à
  l'adaptateur de ce dépôt.

## Où regarder

- [les tests du code nommé par un test](https://github.com/theodubus/memory/blob/00ef2d5e1a97440c9815de0d820286aec4f5a7a3/tests/test_code_teste.py),
  le test `test_section_code_de_l_adaptateur_maintenu_a_defaut` : vérifier
  que sa première moitié prouve le repli, et la seconde le cas qui reste.
- [les contrôles des tests](https://github.com/theodubus/memory/blob/00ef2d5e1a97440c9815de0d820286aec4f5a7a3/engine/socle/checks_tests.py),
  la fonction `config_code` : le repli est la branche qui lit
  l'adaptateur maintenu.

## Options

- **Valider** : je retire le repli et réécris le test, après `verify` et
  l'auto-test, puis je clos B-0076. Effort : quelques minutes. Risque
  faible : la section est désormais dans l'adaptateur de ce dépôt, et un
  projet neuf la reçoit de l'installeur. Réversible : un commit qui se
  défait.
- **Refuser** : le repli et son test restent ; B-0076 est clos sans
  retrait. Effort nul, risque nul.

## Conséquences

- Si Théo valide : le moteur n'a plus aucun code de compatibilité, et
  B-0076 est clos.
- S'il refuse : le repli reste, inutile mais sans effet, et B-0076 est clos.
- Sans réponse : rien ne change ; B-0076 reste ouvert.

## Recommandation

Valider.

Vérifié : la section `[code]` est dans l'adaptateur de ce dépôt depuis le
commit de Théo ; aucune validation ne nomme ce test ; l'installeur pose la
section dans tout projet neuf, avec l'adaptateur de son langage.

Supposé : qu'aucun projet installé hors de ce dépôt ne dépende du repli,
comme Théo l'a dit (personne n'a encore utilisé le socle).

## Réponses possibles

- `valider` — je retire le repli, je remplace `test_section_code_de_l_adaptateur_maintenu_a_defaut` par `test_sans_section_code_les_sources_hors_fichiers_de_test`, et je clos B-0076.
- `refuser` — le repli et son test restent ; B-0076 est clos sans retrait.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
