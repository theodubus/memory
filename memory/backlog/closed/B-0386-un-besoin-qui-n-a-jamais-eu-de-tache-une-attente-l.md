<!-- socle: couche=backlog zone=publique -->
# B-0386 — Un besoin qui n'a jamais eu de tâche, une attente levée ou un besoin pour l'humain, ne se clôt pas « fait » ; l'état dit « à fermer » un besoin qu'une case vide empêche de clore

> statut : fait · origine : J-2026-11-28-A · ref : ADR-0083, ADR-0117, ce commit · lu : backlog@6bf9de12

La gêne 1 du retour de chess sur sa mise à jour du 28 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-28.md`). Le produit fait
naître deux sortes de besoins sans tâche : l'attente, rangée en besoin
`bloqué` qui « se lève en se fermant » (le skill `socle-request`, note
`2026-11-27-i`), et le besoin `pour : humain`, que « l'agent ferme sur sa
parole », sans tâche (`engine/socle/FORMAT.md`, note `2026-11-26-j`).
Le contrôle `memoire.formes` refuse pourtant tout besoin « fait » sans
tâche faite, la règle de la spécification du backlog validée le
16 novembre (ADR-0083) : « un besoin se ferme quand ses tâches sont
closes, l'une au moins faite ; sinon il s'abandonne ».

Les constats :

- chez chess, B-0084, une attente débloquée puis faite, ses deux cases
  cochées : `socle close B-0084` refuse ; la clôture a coûté quatre
  gestes, dont une tâche écrite après coup. B-0083 attend le même sort ;
- ici, le 28 novembre, sur le projet d'essai des tests : un besoin
  `pour : humain`, ses cases cochées, sans tâche, `socle close` le
  refuse du même message ;
- ici, l'état dit « besoins à fermer, leurs tâches closes : B-0383,
  B-0385 », dont une case reste vide : `socle close` les refuserait.

La conception se tranche avec Théo, sa question d'intention posée dans
la conversation (J-2026-11-28-A), avant la spécification et le code.

## Modèle de menace

Ce que `memoire.formes` arrête, avec `memoire.backlog` : un besoin dit
« fait » sans rien qui dise ce qu'il satisfait. Il a eu des tâches, et
aucune n'est faite : elles sont toutes abandonnées, il n'a rien livré, il
s'abandonne. Il n'en a jamais eu, et sa section « Satisfait quand » n'a
aucune case. Il a une case vide, tâche faite ou non.

Ce qu'il laisse passer : un besoin sans tâche, ses cases cochées. L'agent
y coche ce qu'il constate, comme dans une tâche ; aucun contrôle ne juge
la vérité d'une case, ni avant ce besoin ni après. Avant, une tâche écrite
après coup, cochée, fermait déjà le même besoin : la règle n'ouvre aucune
voie qui n'existait pas. Cocher une case fausse est hors du modèle.

## Satisfait quand

- [x] une attente levée et un besoin pour l'humain, sans tâche et leurs cases cochées, se closent par `socle close`, en un geste
- [x] l'état ne dit « à fermer » qu'un besoin que `socle close` accepterait
