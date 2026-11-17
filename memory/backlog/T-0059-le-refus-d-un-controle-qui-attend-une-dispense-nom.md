<!-- socle: couche=backlog zone=publique -->
# T-0059 — Le refus d'un contrôle qui attend une dispense nomme celle qu'il voit hors du bloc final de trailers, et dit de la mettre avec les autres

> statut : ouvert · origine : J-2026-11-17-D · besoin : B-0275 · lu : backlog@6141fdaf

Un commit : le refus d'un contrôle qui attend une dispense ou un trailer (`docs.correspondance`, et ceux qui lisent `Dispense-test` et `Corrige`) cherche aussi ces lignes hors du bloc final ; s'il en trouve, il nomme le commit et dit de mettre la ligne dans le dernier paragraphe du message, avec les autres trailers.

## Fait quand

- [ ] un commit dont la dispense de doc est dans un paragraphe à part, avant les lignes d'attribution, reçoit un refus qui le nomme et dit où écrire la dispense, et un test le montre
