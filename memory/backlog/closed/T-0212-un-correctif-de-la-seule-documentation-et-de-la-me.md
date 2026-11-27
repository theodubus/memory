<!-- socle: couche=backlog zone=publique -->
# T-0212 — Un correctif de la seule documentation et de la mémoire n'est plus jugé par `tests.regression`

> statut : fait · origine : J-2026-11-27-U · besoin : B-0373 · ref : D-0235, J-2026-11-27-V · lu : backlog@4d53be09

Le cas de la documentation dans `tests.regression`
(`engine/socle/checks_tests.py`), à côté de celui de la mémoire (B-0359).

## Fait quand

- [x] un test montre qu'un « Correction : … » qui ne touche qu'un fichier de documentation, ou la documentation et la mémoire, passe avec l'avertissement
- [x] un test montre qu'un correctif qui touche la documentation et un fichier hors de tout adaptateur reste refusé
- [x] le défaut injecté et le témoin sain sont dans `engine/socle/selftest.py`, et la note de version est écrite
