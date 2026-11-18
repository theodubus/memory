<!-- socle: couche=backlog zone=publique -->
# T-0021 — Le lecteur des titres ne retire un dièse final que précédé d'une espace

> statut : ouvert · origine : J-2026-11-13-G · besoin : B-0203 · lu : backlog@9966bbbd

Un commit : `TITRE_RE` (`engine/socle/memory.py`) ; les citations dont l'empreinte change, comptées et dites au journal.

## Fait quand

- [ ] un titre d'entrée qui finit par un dièse collé à un mot le garde, une fermeture précédée d'une espace se retire encore, et un test le montre
- [ ] le journal dit combien de citations d'empreinte le changement périme
