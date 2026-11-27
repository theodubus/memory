<!-- socle: couche=decisions zone=publique -->
# ADR-0118 — Un besoin naît rangé, dans un jalon ou en réserve avec sa raison ; la réserve se retrie à la clôture d'un jalon, et l'état signale le besoin sans tri depuis quinze lots clos

> statut : acceptée · date : 2026-11-27 · source : B-0365@74052016, D-0213@8efe48de, D-0235@2eec26f8 · lu : decisions@2e0f342b

## Contexte

Les besoins d'aucun jalon attendent sans échéance : chez chess, 33 le
26 novembre (B-0365@74052016). Théo a validé une règle en trois moments
(D-0213@8efe48de) : un besoin se range à sa naissance, dans un jalon ou en
réserve avec sa raison ; la réserve se retrie entière à la clôture d'un
jalon ; un besoin en réserve sans tri depuis quinze lots clos est signalé
par l'état, et le compte repart à chaque tri. Il l'a gardée sous une
condition (D-0235@2eec26f8, point 8) : ni appel ni refus de plus. La raison
se donne donc à la création, le contrôle ne fait que rattraper un oubli,
et le signal se calcule. Les tâches T-0220@9f06815a et T-0221@24571269 la
mettent en œuvre, sur le mécanisme de clôture de l'ADR-0117@287f443f.

## Décision

- **La réserve.** Un besoin ouvert qu'aucun jalon ouvert ne nomme dans
  son `après` est en réserve : une seule définition, dans le moteur, que
  la feuille de route, l'état et le contrôle lisent. Un besoin `pour :
  humain` ne se trie pas : « Pour toi » le montre, l'humain le mène
  (B-0363@8c80df98).
- **Deux champs** sur la ligne de métadonnées d'un besoin :
  `réserve : <raison>` (`reserve`), pourquoi il attend hors des jalons, et
  `trié : L-NNNN` (`sorted`), le plus haut identifiant de lot du backlog,
  ouvert ou clos, archivé compris, de la zone du besoin, au moment du tri.
  Récrire `trié`, c'est trier : le compte repart.
- **À sa naissance.** `socle new need "…" --milestone JA-NNNN` ajoute le
  besoin à la fin de l'`après` du jalon, le champ créé s'il manque ; un
  jalon inconnu ou clos, ou public pour un besoin privé, fait refuser la
  commande avant toute écriture. `--reserve "<raison>"` écrit les deux
  champs. Les deux s'excluent ; `--task` reste tel quel. Sans l'un ni
  l'autre, quand le projet a un jalon ouvert, une ligne dit comment le
  ranger, sans refus.
- **Le contrôle `memoire.reserve`**, contre la base, quand la tête a un
  jalon ouvert : il refuse un besoin ouvert, nouveau dans la plage
  (renumérotation et copie privée d'une entrée basculée exclues) ou sorti
  d'un jalon ouvert à la base, qu'aucun jalon ouvert n'attend et sans
  raison ; son message donne les deux façons de le ranger, et le `trié` à
  écrire. Un besoin d'avant sans raison ne se refuse pas : il se signale.
- **Le signal.** Un besoin de la réserve est « à placer », quand la tête a
  un jalon ouvert, s'il n'a pas de raison, ou si quinze lots clos ou plus
  ont un numéro supérieur à son `trié` (sans `trié`, tous les lots clos de
  sa zone comptent). Une ligne de l'état les nomme, bornée, avec le `trié`
  à écrire ; la ligne « En réserve » de la feuille de route dit combien.
  Il se trie à la clôture du lot suivant.
- **La clôture d'un jalon.** Un jalon ouvert à la base et clos à la tête
  est refusé, sur son fichier, tant qu'un besoin de la réserve n'a pas sa
  raison et un `trié` au moins égal au plus haut identifiant de lot de la
  base ; `socle close JA-NNNN` le refuse avec lui (ADR-0117). Un besoin
  proposé à l'abandon reste en réserve, sa raison nommant la demande.

## Modèle de menace

Ce que la règle doit arrêter : un besoin qui entre en réserve sans
raison, un jalon clos sur une réserve que personne n'a relue, et une
réserve qu'aucun moment ne relit.

- Une raison vide de sens (« à voir ») passe : le contrôle juge sa
  présence, non sa qualité, que la revue et l'humain lisent au tri du
  jalon. Accepté.
- `trié` récrit sans trier, pour taire le signal ou passer la clôture : le
  diff le montre, comme toute ligne de métadonnées. Accepté : la règle rend
  le tri peu coûteux, elle n'en prouve pas le jugement.
- `trié` vers un lot qui n'existe pas : le contrôle des références refuse
  un identifiant qui ne désigne aucune entrée.
- Un besoin retiré d'un jalon, dans un commit puis dans un autre : sorti
  d'un jalon ouvert à la base, il est jugé jusqu'à la fusion. Passé d'un
  jalon à un autre, il reste attendu, et passe.
- Un jalon abandonné plutôt que fait : « clos » couvre les deux.
- La base, et non la tête : un lot clos sur la branche après le jalon
  ferait refuser le commit suivant par la CI, un refus de plus. En retour,
  un besoin trié depuis le plus haut lot de la base passe sans être retrié
  à la clôture : il l'a été dans le même lot. Accepté.
- Sans base (premier commit, aucune branche par défaut), le contrôle ne
  tourne pas, comme tout contrôle à base ; la CI juge contre la sienne.
- Un besoin `pour : humain` échappe au tri : « Pour toi » le montre à
  chaque état. Accepté.
- La mémoire privée : un besoin privé se trie sur les lots de sa zone ; un
  jalon public ne nomme pas un besoin privé, ce que `--milestone` refuse et
  que le contrôle des fuites garde de toute façon.

## Conséquences

Ranger un besoin ne coûte aucun appel : la raison ou le jalon se donnent à
`socle new need`. Le signal est dans l'état du démarrage. Un projet qui a
un jalon ouvert voit ses besoins d'avant sans raison « à placer » dès la
mise à jour ; la clôture d'un lot les trie, et la clôture d'un jalon
exige la réserve entière triée. Pour défaire : retirer le contrôle, les
deux options et le signal ; les deux champs restent lisibles et sans
effet.
