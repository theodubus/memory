<!-- socle: couche=demandes zone=publique -->
# D-0041 — Valider des noms neutres dans les données d'une classe du test de mutation (B-0082)

> date : 2026-10-22 · lu : decisions@2a93e7ab

## Décision demandée

Valider que les tests de la classe `TestAMesurer`, dans le fichier des
tests de mutation, remplacent dans leurs données et leurs valeurs
attendues deux noms de modules tirés d'un moteur d'échecs par des noms
neutres.

## Contexte

Le retrait du code de compatibilité a aussi retiré des données des tests
le vocabulaire des échecs, d'où vient le socle. Une classe y a échappé :
`TestAMesurer`, qui vérifie qu'un module « à mesurer » n'a pas encore de
plafond de mutation, que le verdict dit son compte de survivants, et que
`poser` écrit ce compte dans les seuils. Ses modules d'exemple s'appellent
encore `src/eval.rs` (l'évaluation d'une position) et `src/tt.rs` (la
table de transposition).

La demande validée le 20 octobre nommait la plupart des tests de cette
classe, mais pas `test_poser_ecrit_la_raison_dans_la_langue_du_projet`,
qui partage les mêmes données : changer les données de la classe change
donc une valeur attendue de ce test sans validation qui le nomme, et le
contrôle des tests protégés le refuse. La classe est restée telle quelle.

Ce qui change, dans les sept tests de la classe :
`test_un_module_a_mesurer_ne_casse_pas`,
`test_poser_ecrit_le_plafond_mesure`,
`test_poser_ecrit_la_raison_dans_la_langue_du_projet`,
`test_cmd_mutation_verdict_avec_poser`,
`test_poser_plafonds_ne_touche_que_les_modules_a_mesurer`,
`test_poser_les_autres_formes_de_cle` et `test_un_plafond_non_ecrit_est_dit`.
`src/eval.rs` devient `src/score.rs`, `src/tt.rs` devient `src/table.rs`,
dans les données et dans les assertions. Les comptes, les plafonds et les
messages attendus restent les mêmes ; ce que chaque test prouve ne change
pas. Les autres classes du fichier utilisent déjà ces noms neutres.

## Éléments cités

- B-0082@0d0c5c03 — le sujet du backlog qui relève les deux noms restés
  dans cette classe.
- D-0035@984515f3 — la demande validée le 20 octobre, qui a fait le même
  remplacement dans les autres classes du fichier.

## Où regarder

- [le fichier des tests de mutation](https://github.com/theodubus/memory/blob/13223681bf85ce7b842ee5deb2621736a66f5f1b/tests/test_mutation.py),
  classe `TestAMesurer` : vérifier que seuls les deux noms de modules
  changent, et que les autres classes utilisent déjà `src/score.rs` et
  `src/table.rs`.

## Options

- **Valider** : je fais le remplacement dans un commit, après `verify` et
  l'auto-test. Effort : quelques minutes. Risque faible : deux chaînes
  remplacées partout dans une classe. Réversible : un commit qui se
  défait.
- **Refuser** : la classe garde ses noms. Effort nul. Risque nul : ces
  tests sont de l'atelier, aucun projet ne les reçoit.

## Conséquences

- Si Théo valide : le remplacement est commité et B-0082 est clos.
- S'il refuse : B-0082 est clos sans changement ; les noms restent dans
  l'atelier seul.
- Sans réponse : rien ne change ; B-0082 reste ouvert.

## Recommandation

Valider, sans urgence.

Vérifié : les deux noms n'apparaissent que dans cette classe du fichier ;
le test `test_poser_ecrit_la_raison_dans_la_langue_du_projet` lit les
mêmes données que les six autres ; le contrôle des tests protégés a
refusé le changement faute d'une validation qui le nomme.

Supposé : que personne ne lise ces données comme un exemple, ce qui rend
l'enjeu purement de cohérence.

## Réponses possibles

- `valider` — je remplace les deux noms dans les sept tests nommés ci-dessus, et je clos B-0082.
- `refuser` — la classe garde ses noms ; B-0082 est clos sans changement.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
