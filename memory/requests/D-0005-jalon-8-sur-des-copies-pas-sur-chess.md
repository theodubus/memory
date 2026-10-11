<!-- socle: couche=demandes zone=publique -->
# D-0005 — Mener le jalon 8 sur des copies jetables, sans toucher au vrai dépôt chess tant que l'outil n'est pas fini ?

> date : 2026-10-10 · bloque : le jalon 8

## Décision demandée

Faire tout le jalon 8 (l'installeur et ses trois entrées d'initialisation)
sur des copies jetables, sans pull request sur le vrai chess avant que
l'outil soit terminé ; et dire si une copie privée de chess sur GitHub sert,
pour éprouver la CI d'un projet Rust sur un vrai runner.

## Contexte

Tu demandais pourquoi j'avais besoin d'une installation réelle sur chess.
Réponse honnête : je n'en ai pas besoin. Je l'avais proposée parce qu'un
usage réel, sur des semaines, est le meilleur retour qu'on puisse avoir ;
mais c'est l'étape d'après l'outil, pas une étape de sa fabrication.

Ce que demande le jalon 8 du cadrage : un installeur qui pose tout en une
commande, l'initialisation depuis trois entrées (un document de cadrage, rien
du tout, un dépôt existant, ou cadrage et dépôt ensemble), le mode adoption
et la mise à jour. Sa porte : une installation sur un projet existant sans
merge manuel, et une initialisation réussie depuis chacune des entrées.
Rien de cela n'exige le vrai chess. Les portes des jalons 2 et 3 ont déjà
été franchies sur un clone local jetable de chess, jamais poussé : l'audit
passe, et la vérification complète exécute la CI de chess. Le jalon 8 peut
faire de même, sur un clone de chess pour « dépôt existant », un dépôt vide
pour « rien », le cadrage de ce dépôt pour « document ».

Ce qu'une copie locale ne montre pas : la CI d'un projet Rust sur un vrai
runner GitHub (installation de la toolchain, durée, check requis). La CI du
socle a déjà tourné sur GitHub, mais pour un projet Python, celui-ci. Pour
la voir sur du Rust, il faudrait un dépôt GitHub. Un fork public de chess
ne convient pas bien : il est public, ses Actions sont désactivées par
défaut, et une pull request ouverte depuis un fork vise par défaut le dépôt
d'origine, donc le vrai chess. Une copie privée — un dépôt neuf où l'on
pousse le contenu de chess — n'a aucun de ces défauts. Elle n'est utile
qu'une fois, juste avant la vraie installation.

## Éléments cités

- B-0003@dd701305 — le sujet du backlog qui porte le jalon 8 : les trois entrées d'initialisation, les migrations de format et le diff de politique à la mise à jour.
- J-2026-10-10-F@a240a94e — l'entrée du journal où l'audit du socle passe sur un clone local de chess, porte du jalon 2.
- J-2026-10-10-H@905a9075 — l'entrée du journal où la vérification complète exécute la CI de chess sur ce même clone, porte du jalon 3.

## Où regarder

- Le jalon 8 et sa porte : [cadrage, section « Jalons »](../archives/cadrage-2026-10-10.md#jalons), point 8.
- Ce que les copies locales ont déjà permis : [essai du socle sur chess](../../docs/chess/README.md).

Ce qu'il faut vérifier : que la porte du jalon 8 te semble atteignable sans
le vrai chess, et si la vérification de la CI Rust sur GitHub vaut une copie
privée.

## Options

- **Copies locales seulement, vrai chess après la fin de l'outil** : effort
  nul pour toi ; risque faible, la CI Rust sur runner reste non éprouvée
  jusqu'à la vraie installation ; réversible.
- **Copies locales, plus une copie privée de chess juste avant la vraie
  installation** : effort de deux minutes pour toi (créer un dépôt privé
  vide et m'y donner accès) ; risque nul ; réversible, le dépôt se supprime.
- **Installer sur le vrai chess maintenant** : effort de relecture pour toi ;
  risque réel, chess recevrait un outil encore en construction et devrait
  suivre ses changements de format ; réversible, mais au prix d'une pull
  request de retrait.

## Conséquences

Si tu valides, je mène le jalon 8 sur des copies jetables, et je te
redemanderai la copie privée au moment de la vraie installation. Si tu
refuses, dis-moi laquelle des autres options tu préfères. Sans réponse, je
ne touche à aucun dépôt autre que celui-ci : les copies locales ne
demandent l'accord de personne.

## Recommandation

Copies locales seulement, et la copie privée plus tard, juste avant la vraie
installation. Vérifié : les portes des jalons 2 et 3 ont été franchies sur
un clone local, sans rien pousser ; la CI du socle a tourné sur GitHub pour
un projet Python. Supposé : que la CI d'un projet Rust se comporte sur un
runner comme celle de chess aujourd'hui, puisqu'elle en reprend les étapes.

## Réponses possibles

- `valider` — jalon 8 sur des copies locales ; copie privée de chess demandée seulement avant la vraie installation.
- `copie-privee-maintenant` — jalon 8 sur des copies locales, et je crée tout de suite une copie privée pour la CI Rust.
- `refuser` — le texte de ta réponse dit comment tu veux mener le jalon 8.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit.
