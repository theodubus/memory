<!-- socle: couche=backlog zone=publique -->
# B-0342 — Le tri des constats de revue met au backlog des cas limites rares qui ne sont qu'une légère gêne, contre D-0165

> statut : fait · origine : J-2026-11-24-B · priorité : haute · lu : backlog@202ec8d2 · ref : J-2026-11-24-N

La règle de tri d'ADR-0073, que le skill `socle-review` donne au
relecteur et à l'agent, met au backlog tout constat non bloquant qui
peut se produire dans l'usage normal : un relecteur en trouve toujours,
et le backlog grossit à chaque lot (J-2026-11-24-A : du 14 au 23
novembre, les revues ont ouvert 111 entrées). D-0165, que Théo a
donnée le 24 : le temps va aux ajouts et aux bugs importants, jamais à
un cas limite qui arrive rarement et n'est en pratique qu'une légère
gêne que l'agent peut gérer lui-même.

## Satisfait quand

- [x] un constat de revue qui n'est qu'un cas limite rare, légère gêne que l'agent gère, ne va plus au backlog, et les entrées ouvertes de cette sorte sont refermées
