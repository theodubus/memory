<!-- socle: couche=demandes zone=publique -->
# D-0130 — Changer la commande de tests de l'adaptateur pour le lanceur parallèle, et valider la spécification de la durée des étapes rapides et de son seuil (lot L-0012)

> date : 2026-11-17

## Décision demandée

Deux points, à valider ensemble ou séparément : changer vous-même une
ligne de l'adaptateur pour que les tests du dépôt tournent sur tous les
cœurs, et valider la spécification ci-dessous avant que l'agent n'en
écrive le code.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA comme Claude Code : il
garde la mémoire du projet, vérifie ce que l'agent produit, et vous pose en
« demandes », comme celle-ci, les décisions qui vous reviennent. Chess,
votre jeu d'échecs, est le projet pilote qui l'utilise.

**Le chantier.** Avant toute nouvelle fonction, l'agent termine une suite
de lots, chacun un groupe de tâches menées puis relues ensemble. Le lot de
la structure du backlog a été livré le 17 novembre. Le lot présent, que
vous avez placé juste après le 16 novembre, raccourcit la vérification
rapide, `verify --fast` : la commande qui lance les contrôles et les tests
du dépôt à la fin de chaque tour de l'agent et avant chaque envoi. Elle
prenait 143 secondes le 13 octobre, sur une autre machine ; elle en prend
aujourd'hui près de onze minutes, sans que rien ne l'ait signalé. Chaque
lot en paie le prix : chaque envoi attend autant, et un sous-agent qui
attend plus de cinq minutes relit tout son contexte au prix fort.

**La question.** Les deux remèdes vous reviennent. Le premier lance les
tests sur tous les cœurs de la machine au lieu d'un seul ; sa commande est
dans l'adaptateur du dépôt (`.socle/adapter.toml`, le fichier qui dit au
socle comment compiler et tester le code), un fichier protégé que l'agent
ne peut pas écrire. Le second fait dire au socle la durée de chaque étape,
et avertir au-delà d'un seuil : sa conception n'est pas tranchée, et se
valide avant son code.

**Ce qui est mesuré.** Dans le conteneur de cette session (4 cœurs), le
17 novembre : `verify --fast --redo` (tout relancé) prend 650,9 s ; les
tests seuls, lancés l'un après l'autre, 648,7 s. Un lanceur écrit pour ce
lot, `tests/parallele.py`, lance chaque fichier de tests dans son propre
processus, quatre à la fois : 176, 175 et 174 s au mur, trois fois de
suite, les mêmes 1 172 tests verts. Après le changement, la vérification
devrait prendre environ 180 s ; c'est déduit, pas encore mesuré.

**Le premier point : la ligne de l'adaptateur.** Dans la section
`[capabilities.tests]`, la ligne
`command = "python3 -m unittest discover -s tests -t . -q"` devient
`command = "python3 tests/parallele.py"`, rien d'autre. Le geste, si vous
validez : sur GitHub, ouvrir `.socle/adapter.toml` sur la branche
`claude/socle-l0012-passation-xw9g3i`, remplacer cette ligne, et commiter
sur la branche. L'empreinte citée plus bas est celle du fichier ainsi changé ;
votre réponse, consignée par l'agent, couvre ce changement auprès du
contrôle des fichiers protégés. Dans un terminal, le même changement se
fait à la main, suivi de `python3 .socle/socle approve --text "<raison>"`.

**Le second point : la spécification de la durée des étapes.**

1. Chaque vérification qui lance une étape de l'adaptateur (`verify`,
   `verify --fast`, et la CI) imprime sa durée au mur, en secondes, au
   bout de sa ligne, puis le total des étapes lancées. Des étapes rapides
   déjà passées sur le même contenu, que la vérification ne relance pas,
   le disent sans durée.
2. Un seuil, la clé `[verify] fast_max_seconds` des garde-fous du projet
   (`.socle/guardrails.toml`, le fichier de ses limites), porte sur le
   total des étapes rapides, quand `verify --fast` les a toutes lancées.
   Le gabarit d'un projet neuf le pose à 300 secondes ; un projet qui ne
   l'écrit pas reçoit la même valeur.
3. Au-delà du seuil, un avertissement, jamais un échec : il donne le
   total, le seuil, et l'étape la plus longue avec sa durée. La
   vérification passe ; la fin de tour et l'envoi le montrent comme les
   autres avertissements.
4. Relever le seuil l'assouplit : comme pour un budget de taille, cela
   exige une demande que vous validez ; le baisser est libre. La durée
   mesurée, elle, ne se compare pas d'une fois à l'autre : elle dépend de
   la machine.
5. En CI, les durées s'impriment, sans seuil : la CI lance toutes les
   étapes, sur une autre machine.
6. Le contrôle a son défaut injecté (une étape lente sous un seuil d'une
   seconde) et un cas sain dans l'auto-test du socle ; le guide et une
   note de version le disent aux projets qui le reçoivent.

## Éléments cités

- L-0012@43dd66c3 — le lot présent, la durée de la vérification, que vous avez placé le 16 novembre.
- B-0257@4a64e0f3 — le besoin de lancer la suite de tests sur plusieurs cœurs, avec les mesures du 15 novembre.
- T-0044@8d037e37 — sa tâche : la durée relevée avant et après, la suite parallèle verte trois fois, moins de cinq minutes.
- B-0258@0b668def — le besoin que la durée des étapes se dise et ait un seuil, dont la conception restait à trancher.
- T-0045@2be8b0ed — sa tâche : la durée de chaque étape imprimée, et l'avertissement d'un seuil dépassé.
- J-2026-11-17-I@47fe7455 — l'entrée du journal qui consigne le lanceur et ses mesures.
- ADR-0001@692e0dfc — la décision qui borne le moteur à la bibliothèque standard de Python, que le lanceur respecte.
- .socle/adapter.toml sha256:5dffd22cd3ada2b2

## Où regarder

- [tests/parallele.py](https://github.com/theodubus/memory/blob/fe4789942aeb24df67ef04d9a55925cd686eb1e5/tests/parallele.py) : le lanceur, 137 lignes ; vérifier qu'il ne fait que lancer chaque fichier de tests et en rendre le bilan.
- [Le journal du 17 novembre](https://github.com/theodubus/memory/blob/fe4789942aeb24df67ef04d9a55925cd686eb1e5/memory/journal/2026-11-6.md) : l'entrée J-2026-11-17-I, les mesures et la nature de chacune.
- [B-0258](https://github.com/theodubus/memory/blob/fe4789942aeb24df67ef04d9a55925cd686eb1e5/memory/backlog/B-0258-la-duree-des-etapes-rapides-se-dit-et-a-un-seuil-v.md) : le besoin du second point, et ce qu'il laissait à trancher.

## Options

- **Les deux points.** Effort : une ligne pour vous, puis environ une
  demi-journée de lot pour l'agent. Risque : faible ; le lanceur est
  testé, et le seuil ne fait qu'avertir. Réversible : la ligne se remet,
  le seuil se règle.
- **Le premier seul.** Effort : une ligne pour vous. Risque : la durée
  reste muette, une nouvelle dérive ne se verrait pas. Réversible :
  l'agent réécrit la spécification selon votre remarque.
- **Le second seul.** Effort : le lot de l'agent seul. Risque : la
  vérification reste à onze minutes, et l'avertissement le dira à chaque
  fin de tour. Réversible : la ligne peut changer plus tard.
- **Aucun.** Effort : nul. Risque : chaque lot continue de payer onze
  minutes par vérification. Réversible : les deux tâches restent
  ouvertes.

## Conséquences

- Si vous validez : après votre commit, l'agent relève la durée de
  `verify --fast --redo`, attend trois CI vertes, puis implémente la
  spécification, la fait relire et livre le lot.
- Si vous refusez : l'adaptateur garde sa commande, et l'agent reprend les
  deux tâches selon votre réponse.
- Sans réponse : le lot attend ; l'agent ne touche à rien d'autre de ce
  lot, et la vérification reste à onze minutes.

## Recommandation

Valider les deux points. Vérifié : les durées ci-dessus, mesurées une
fois pour la suite séquentielle et trois fois pour la suite parallèle,
tous les tests verts à chaque fois ; les neuf tests du lanceur. Supposé :
la durée d'environ 180 s après le changement, déduite de deux relevés ;
le gain en CI, que la machine de GitHub fixera ; qu'un seuil de 300 s
convienne aux autres projets, sans mesure faite chez eux.

## Réponses possibles

- `valider` — vous changez la ligne de l'adaptateur, et la spécification est validée telle quelle.
- `adaptateur-seul` — vous changez la ligne ; la spécification revient à l'agent avec votre remarque.
- `specification-seule` — l'adaptateur garde sa commande ; la spécification est validée.
- `refuser` — ni l'un ni l'autre ; l'agent reprend les deux tâches selon votre remarque.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
