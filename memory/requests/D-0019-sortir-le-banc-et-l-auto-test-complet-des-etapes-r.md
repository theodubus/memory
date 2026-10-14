<!-- socle: couche=demandes zone=publique -->
# D-0019 — Sortir le banc et l'auto-test complet des étapes rapides de ce dépôt

> date : 2026-10-13

## Décision demandée

Faire tourner le banc et l'auto-test complet de ce dépôt en CI seulement,
et plus à chaque fin de tour, à chaque vérification que l'agent lance et à
chaque push.

## Contexte

Ce dépôt vérifie, à la fin de chaque tour où du code a changé, avant chaque
push et quand l'agent lance `verify --rapide`, ses « étapes rapides » : sa
suite de tests entière. C'est son adaptateur qui le dit, un fichier
protégé que seul toi modifies. Mesuré le 13 octobre : la suite prend
260 secondes, dont 102 pour le banc (des sessions d'agent simulées sur de
petits projets) et 35 pour le test qui joue l'auto-test complet (chaque
défaut injecté, un par un) ; sans ces deux-là, 124 secondes. La CI les
jouerait toujours, à chaque push. J'ai déjà fait ce qui ne touchait que le
moteur : une vérification réussie ne se refait plus sur un arbre identique,
l'auto-test tourne sur quatre fils (de 76 à 33 secondes) et une seule fois
en CI ; la suite est passée de 370 à 260 secondes. Le reste change ce que
la fin de tour de ce dépôt vérifie : la décision est la tienne. C'est le
lot L6 de la passe de recul, dans l'ordre que tu as validé.

## Éléments cités

- **Le chantier des lots de la passe de recul** (B-0044@868ee9c8) : L6, la
  fin de tour, devait passer par une demande parce qu'il touche
  l'adaptateur protégé de ce dépôt.
- **Les mesures et la part déjà faite** (J-2026-10-13-O@3d4f59c9) : la
  vérification mémorisée, l'auto-test parallèle, les temps avant et après.
- **Le banc** : les tests de `tests/test_banc.py`, qui jouent les scénarios
  d'évaluation sur un agent simulé.
- **L'auto-test complet** : le test de `tests/test_autotest.py` qui injecte
  chaque défaut et vérifie qu'il est attrapé ; ses autres tests, rapides,
  resteraient.

## Où regarder

- [l'adaptateur de ce dépôt](https://github.com/theodubus/memory/blob/cd6436ac4eb2d0f480e1290599fabeded8ca122d/.socle/adapter.toml) : la section
  `[capabilities.tests]`, `fast = true`, qui met la suite entière dans les
  étapes rapides.
- [le relevé de la passe de recul](https://github.com/theodubus/memory/blob/cd6436ac4eb2d0f480e1290599fabeded8ca122d/docs/recul.md#h-performance) :
  la section H et la proposition R5, qui proposaient ce changement.
- [le journal](https://github.com/theodubus/memory/blob/cd6436ac4eb2d0f480e1290599fabeded8ca122d/memory/journal/2026-10-2.md#L734) : l'entrée
  J-2026-10-13-O, les mesures.
- [le banc](https://github.com/theodubus/memory/blob/cd6436ac4eb2d0f480e1290599fabeded8ca122d/tests/test_banc.py) et [l'auto-test](https://github.com/theodubus/memory/blob/cd6436ac4eb2d0f480e1290599fabeded8ca122d/tests/test_autotest.py) :
  ce qui sortirait des étapes rapides.

## Options

- **Une convention du moteur** : il pose une variable d'environnement
  (`SOCLE_RAPIDE`) pendant les étapes rapides ; le banc et l'auto-test
  complet de ce dépôt se mettent de côté quand elle est posée, avec leur
  raison écrite ; la CI les joue toujours. Je l'écris, sans toucher à
  l'adaptateur. Effort faible ; risque : une régression du banc ou de
  l'auto-test ne se voit qu'en CI ; la fin de tour passe de 260 à environ
  124 secondes de tests ; réversible en retirant les deux lignes.
- **Tu modifies l'adaptateur** : une commande de tests rapide qui exclut
  ces deux modules, et une étape lente pour la CI. Même effet ; effort
  moyen, à faire par toi ; risque : le même, et la liste des modules exclus
  vit dans un fichier protégé, à tenir à jour par toi ; réversible.
- **Rien** : 260 secondes à chaque fin de tour qui touche du code. Effort
  nul ; risque : aucun sur les contrôles, une boucle de travail lente ;
  réversible.

## Conséquences

- Si tu valides la convention : je l'écris, avec ses tests ; une
  régression du banc ou de l'auto-test ne se voit plus qu'en CI, une
  quarantaine de minutes après le push, au lieu de la fin du tour.
- Si tu préfères modifier l'adaptateur : je te donne les lignes exactes, et
  tu les commites.
- Si tu refuses, ou sans réponse : rien ne change ; je passe à R2.

## Recommandation

La convention du moteur. Vérifié : les temps mesurés ci-dessus, et que la
CI joue la suite entière à chaque push. Supposé : que le banc et
l'auto-test complet attrapent peu de choses qu'une fin de tour aurait
arrêtées plus tôt ; que les tests qui restent rapides
voient la plupart des régressions du moteur ; non mesuré.

## Réponses possibles

- `convention` — j'écris la convention du moteur et les deux mises de côté.
- `adaptateur` — tu modifies l'adaptateur toi-même, avec les lignes que je te donne.
- `rien` — rien ne change.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
