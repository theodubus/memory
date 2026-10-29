<!-- socle: couche=demandes zone=publique -->
# D-0047 — Choisir comment débloquer la PR #7, dont un ancien correctif ne prouve pas son défaut dans la CI

> date : 2026-10-29 · lu : decisions@d14040a2

## Décision demandée

Choisir comment faire passer la CI de la PR #7 (la branche de travail vers
`main`), que le contrôle des correctifs bloque sur un ancien commit dont le
test ne prouve rien dans l'environnement de la CI.

## Contexte

La CI de la PR #7 n'échoue que sur `tests.regression`, le contrôle qui
rejoue sur son commit parent le test de chaque correctif, et refuse un
test qui y passe déjà. Il bloque le correctif 8d7a044, « une sortie coupée
n'est plus une panne » (B-0070), écrit dans une session précédente. Son
test, `test_main_rend_la_main_sans_trace_quand_le_lecteur_ferme_le_tube`,
lance `socle checks` et ferme sa sortie. Sous Python 3.12, celui de la CI,
avec une sortie tamponnée comme sur GitHub, le parent ne laisse aucune
trace : le test passe sans le correctif. Avec `PYTHONUNBUFFERED=1`, comme
dans le conteneur de l'agent, il échoue sur le parent comme il le doit ;
c'est pourquoi la CI locale passait. Reproduit dans les deux cas.

La CI d'un push ne juge que les commits du push ; celle de la PR juge
toute la plage depuis `main`, où ce commit est. L'échec est déterministe :
relancer n'y change rien. Le défaut lui-même est prouvé ailleurs : le
correctif c9afeb1 a ajouté un test en processus qui échoue sans lui quelle
que soit la version de Python. Mais le contrôle juge chaque correctif par
son propre test, et l'historique déjà poussé ne se corrige pas sans le
réécrire.

## Éléments cités

- #7 — la pull request de la branche de travail vers `main`, ouverte par
  l'agent, que cette CI bloque.
- B-0070@905f57e8 — le sujet clos du backlog : une commande du socle dont
  la sortie est coupée plantait avec une trace Python.
- 8d7a044 — le correctif de B-0070, dont le test passe sur son parent dans
  la CI.
- c9afeb1 — le correctif de la même sortie coupée sous Python 3.14, avec un
  test qui échoue sans lui quelle que soit la version.

## Où regarder

- [la pull request](https://github.com/theodubus/memory/pull/7) : le
  commentaire de l'agent qui décrit l'échec, et la CI rouge sur
  `tests.regression`.
- [les tests de la ligne de commande](https://github.com/theodubus/memory/blob/7eaf25aeda72c8a229bcf8ba1b29556becf41a5d/tests/test_cli.py),
  la classe `TestTubeFerme` : le test de 8d7a044, puis celui de c9afeb1.
- [les contrôles des tests](https://github.com/theodubus/memory/blob/7eaf25aeda72c8a229bcf8ba1b29556becf41a5d/engine/socle/checks_tests.py),
  la fonction `regression` : ce qu'elle refuse, et qu'elle n'admet
  aujourd'hui aucune exception.

## Options

1. **Une exception validée par l'humain.** Le contrôle admet un correctif
   dont le test passe sur le parent quand une demande validée nomme son
   commit, et le dit en avertissement. Cette demande-ci, validée, nomme
   8d7a044 : la PR passe. Le mécanisme sert ensuite à tout projet, pour un
   test dont la preuve dépend de l'environnement. Effort : une heure, avec
   un test et un témoin sain dans l'auto-test. Risque faible : rien ne
   passe sans une validation qui nomme le commit, et la CI le montre.
   Réversible.
2. **Fusionner en passant outre la CI, une fois**, si la règle de `main`
   vous le permet. Effort : quelques minutes. Risque : la protection est
   contournée une fois ; la CI rouge reste sur la fusion. Le problème ne
   revient pas, puisque 8d7a044 sera dans `main`. Rien ne change dans le
   socle.
3. **Une CI sans tampon** : `PYTHONUNBUFFERED=1` dans la CI de ce dépôt,
   fichier protégé que vous approuvez. Effort : quelques minutes. Risque :
   la CI ne verrait plus les défauts liés au tampon, comme celui de Python
   3.14 qu'elle n'a pas vu. Réversible.
4. **Réécrire l'historique de la branche** pour donner à 8d7a044 un test
   qui prouve, puis la pousser de force. Effort : une heure. Risque élevé :
   les SHA que la mémoire cite comme preuves ne désigneraient plus rien.
   Difficile à défaire.

## Conséquences

- Si Théo valide (option 1) : le contrôle et son témoin s'écrivent, la CI
  de la PR passe avec un avertissement qui cite cette demande, et la PR se
  fusionne normalement.
- S'il choisit l'option 2, 3 ou 4 : je fais ma part, ou rien pour l'option
  2, qui est son geste.
- S'il refuse : la PR reste rouge ; rien ne se fusionne sur `main`, et
  chess comme le pilote s'installent depuis la branche de travail.
- Sans réponse : la PR reste ouverte et rouge.

## Recommandation

L'option 1.

Vérifié : sous Python 3.12 avec une sortie tamponnée, le test de 8d7a044
passe sur son parent, trois fois sur trois ; avec `PYTHONUNBUFFERED=1`, il
y échoue ; le test de c9afeb1 échoue sans le correctif sous les deux ; la
CI de la PR n'a aucun autre échec.

Supposé : que d'autres projets rencontrent un test dont la preuve dépend
de l'environnement, et que l'exception validée leur serve.

## Réponses possibles

- `valider` — option 1 : le contrôle admet un correctif que nomme une demande validée, et la PR passe avec cette demande.
- `fusion-forcee` — option 2 : Théo fusionne en passant outre la CI une fois ; rien ne change dans le socle.
- `ci-sans-tampon` — option 3 : la CI de ce dépôt tourne sans tampon de sortie, après l'approbation de Théo.
- `reecrire` — option 4 : l'historique de la branche est réécrit, après une demande pour la poussée forcée.
- `refuser` — la PR reste rouge ; les installations se font depuis la branche de travail.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
