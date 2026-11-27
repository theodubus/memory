<!-- socle: couche=demandes zone=publique -->
# D-0237 — Alléger la vérification rapide de l'atelier : ses modules de tests les plus longs mis de côté pendant les étapes rapides, que la CI joue toujours

> date : 2026-11-27

## Décision demandée

Pendant la vérification rapide de ce dépôt, mettre de côté ses modules de tests les plus longs, jusqu'à la tenir sous son seuil de 300 secondes, la CI jouant toujours la suite entière.

## Contexte

**Le projet.** Ce dépôt, l'atelier, fabrique le socle : un outil qui permet de confier un projet de code à un agent d'IA sur la durée, avec mémoire, documentation, contrôles et demandes de décision. Le produit, qu'un projet reçoit, est son moteur ; les tests de l'atelier ne le suivent pas.

**Le chantier.** Le jalon en cours met chess à jour puis corrige ce que la mise à jour montre. Chaque lot se pousse plusieurs fois, et chaque push lance d'abord la vérification rapide, `verify --fast`, qui lance ici toute la suite de tests de l'atelier. Le 27 novembre, tu as demandé si son dépassement valait d'être traité, puis de poser cette demande.

**La question.** La vérification rapide dépasse son seuil de 300 secondes : 339 secondes mesurées seule le 27 novembre, 263 à 362 au journal avant, et 574 à 580 quand d'autres travaux chargent la machine, comme trois fois dans cette session. Faut-il en sortir les modules les plus longs ?

Le moteur prévoit déjà ce cas : pendant les étapes rapides, il pose la variable `SOCLE_RAPIDE`, pour qu'un test trop long s'y mette de côté avec sa raison écrite ; la CI, qui lance toutes les étapes sans elle, le joue toujours. Le changement se ferait dans le lanceur de tests de l'atelier, `tests/parallele.py`, qui n'est pas un fichier protégé : il ne lancerait pas, quand la variable est posée, les modules d'une liste écrite, chacun avec sa durée mesurée. Ni l'adaptateur, ni le moteur, ni un test ne changent ; aucun test n'est supprimé.

Le coût d'aujourd'hui : chaque push attend une dizaine de minutes, et un refus de contrôle n'arrive qu'après elles (un push refusé ainsi aujourd'hui). La CI relance de toute façon toute la suite avant chaque fusion : la vérification rapide la double.

## Éléments cités

- D-0236@62fc1597 — ta réponse dans la conversation : poser cette demande.
- B-0258@8f9ad845 — le besoin clos qui a donné à la vérification rapide sa durée affichée et son seuil de 300 secondes.
- F-0014@24da316e — le fait mesuré : sur les projets d'essai, la vérification rapide prend moins d'une seconde ; le dépassement est propre à l'atelier.

## Où regarder

- [tests/parallele.py](https://github.com/theodubus/memory/blob/49b19bbfc6f9b08db79c1b09b9fbc108970e30c6/tests/parallele.py) : le lanceur qui recevrait la liste ; vérifier qu'il lance chaque module dans son processus, avec l'environnement hérité.
- [engine/socle/verification.py](https://github.com/theodubus/memory/blob/49b19bbfc6f9b08db79c1b09b9fbc108970e30c6/engine/socle/verification.py) : vers la ligne 150, `RAPIDE`, la variable et sa règle, qu'un test trop long se met de côté pendant les étapes rapides et que la CI le joue toujours.

## Options

- **A. Mettre de côté les modules les plus longs, par la variable.** Une liste dans le lanceur, chaque module avec sa durée mesurée, choisie pour tenir sous 300 secondes ; le lanceur dit, à chaque passage, combien il en a mis de côté. Effort : une tâche, une trentaine de lignes et leurs tests. Risque : une régression dans un module mis de côté n'est vue qu'à la CI, après le push, jamais après la fusion, que la CI garde. Réversible : la liste se vide.
- **B. Relever le seuil.** Une clé des garde-fous, par une demande de plus. Effort nul ; le push garde son attente, six à dix minutes.
- **C. Ne rien changer.** L'avertissement continue à chaque push ; rien ne bloque.

## Conséquences

- **Si tu valides** : une tâche ouvre la liste et ses tests, dans le prochain lot ; avec les cinq modules les plus longs sortis, la vérification rapide passerait d'environ 340 à environ 220 secondes, seule, le tiers de son attente ; la CI reste inchangée.
- **Si tu refuses** : rien ne change ; l'avertissement reste.
- **Sans réponse** : rien ne change ; le reste du jalon avance sans elle.

## Recommandation

Valider A. Vérifié : la suite seule, 339 secondes au mur sur 4 fils, 1 347 secondes de calcul en 66 modules ; ses cinq plus longs, `test_hooks` 148 s, `test_installeur` 96 s, `test_adaptateurs_multiples` 91 s, `test_adoption` 74 s, `test_attendus` 72 s, 481 secondes à eux cinq ; chargée, 574 à 580 secondes ; la CI de GitHub stable, 9 à 11 minutes, avant et après le dernier lot ; la variable et sa règle dans le moteur. Supposé : le gain au mur, calculé sur ces durées, que la tâche mesurera.

## Réponses possibles

- `valider` — l'option A : les modules les plus longs mis de côté pendant les étapes rapides, la CI jouant tout.
- `refuser` — rien ne change.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
