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

La piste soumise à Théo : à la clôture de chaque jalon, l'agent trie la
réserve, chaque besoin rejoignant une étape à venir, restant en réserve
d'une raison, ou proposé à Théo pour abandon ; la feuille de route dit
depuis quand la réserve attend.

## Satisfait quand

- [ ] à la clôture d'un jalon, chaque besoin hors jalon est placé dans une étape à venir, gardé en réserve avec sa raison, ou proposé à l'humain pour abandon
- [ ] la feuille de route dit depuis quand attend le plus ancien besoin de la réserve
