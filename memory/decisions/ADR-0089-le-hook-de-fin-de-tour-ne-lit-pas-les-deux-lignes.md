<!-- socle: couche=decisions zone=publique -->
# ADR-0089 — Le hook de fin de tour ne lit pas les deux lignes du récap dans un bloc de code délimité

> statut : acceptée · date : 2026-11-18 · source : ADR-0007@d1b9c2e7, ADR-0009@f0d60dfd, ADR-0010@3990e4a1, T-0088@972bacbe, D-0127@4d91f8cd, L-0016@76fc494b, J-2026-11-18-P@0c5f6ad8 · lu : decisions@07264857

## Contexte

ADR-0007@d1b9c2e7 et ADR-0009@f0d60dfd font exiger au hook de fin de
tour, quand l'agent a agi, deux lignes dans son dernier message :
« Pour toi : » et « Ensuite : ». `recap_manquant`
(`engine/socle/human.py`) les cherchait dans tout le message, blocs de
code compris. T-0088@972bacbe rend le format compact de `socle roadmap`
sur l'exemple que Théo a validé (D-0127@4d91f8cd), qui finit par une
ligne « Ensuite : » ; le skill `socle-batch` fait coller ce compact au
récap de la clôture d'un lot, et dit de le coller dans un bloc de code
depuis la passe 2 de la revue du lot (T-0091@0708a1ac) : collé en texte, sa ligne
tiendrait encore lieu de celle du récap. La passe 1 de la revue
du lot L-0016@76fc494b l'a relevé (J-2026-11-18-P@0c5f6ad8) : un récap
qui oublie sa propre ligne « Ensuite : » passait, quand il était refusé
avant le lot. Le contrôle des liens, lui, ne lisait déjà pas les blocs
de code, qui montrent des exemples (ADR-0010@3990e4a1).

## Décision

- `recap_manquant` retire du message ses blocs de code délimités avant
  d'y chercher ses lignes : de la clôture ouvrante, trois accents graves
  ou trois tildes au moins en début de ligne, à la clôture fermante, le
  même caractère, au moins aussi long, seul sur sa ligne. Un bloc jamais
  fermé court jusqu'à la fin du message, comme le rend un lecteur
  Markdown.
- Cela vaut pour les deux lignes, et pour les motifs qu'un projet donne
  dans sa politique (`[human] recap_markers`) : le bloc se retire avant
  tout motif.
- Le compact garde sa ligne « Ensuite : », comme l'exemple validé.
- Le refus du hook dit à l'agent d'écrire ses deux lignes en texte, hors
  de tout bloc de code ; le guide aussi.

## Modèle de menace

- **Ce que le contrôle arrête.** La fin du tour d'un agent qui a agi
  sans ses deux lignes, y compris quand une sortie collée dans un bloc de
  code en contient une : le compact de `socle roadmap`, le récap d'une
  session précédente, la sortie d'une commande ou d'un hook.
- **Ce qu'il laisse passer.** Une ligne écrite hors d'un bloc de code
  délimité, même dans une citation (`> Ensuite : …`), même recopiée
  d'une sortie : le contrôle juge qu'une ligne est là, pas d'où elle
  vient ni ce qu'elle dit. De même, un bloc que le contrôle ne tient pas
  pour délimité, ouvert dans une citation (sa clôture précédée de `>`),
  ou indenté de quatre espaces sans clôture : ses lignes comptent. Une sortie collée
  qui contient elle-même une clôture referme le bloc avant sa fin : la
  suite de la sortie se lit en texte.
- **Un message dont le bloc reste ouvert.** Tout ce qui suit sa clôture
  ouvrante est dans le bloc : les deux lignes écrites avant comptent,
  celles écrites après ne comptent pas, et le hook refuse la fin du
  tour une fois, en lui disant d'écrire ses deux lignes en texte, hors
  de tout bloc de code ; l'agent ferme son bloc.
- **Ce qui change pour l'agent.** Il écrit ses deux lignes en texte,
  jamais dans un bloc de code ; une sortie collée dans un bloc ne les
  remplace pas.
- **Pourquoi c'est acceptable.** Le contrôle rattrape l'oubli d'un agent
  coopératif ; il ne prétend pas arrêter un agent qui écrirait, hors d'un
  bloc, une ligne vide de sens. Une ligne recopiée hors d'un bloc se lit
  comme celle de l'agent, et l'humain la lit de même.

## Conséquences

Un agent qui écrivait son récap dans un bloc de code est refusé une fois,
et le réécrit en texte. Le contrôle des liens garde sa propre lecture des
blocs (`memoire.lignes_hors_code`), qui bascule à chaque clôture, quel
qu'en soit le caractère : les deux lectures diffèrent pour un bloc qui
contient une clôture d'un autre caractère ou plus courte, et pour une
clôture suivie d'un texte sur sa ligne ; T-0092@7e2a78c6 les rapproche.

Pour défaire : chercher les motifs dans le message entier, dans
`recap_manquant`, et retirer du refus et du guide la phrase sur les blocs
de code.
