<!-- socle: couche=demandes zone=publique -->
# D-0049 — Choisir comment débloquer la PR #10, dont un correctif échoue sur lui-même dans la CI

> date : 2026-10-30 · lu : decisions@828266d1

## Décision demandée

Choisir comment faire passer la CI de la PR #10, que le contrôle des
correctifs bloque sur un commit déjà poussé dont le test échoue sur
lui-même dans l'environnement de la CI de GitHub.

## Contexte

La CI de la PR #10 n'échoue que sur `tests.regression`, le contrôle qui
rejoue le test de chaque correctif sur son parent, où il doit échouer, puis
sur le correctif lui-même, où il doit passer. Il bloque le correctif
b61611e, celui du nom de l'humain (B-0094) : sur ce commit, un test de
l'installeur, `test_l_installation_dit_quoi_faire_ensuite`, échoue. La
nouvelle étape « écrire ton nom » ne s'affiche que sans nom git ; la CI de
GitHub n'a pas d'identité git, ce conteneur en a une ; elle s'y plaçait
avant l'étape que le test attend en troisième. Le commit suivant, 1c01c86,
l'a déplacée : la tête de la PR passe tous ses tests, sur GitHub comme ici.
Reproduit ici sans identité git : le contrôle échoue de même ; avec
l'identité du conteneur, il passe.

Le contrôle juge chaque correctif par son propre commit, et l'historique
déjà poussé ne se corrige pas sans le réécrire. Pour que cela ne se
reproduise pas, la suite de tests ignore désormais la configuration git de
la machine, comme sur GitHub.

## Éléments cités

- #10 — la pull request de la branche de travail vers `main`, ouverte par
  l'agent, avec les correctifs du deuxième retour du pilote.
- B-0094@5e0722d0 — le sujet clos : en session cloud, l'installeur prenait le
  nom git de l'agent pour celui de l'humain.
- b61611e — le correctif de B-0094, dont le test échoue sur lui-même dans la
  CI de GitHub.
- 1c01c86 — le commit suivant, qui déplace l'étape et rend le test vert.
- D-0047@b6b624e3 — la demande du 29 octobre : une demande validée qui
  nomme un correctif l'admet quand son test passe déjà sur le parent.
- B-0048@a359bf6f — le sujet ouvert du backlog : une action externe validée par une
  demande reste refusée par le hook de l'agent.

## Où regarder

- [la pull request](https://github.com/theodubus/memory/pull/10) : sa CI
  rouge sur `tests.regression`, et le commentaire de l'agent qui décrit
  l'échec.
- [les contrôles des tests](https://github.com/theodubus/memory/blob/a74a30d87f7d2e246c1c02e4ba5a7486c77ea062/engine/socle/checks_tests.py),
  la fonction `regression` : l'exception de D-0047 ne couvre que le test qui
  passe sur le parent, pas celui qui échoue sur le correctif.
- [les tests de l'installation](https://github.com/theodubus/memory/blob/a74a30d87f7d2e246c1c02e4ba5a7486c77ea062/tests/test_initialisation.py),
  le test `test_l_installation_dit_quoi_faire_ensuite`, qui attend l'étape
  « ouvrir l'agent » en troisième.

## Options

1. **Étendre l'exception de D-0047.** Une demande validée qui nomme un
   correctif l'admet aussi quand son test échoue sur lui-même dans la CI, et
   le contrôle le dit en avertissement. Cette demande-ci, validée, nomme
   b61611e : la PR passe. Effort : une demi-heure, avec un test. Risque
   faible : rien ne passe sans une validation qui nomme le commit.
   Réversible.
2. **Fusionner en passant outre la CI, une fois**, si la règle de `main`
   vous le permet. Effort : quelques minutes. Risque : la protection est
   contournée une fois, la CI rouge reste sur la fusion. Rien ne change dans
   le socle.
3. **Réécrire l'historique de la branche**, en fondant 1c01c86 dans
   b61611e, puis le pousser de force. Effort : une demi-heure. Risque : une
   poussée forcée, que le hook refuse à l'agent même validée : vous
   la feriez depuis un terminal. Difficile à défaire.

## Conséquences

- Si Théo valide (option 1) : l'exception et son test s'écrivent, la CI de
  la PR passe avec un avertissement qui cite cette demande, et la PR se
  fusionne normalement.
- S'il choisit l'option 2 ou 3 : je fais ma part, ou rien pour l'option 2,
  qui est son geste.
- S'il refuse : la PR reste rouge ; rien ne se fusionne sur `main`. Le
  pilote n'en dépend pas : ses correctifs ne servent qu'aux installations
  suivantes.
- Sans réponse : la PR reste ouverte et rouge.

## Recommandation

L'option 1, comme pour D-0047.

Vérifié : sans identité git, le contrôle refuse b61611e et lui seul ; avec
l'identité du conteneur, il passe ; la tête de la PR passe la suite entière
sans identité git.

Supposé : qu'un correctif dont la preuve dépend de l'environnement se
représente ailleurs, et que l'exception étendue y serve.

## Réponses possibles

- `valider` — option 1 : le contrôle admet aussi un correctif qui échoue sur lui-même quand une demande validée le nomme, et la PR passe avec cette demande.
- `fusion-forcee` — option 2 : Théo fusionne en passant outre la CI une fois ; rien ne change dans le socle.
- `reecrire` — option 3 : l'historique de la branche est réécrit, et Théo pousse de force depuis un terminal.
- `refuser` — la PR reste rouge ; rien ne se fusionne sur `main`.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
