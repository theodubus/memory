<!-- socle: couche=backlog zone=publique -->
# T-0213 — L'état dit en tête qu'une passation attend sur une référence en avance sur la tête locale, avec les instructions, skills et hooks qui changent

> statut : ouvert · origine : J-2026-11-27-U · besoin : B-0374 · ref : D-0235 · lu : backlog@4d53be09

L'avertissement de l'état et la ligne du skill `socle-handoff`.

## Fait quand

- [ ] un test montre l'avertissement en tête de l'état, avec les fichiers d'instructions, de skills et de hooks changés, quand la tête locale est un ancêtre strict de la référence de la passation
- [ ] un test montre qu'il ne paraît pas quand la tête contient la référence
- [ ] le gabarit du skill `socle-handoff` fait lire ce diff avant tout travail, sa copie protégée remise, et la note de version est écrite
