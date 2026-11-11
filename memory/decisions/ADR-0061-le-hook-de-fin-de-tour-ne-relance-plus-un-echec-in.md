<!-- socle: couche=decisions zone=publique -->
# ADR-0061 — Le hook de fin de tour ne relance plus un échec inchangé

> statut : acceptée · date : 2026-11-11 · source : B-0143@b34941ca, J-2026-11-09-K@24ab3e43 · lu : decisions@8aebd143

## Contexte

Quand les contrôles de fin de tour échouent, le hook `Stop` bloque la fin
et renvoie leur rapport à l'agent, jusqu'à trois tentatives, puis demande
l'escalade. Sur un échec que l'agent ne peut pas corriger (un fichier
protégé changé par erreur, qu'il n'a pas le droit de remettre), chaque
relance rapportait le même échec sur le même arbre : elle coûtait un appel
de l'agent, qui relit sa conversation, et l'agent y répondait par un récap
entier, puisque sa réponse est une fin de tour (J-2026-11-09-K@24ab3e43).

## Décision

1. Le hook retient, avec le compte des tentatives de la session, la
   signature de l'échec : l'empreinte de l'arbre et les noms des
   contrôles en échec, sans le texte de leurs erreurs. Pour une étape de
   l'adaptateur, ce texte est la fin de la sortie de l'outil, avec une
   durée (« Ran N tests in X.XXXs ») : il change à chaque relance sur un
   test rouge, le cas le plus courant, et ferait de chaque relance un
   échec nouveau (revue du lot).
2. Le premier arrêt d'un tour bloque toujours : l'agent a sa chance de
   corriger. Une relance que le hook a lui-même provoquée
   (`stop_hook_active`) sur la même signature ne bloque plus : le hook
   imprime le rapport en message à l'humain (« sans changement depuis la
   tentative précédente »), et la relance ne compte pas comme une
   tentative. Le premier arrêt du tour suivant bloque de nouveau, et
   l'escalade au troisième échec tient.
3. Le message du refus dit à l'agent qui ne peut pas corriger de répondre
   en une ligne qui dit pourquoi, sans redire son récap.

## Conséquences

Un tour qui ne peut rien corriger coûte une relance au lieu de deux ou
trois, et une réponse d'une ligne. Aucune protection ne tombe : un tour
finissait déjà rouge après l'escalade, avec le rapport en message à
l'humain ; ici il finit rouge plus tôt par le même chemin, seulement quand
la relance n'a rien changé. Le hook avant commit, le hook avant push et la
CI jugent toujours tout. Le défaire : retirer la branche
`stop_hook_active` de `hooks.stop` ; la signature dans le compteur est
alors ignorée.
