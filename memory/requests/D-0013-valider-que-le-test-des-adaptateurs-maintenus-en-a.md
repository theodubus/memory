<!-- socle: couche=demandes zone=publique -->
# D-0013 — Valider que le test des adaptateurs maintenus en attende huit au lieu de trois

> date : 2026-10-11 · lu : decisions@7945802c · bloque : le commit des cinq adaptateurs nouveaux

## Décision demandée

Autoriser que le test qui fige la liste des adaptateurs maintenus attende
désormais huit adaptateurs (les trois actuels, plus JavaScript et
TypeScript, Go, Java, Ruby et PHP) au lieu de trois.

## Contexte

Tu m'as donné le feu vert pour proposer des adaptateurs pour d'autres
langages courants que Rust et Python. J'en ai écrit cinq, chacun avec son
outil de tests et son outil de mutation : JavaScript et TypeScript (vitest,
Stryker), Go (go test, gremlins), Java (Maven, JUnit 5, PIT), Ruby (RSpec,
mutant) et PHP (PHPUnit, Infection). Les cinq outils de mutation ont tourné
ici sur un petit projet par langage, et le moteur lit leurs rapports avec
les mêmes comptes que ceux que chaque outil affiche. Toute la suite des
tests du moteur passe, sauf un test : celui qui vérifie qu'il existe
exactement trois adaptateurs maintenus. Ajouter des adaptateurs change
forcément sa valeur attendue. Depuis ta décision sur le point 2 de la
politique, je ne peux pas changer seul une valeur attendue : il me faut une
demande validée qui nomme le test. Rien d'autre n'est affaibli : aucun test
n'est supprimé, aucune autre assertion ne change.

## Éléments cités

- **Le sujet des adaptateurs** : le sujet de backlog que tu as ouvert pour
  proposer plus que des adaptateurs Rust et Python.
- **Le test concerné**, `test_les_trois_adaptateurs`, dans le fichier des
  tests des adaptateurs : il compare la liste des adaptateurs maintenus à
  `python`, `python-pytest`, `rust`. Après le changement, il la comparera à
  `go`, `java`, `javascript`, `php`, `python`, `python-pytest`, `ruby`,
  `rust`, et prendra un nom qui ne dit plus « trois ».
- **Le point 2 de la politique, tel que tu l'as tranché** : une valeur
  attendue ne change que sur une demande validée qui nomme le test, ou sur
  une spécification que toi seul as écrite.

## Où regarder

- [le test, dans sa version actuelle](https://github.com/theodubus/memory/blob/18a133a1457e7622ccba849f48d6c0dbfb253008/tests/test_adaptateurs.py) :
  vérifier que la première méthode fige la liste des trois adaptateurs.
- [le sujet des adaptateurs](https://github.com/theodubus/memory/blob/18a133a1457e7622ccba849f48d6c0dbfb253008/memory/backlog.md#b-0030--des-adaptateurs-pour-dautres-langages-courants) :
  vérifier que les cinq langages sont ceux que tu voulais.
- [la décision sur le point 2](https://github.com/theodubus/memory/blob/18a133a1457e7622ccba849f48d6c0dbfb253008/memory/decisions/ADR-0017-une-valeur-attendue-ne-change-que-sur-une-specific.md) :
  vérifier que c'est ce cas qu'elle couvre.

## Options

- **Valider** : le test attend les huit adaptateurs, et les cinq nouveaux se
  commitent. Effort nul de ton côté ; risque faible, puisque seule la liste
  attendue s'allonge ; réversible en retirant les adaptateurs.
- **Refuser** : les cinq adaptateurs ne se commitent pas comme adaptateurs
  maintenus. Effort : je les sortirais du dossier des adaptateurs maintenus,
  en exemples à copier, ce qui les rend moins faciles à installer ; risque
  nul ; réversible.

## Conséquences

- Si tu valides : je consigne ta réponse, je commite les cinq adaptateurs
  avec leurs lecteurs de mutation, leurs tests et le banc qui les éprouve,
  puis je pousse.
- Si tu refuses : les adaptateurs restent non commités, et je te propose de
  les livrer en exemples hors de la liste maintenue.
- Sans réponse : le travail attend, non commité ; je continue de les éprouver
  sur des projets jetables, ce qui n'en dépend pas.

## Recommandation

Valider. Vérifié : toute la suite des tests passe avec ce seul changement,
et les cinq outils de mutation ont tourné ici, chacun lu avec les comptes
qu'il affiche. Supposé : les étapes de CI que chaque adaptateur ajoute au
workflow (installation de Node, Go, Java, Ruby ou PHP) marchent sur GitHub ;
elles n'ont tourné qu'ici.

## Réponses possibles

- `valider` — le test attend les huit adaptateurs ; les cinq nouveaux se commitent et se poussent.
- `refuser` — les adaptateurs restent hors de la liste maintenue ; je propose de les livrer en exemples.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
