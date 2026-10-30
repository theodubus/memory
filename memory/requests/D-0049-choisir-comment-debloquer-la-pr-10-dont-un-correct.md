<!-- socle: couche=demandes zone=publique -->
# D-0049 — Choisir comment débloquer la PR #10, dont un correctif échoue sur lui-même dans la CI

> date : 2026-10-30 · lu : decisions@828266d1

## Décision demandée

Choisir comment faire passer la CI de la PR #10, que le contrôle des
correctifs bloque sur un commit déjà poussé : soit en retirant ce commit
de l'historique, soit en l'acceptant tel qu'il est.

## Contexte

**Ce que fait le contrôle.** `tests.regression` ne tourne que dans la CI.
Pour chaque commit marqué correctif (sujet `fix:` ou trailer `Corrige:`),
il reprend les fichiers de test que ce commit a changés et les exécute
deux fois : sur le commit parent, où ils doivent échouer, ce qui prouve que
le test voit le défaut ; puis sur le correctif lui-même, où ils doivent
passer, ce qui prouve que le correctif le corrige. Il juge chaque correctif
tel qu'il est dans l'historique, pas la tête de la branche.

**Ce qui échoue.** b61611e, le correctif du nom de l'humain (B-0094), a changé deux
fichiers de test, dont celui de l'installeur. Ses tests nouveaux passent
bien : ils échouent sur le parent et passent sur lui. Mais sur b61611e, un
test plus ancien du même fichier échoue,
`test_l_installation_dit_quoi_faire_ensuite`. Il attend « ouvrir l'agent »
en troisième étape après l'installation. Or b61611e a ajouté une étape
« écrire ton nom », qui ne s'affiche que si l'installeur ne trouve aucun
nom, et l'a placée avant. La CI de GitHub n'a pas d'identité git : l'étape
s'y affiche et décale la liste, le test échoue. Ce conteneur a une
identité git (« Claude ») : l'étape ne s'y affichait pas, et le test
passait. b61611e a donc vraiment cassé ce test, mais seulement là où aucun
nom n'est connu ; le contrôle a raison sur ce commit.

**Ce qui est déjà corrigé.** Le commit suivant, 1c01c86, a déplacé l'étape
après « ouvrir l'agent » : sur la tête de la PR, tous les tests passent,
sur GitHub comme ici. La suite de tests ignore désormais la configuration
git de la machine : elle ne peut plus passer ici en échouant sur GitHub.

**Pourquoi un commit de plus n'y change rien.** La CI d'une PR juge toute
la plage depuis `main`. Tant que b61611e est dans cette plage, le contrôle
le rejoue et le refuse, quel que soit ce qui vient après. Il n'en sort que
de deux façons : en disparaissant de l'historique (options 1 et 2), ou en
entrant dans `main`, après quoi aucune plage future ne le contient
(options 3 et 4, qui l'acceptent tel qu'il est).

## Éléments cités

- #10 — la pull request de la branche de travail vers `main`, ouverte par
  l'agent, avec les correctifs du deuxième retour du pilote.
- B-0094@5e0722d0 — le sujet clos : en session cloud, l'installeur prenait le
  nom git de l'agent pour celui de l'humain.
- b61611e — le correctif de B-0094, dont un test du fichier qu'il change
  échoue sur lui-même sans identité git.
- 1c01c86 — le commit suivant, qui déplace l'étape et rend ce test vert.
- D-0047@b6b624e3 — la demande du 29 octobre : une demande validée qui
  nomme un correctif l'admet quand son test passe déjà sur le parent.
- B-0048@a359bf6f — le sujet ouvert du backlog : une action externe validée par une
  demande reste refusée par le hook de l'agent.

## Où regarder

- [la pull request](https://github.com/theodubus/memory/pull/10) : sa CI
  rouge sur `tests.regression`, et le commentaire de l'agent qui décrit
  l'échec.
- [les contrôles des tests](https://github.com/theodubus/memory/blob/a74a30d87f7d2e246c1c02e4ba5a7486c77ea062/engine/socle/checks_tests.py),
  la fonction `regression` : le rejeu sur le parent puis sur le correctif ;
  l'exception de D-0047 ne couvre que le premier.
- [les tests de l'installation](https://github.com/theodubus/memory/blob/a74a30d87f7d2e246c1c02e4ba5a7486c77ea062/tests/test_initialisation.py),
  le test `test_l_installation_dit_quoi_faire_ensuite`, qui attend l'étape
  « ouvrir l'agent » en troisième.

## Options

Les deux premières retirent le commit cassé de l'historique : le contrôle
passe parce qu'il n'y a plus rien à refuser. Les deux dernières gardent ce
commit et l'acceptent : l'une une fois, sans trace dans le socle, l'autre
par une validation écrite qui le nomme.

1. **Refaire la PR sur une branche neuve.** Je recrée ses changements depuis
   `main` sur une branche neuve, où b61611e et 1c01c86 ne font qu'un commit,
   correct sur GitHub ; je ferme la PR #10 et en ouvre une autre. Rien n'est
   contourné ni relâché. Effort : une demi-heure, et votre accord pour
   pousser sur cette branche neuve, où je continue ensuite. Risque : les
   SHA b61611e et 1c01c86, cités dans le journal, ne désignent plus que
   l'ancienne branche, qui reste. Réversible.
2. **Réécrire la branche actuelle.** Même résultat sur la même branche et la
   même PR, mais il faut une poussée forcée, que le hook refuse à l'agent
   même validée : vous la feriez depuis un terminal. Effort : une
   demi-heure, et un geste à vous. Difficile à défaire.
3. **Admettre ce commit par une demande validée.** Le contrôle apprend
   qu'une demande validée qui nomme un correctif l'admet aussi quand son
   test échoue sur lui-même, en avertissement qui cite la demande ; celle-ci
   nomme b61611e. Le contrôle ne se relâche pour aucun autre commit : chaque
   admission exige votre validation, qui nomme le commit et reste dans la
   mémoire. C'est le mécanisme de D-0047, étendu à ce cas. Effort : une
   demi-heure, avec un test. Réversible.
4. **Fusionner une fois en passant outre la CI**, si la règle de `main` vous
   le permet. Rien ne change dans le socle ; b61611e entre dans `main` et ne
   se rejoue plus. Effort : quelques minutes. Risque : la protection est
   contournée une fois, sans trace dans la mémoire, et la CI rouge reste sur
   la fusion.

## Conséquences

- Option 1 ou 2 : l'historique de la PR ne contient plus de commit cassé, et
  sa CI passe sans exception.
- Si Théo valide (option 3) : la CI de la PR passe avec un avertissement
  qui cite cette demande ; le mécanisme sert ensuite à tout projet.
- Option 4 : rien à faire de mon côté.
- S'il refuse : la PR reste rouge ; rien ne se fusionne sur `main`. Le
  pilote n'en dépend pas : ses correctifs ne servent qu'aux installations
  suivantes.
- Sans réponse : la PR reste ouverte et rouge.

## Recommandation

L'option 1 : elle retire le défaut au lieu de l'accepter, sans geste à
vous ni poussée forcée. L'option 3 reste raisonnable si vous préférez
garder la PR #10 telle quelle : elle n'admet que ce commit, nommé.

Vérifié : sans identité git, le contrôle refuse b61611e et lui seul ; avec
l'identité du conteneur, il passe ; la tête de la PR passe la suite entière
sans identité git ; une demande sans réponse se réécrit, une demande
répondue est figée.

Supposé : que la branche neuve de l'option 1 passe la CI du premier coup ;
je la vérifierai sans identité git avant de la pousser.

## Réponses possibles

- `branche-neuve` — option 1 : je refais la PR sur une branche neuve, sans le commit cassé, et ferme la PR #10.
- `reecrire` — option 2 : je prépare l'historique réécrit, et Théo le pousse de force depuis un terminal.
- `valider` — option 3 : le contrôle admet aussi un correctif qui échoue sur lui-même quand une demande validée le nomme, et la PR passe avec cette demande.
- `fusion-forcee` — option 4 : Théo fusionne en passant outre la CI une fois ; rien ne change dans le socle.
- `refuser` — la PR reste rouge ; rien ne se fusionne sur `main`.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
