<!-- socle: couche=backlog zone=publique -->
# T-0104 — recul_de_la_cloture exclut le lot de la liste des entrées qu'il a closes

> statut : ouvert · origine : J-2026-11-19-N · besoin : B-0299 · lu : backlog@bd95cf82

Un commit : `recul_de_la_cloture` (`engine/socle/review.py`) exclut
`lot.id` des entrées que le lot a ouvertes et closes.

## Fait quand

- [ ] le refus de la clôture d'un lot relu ne nomme pas le lot parmi les entrées qu'il a closes, et un test le montre
