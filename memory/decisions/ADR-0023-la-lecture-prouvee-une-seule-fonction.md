<!-- socle: couche=decisions zone=publique -->
# ADR-0023 — La lecture prouvée, une seule fonction

> statut : acceptée · date : 2026-10-13 · lu : decisions@8e6f1b5f · source : fichier:docs/recul.md

## Contexte

La lecture prouvée (ADR-0008@c8c9e0ec) était la mécanique la plus fragile
du moteur, d'après le relevé de la passe de recul (R4) : quatre correctifs
en trois jours, une fonction de 90 lignes écrite deux fois, dans le
contrôle `memoire.lectures` et dans le hook de l'agent, avec des règles qui
divergeaient, et l'essentiel du temps de la fin de tour. Le relevé y
ajoutait deux défauts : une lecture d'index recopiée d'un sujet plus ancien
du même fichier passait, parce que « déjà citée » se cherchait dans tout le
fichier de la base ; et le verdict dépendait de la base choisie, si bien que
la CI, qui juge depuis la branche par défaut, pouvait refuser ce que le
hook avant push, qui juge depuis le dernier push, avait accepté. Le relevé
proposait d'accepter toute version présente dans la plage. Pour une
entrée, ce serait plus faible que ce que l'auto-test et les tests exigent
déjà : une entrée citée dans la version qu'elle vient de perdre doit être
refusée.

## Décision

- Une seule fonction, `moteur/socle/lectures.py`, que le contrôle et le
  hook appellent, sur la même plage : la base, chaque commit de la plage et
  l'arbre.
- Une citation d'entrée `ID@empreinte` vaut pour la version actuelle de
  l'entrée, ou pour celle du commit où la citation paraît pour la première
  fois : inchangé.
- Une citation d'index `backlog@…` ou `decisions@…` vaut pour toute version
  de l'index dans la plage, sans l'entrée qui cite ni celles du même type
  ajoutées après elle. Elle prouve que l'index a été consulté, pas une
  version de son contenu. Une base plus ancienne ne fait qu'élargir ce qui
  est accepté : la CI accepte tout ce que le hook avant push accepte.
- Une citation déjà là à la base ne se rejuge que si elle change d'entrée :
  « déjà citée » se juge dans la même entrée, ou dans celle dont elle vient
  (un sujet archivé, une entrée basculée en privé) ; hors de toute entrée,
  dans le même fichier.
- La parution d'une citation se cherche par `git log -S`, et la mémoire
  d'une révision se lit en un seul processus git : sur la plage de cette
  branche, le contrôle passe de 21,9 à 4,9 secondes.

## Conséquences

La preuve de lecture d'une entrée garde sa force ; celle d'un index
s'assouplit d'une version lue en cours de route à toute version de la
plage, ce qui lève le refus à tort de la CI. Une lecture recopiée d'une
autre entrée se juge comme une lecture neuve. Pour défaire : rétablir les
deux fonctions d'avant, dans le contrôle et le hook ; les tests de
`tests/test_lectures.py` disent ce que chaque règle garde.
