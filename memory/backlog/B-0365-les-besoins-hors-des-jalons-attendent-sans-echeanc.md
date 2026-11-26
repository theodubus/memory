<!-- socle: couche=backlog zone=publique -->
# B-0365 — Les besoins hors des jalons attendent sans échéance : rien ne les place dans une étape ni ne les trie, et la réserve grossit

> statut : ouvert · origine : J-2026-11-26-AD · lu : backlog@0e2e535a · ref : B-0364

Théo, le 26 novembre (J-2026-11-26-AD) : « Les besoins hors
jalons/lots/etapes s'insèrent tout seul dans les étapes du travail
lorsqu'il faudrait les faire ? Ou ça pourrit un peu sur le côté ? »

Ce qui existe : l'état liste au démarrage les besoins à découper ;
l'ordre met d'abord les tâches du prochain jalon, puis les autres par
priorité (`memory.ordre_de`) ; un lot se forme sur tout le backlog ouvert
(skill `socle-batch`). Ce qui manque : rien ne place un besoin hors jalon
dans une étape, ni ne décide quand le faire ; tant qu'un jalon a du
travail, il attend. Chez chess, le 26 novembre, 33 besoins attendaient
après les jalons, dans aucun.

La première piste, trier à la clôture de chaque jalon, ne suffit pas,
Théo le relève (J-2026-11-26-AE) : il ne faut ni que la réserve pourrisse,
ni retrier sans cesse. Un jalon dure des semaines ; un lot, une heure.
La règle soumise, à trois moments :

- à sa naissance, un besoin se range : dans un jalon, ou en réserve avec
  sa raison, sans autre geste que de l'écrire ;
- à la clôture d'un jalon, la réserve se retrie : chaque besoin rejoint
  un jalon à venir, y reste d'une raison, ou est proposé à l'humain pour
  abandon ;
- un besoin en réserve depuis dix lots clos, sans tri depuis, remonte
  « à placer » dans l'état, et se trie à la clôture du lot suivant.

## Satisfait quand

- [ ] aucun besoin n'entre en réserve sans sa raison
- [ ] à la clôture d'un jalon, chaque besoin de la réserve est placé dans un jalon à venir, gardé avec sa raison, ou proposé à l'humain pour abandon
- [ ] un besoin en réserve depuis dix lots clos sans tri est signalé par l'état
