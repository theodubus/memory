<!-- socle: couche=backlog zone=publique -->
# T-0157 — Une adoption sans contrôle en échec écrit warn_only = [], et ses mises à jour redisent qu'elle n'a rien à inscrire

> statut : abandonné · origine : J-2026-11-22-J · besoin : B-0329 · lu : backlog@1b35b8e8 · ref : D-0168

Un commit : `_adopter` (`engine/socle/installer.py`) écrit
`[adoption] warn_only = []` à une adoption sans contrôle en échec,
comme le constat 2 de B-0329 le dit ; sa note de version.

T-0157 s'abandonne le 24 novembre 2026 par D-0168 avec son besoin B-0329, sous « X2 — imaginé par un relecteur, jamais vu, rattrapé ou bénin » du tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`).

## Fait quand

- [ ] la mise à jour d'un projet adopté sans contrôle en échec dit qu'il n'a rien à inscrire, et un test qui échoue sur le commit parent le montre
