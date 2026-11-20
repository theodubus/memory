<!-- socle: couche=decisions zone=publique -->
# ADR-0101 — Le seuil d'un lot qui ne se mène pas en une session : neuf tâches encore attendues, mesuré sur les lots faits, dans [batches] max_tasks

> statut : acceptée · date : 2026-11-20 · source : B-0233@9e29a147, T-0012@045512f0, ADR-0079@d9cd58c2, D-0118@c6376e4c, D-0134@a3f8bf61, J-2026-11-20-S@9192eeb9 · lu : decisions@103da660

## Contexte

B-0233@9e29a147 : un jalon né lot a réuni 22 sujets avant que Théo ne le
lise comme « prochain lot » (D-0118@c6376e4c). La règle qui forme un lot
(ADR-0079@d9cd58c2, point 4) existe, mais rien ne montre qu'un lot la
tord. T-0012@045512f0 fait avertir l'état et le rappel de fin de tour
au-delà d'un seuil mesuré sur les lots faits.

La mesure est au journal (J-2026-11-20-S@9192eeb9) : les quatorze lots
clos, leurs tâches dans `après`, et leurs sessions, comptées sur les
entrées de leur ouverture, de leurs passations, de leurs reprises en
session neuve et de leur clôture. Deux enseignements. Le nombre de
sessions d'un petit lot suit ses passes de revue plus que ses tâches :
L-0004@10c94b27 et L-0012@519fa7dd, deux tâches, en ont pris trois. Et
aucun lot n'a mené plus de neuf tâches : neuf est le plus grand nombre
qu'une session ait mené (L-0018@372bba8b, depuis les allégements de
D-0134@a3f8bf61, en 71 % d'une fenêtre de cinq heures), et les lots de
sept tâches et plus, sauf lui, en ont pris plusieurs (L-0014@cd0d35b8,
sept tâches, trois sessions).

## Décision

1. **Le seuil est de neuf tâches encore attendues** : au-delà, l'état
   (avec ce qui demande d'agir, sur une ligne qui nomme chaque lot et son
   compte) et le rappel de fin de tour (sous l'ordre du backlog)
   avertissent qu'un lot ouvert ne se mène pas en une session, et disent
   de le couper en lots, ou d'en faire un jalon et de former ses lots
   dessous. Au seuil et en dessous, rien. Un avertissement, jamais un
   échec : un lot formé au-delà reste permis.
2. **Se comptent les tâches que le lot attend encore** : ouvertes, en
   cours ou bloquées ; ni les closes, ni le lot d'avant, ni une demande.
   Un lot en cours se juge sur ce qui lui reste à mener.
3. **Le seuil se règle** dans `[batches] max_tasks` des garde-fous, neuf
   par défaut : ce qu'une session mène dépend de l'agent et de son
   modèle, que le moteur ne connaît pas. Le cliquet le juge comme
   `[verify] fast_max_seconds` : baisser est libre, relever exige une
   demande validée, `nan` se lit zéro.
4. **Seul le nombre se juge** : l'état ne sait pas quels fichiers
   touchera une tâche pas encore faite ; aucun champ ne le dit, et son
   texte ne le prouve pas. Que les tâches d'un lot partagent des
   fichiers, un garde-fou ou des tests reste le jugement de l'agent qui
   le forme (ADR-0079, point 4), que le skill `socle-batch` dit
   (T-0073@ef810408).

## Conséquences

À la livraison, l'état avertit pour L-0006@7bbb0f14 (douze tâches encore
attendues sur dix-neuf), L-0007@73cf3af3, L-0008@a6ecb00f et
L-0010@a5e8d844 (dix chacun), formés avant la mesure ; les couper revient
à leur prochaine annonce. Le seuil se remesure quand des lots nouveaux le
contredisent : un lot de plus de neuf tâches mené en une session le
relève, par une demande. Le défaire : retirer `memoire.lots_trop_longs`
de l'état et du rappel, et la clé des gabarits.
