<!-- socle: couche=backlog zone=publique -->
# B-0257 — La suite de tests de ce dépôt sur plusieurs cœurs : verify --fast passe près de douze minutes sur un seul cœur

> statut : ouvert · origine : J-2026-11-16-E · lu : backlog@998104b7

Un sujet de l'atelier, d'une analyse en lecture seule du 15 novembre sur
d1d296e, que Théo a fait inscrire (J-2026-11-16-E) ; il n'en fixe ni la
priorité ni le lot. Ce qui suit garde la nature de chaque constat.

Le constat, commun avec B-0258 :

- Mesuré, une fois, dans un conteneur de session cloud à 4 cœurs (Python
  3.13) : `python3 .socle/socle verify --fast --redo` passe en 11 min
  49 s, dont 11 min 31 de CPU. Un seul cœur sert : l'étape des tests,
  `python3 -m unittest discover -s tests -t . -q`, lance les 51 fichiers
  l'un après l'autre.
- Mesuré, une fois, même conteneur : chaque fichier de `tests/` lancé dans
  son propre processus (`python3 -m unittest tests.<module> -q`), quatre à
  la fois, avec `SOCLE_RAPIDE=1` et `LC_ALL=C.UTF-8` : 185 s au mur, 720 s
  en somme, 51 fichiers, aucun échec, arbre intact. Les plus longs :
  test_hooks 84 s, test_adaptateurs_multiples 48 s, test_attendus 47 s,
  test_adoption 46 s, test_demarrage 44 s, test_installeur 43 s.
- Écrit dans `docs/fabrication/recul.md` : la suite rapide prenait 143 s
  le 13 octobre. Les deux relevés viennent de deux machines différentes.
- Déduit, non mesuré : `docs/fabrication/consommation.md` dit qu'un
  sous-agent écrit son cache pour cinq minutes, et qu'un appel après plus
  de cinq minutes de silence réécrit tout son contexte (19 fois l'appel
  médian, plus du quart du coût des sous-agents). Le skill
  `.claude/skills/delegate-lot/SKILL.md` fait lancer `verify --fast` à
  chaque sous-agent, une fois, à la fin : une vérification de plus de
  cinq minutes provoquerait cette réécriture à chaque sous-agent.
- Vérifié : `verify --fast` n'imprime aucune durée ; aucun sujet ouvert ne
  portait sur la durée des étapes rapides.

Mesuré aussi dans la session du 15 et 16 novembre (J-2026-11-16-A) :
chaque push de la branche de travail, dont le hook avant envoi lance
`verify --fast`, a duré plus de dix minutes, et un implémenteur a vu la
suite entière (`unittest discover`) prendre 931 s.

Quoi : la commande de tests de l'adaptateur de ce dépôt lance chaque
fichier de tests dans son processus, autant à la fois que de cœurs, par
un lanceur en bibliothèque standard seule (ADR-0001). `.socle/adapter.toml`
est protégé : son changement passe par une demande à Théo.

À vérifier avant de changer quoi que ce soit : la durée de `verify --fast
--redo` dans une session de travail ; qu'aucun fichier de tests n'en gêne
un autre (un seul passage ne le prouve pas) ; qu'en CI, où l'auto-test
tourne déjà sur quatre fils, le cumul ne ralentit rien.

## Fait quand

- [ ] la durée de `verify --fast --redo` est relevée dans une session de travail, avant et après
- [ ] la suite lancée en parallèle passe trois fois de suite, en local et en CI
- [ ] après le changement, `verify --fast --redo` prend moins de cinq minutes dans une session de travail
