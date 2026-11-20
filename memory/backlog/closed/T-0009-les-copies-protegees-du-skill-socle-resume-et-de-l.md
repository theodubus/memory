<!-- socle: couche=backlog zone=publique -->
# T-0009 — En mode amont, une copie protégée qui diffère de son gabarit est signalée

> statut : fait · origine : J-2026-11-14-F · ref : J-2026-11-20-K · besoin : B-0218 · lu : backlog@9966bbbd

Un commit : en mode amont, l'état ou un contrôle compare chaque copie protégée que pose l'installeur (les skills du socle, la CI du socle) à son gabarit et nomme celles qui diffèrent ; un contrôle a son défaut injecté et son témoin sain dans `engine/socle/selftest.py`. Le rafraîchissement des copies de ce dépôt est T-0072.

## Fait quand

- [x] en mode amont, une copie protégée qui diffère de son gabarit est nommée par l'état ou par un contrôle, une copie égale ne l'est pas, et un test le montre
