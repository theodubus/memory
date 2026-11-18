<!-- socle: couche=decisions zone=publique -->
# ADR-0090 — L'état demande à l'origine les branches qu'elle a encore avant de les donner à l'humain, et dit sa liste du dernier fetch quand elle ne répond pas

> statut : acceptée · date : 2026-11-18 · source : B-0193@310eead1, ADR-0041@1e91c0da · lu : decisions@face0f8a

## Contexte

`branches_a_supprimer`, `branches_contenues_dans_le_travail` et
`branches_inactives` (`engine/socle/human.py`) lisent les références du
dernier fetch. Un fetch sans élagage garde celle d'une branche supprimée
sur l'origine, et l'état la donnait à l'humain, à supprimer ou à
examiner, alors qu'il l'avait déjà supprimée : trois fois entre le 12 et
le 18 novembre (B-0193@310eead1). Deux pistes : élaguer dans un hook qui
va déjà sur l'origine (le démarrage, en session cloud seulement), ou
vérifier au moment de dire.

## Décision

- `a_faire` calcule les trois listes comme avant, puis, s'il y a au
  moins une branche à dire, demande à l'origine celles qu'elle a
  (`git ls-remote --heads origin`, sans invite d'identifiants HTTPS, en
  `DELAI_ORIGINE`, cinq secondes, au plus) et ne garde que celles-là.
- Une branche inactive que l'origine n'a plus, dont la référence, dans
  ce clone, garde seule un commit que la mémoire cite, se dit encore :
  étiqueter ce commit d'abord, sans quoi un `git fetch --prune` le perd.
- Sans réponse de l'origine (délai, erreur, hors ligne), il les garde
  toutes, et chaque ligne dit qu'elle vient du dernier fetch et que
  `git fetch --prune origin` la rafraîchit.
- L'état ne touche pas aux références du clone : il ne les élague pas.
  Rien à dire, rien à demander : l'origine n'est pas interrogée.

## Conséquences

La vérification vaut partout où l'état se calcule, session locale
comprise, et pas seulement au démarrage d'une session cloud ; elle coûte
un aller-retour vers l'origine, seulement quand une branche est à dire,
comme la recherche d'un commit cité dans les pull requests de l'origine
(ADR-0041@1e91c0da). Une branche supprimée sur l'origine pendant la
session disparaît de la liste au calcul suivant.

Pour défaire : retirer de `a_faire` l'appel à `branches_de_l_origine` et
la note du dernier fetch.
