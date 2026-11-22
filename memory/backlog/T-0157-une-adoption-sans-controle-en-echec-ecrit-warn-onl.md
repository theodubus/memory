<!-- socle: couche=backlog zone=publique -->
# T-0157 — Une adoption sans contrôle en échec écrit warn_only = [], et ses mises à jour redisent qu'elle n'a rien à inscrire

> statut : ouvert · origine : J-2026-11-22-J · besoin : B-0329 · lu : backlog@1b35b8e8

Un commit : `_adopter` (`engine/socle/installer.py`) écrit
`[adoption] warn_only = []` à une adoption sans contrôle en échec,
comme le constat 2 de B-0329 le dit ; sa note de version.

## Fait quand

- [ ] la mise à jour d'un projet adopté sans contrôle en échec dit qu'il n'a rien à inscrire, et un test qui échoue sur le commit parent le montre
