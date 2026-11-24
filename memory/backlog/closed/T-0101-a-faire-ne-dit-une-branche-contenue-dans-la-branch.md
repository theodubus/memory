<!-- socle: couche=backlog zone=publique -->
# T-0101 — a_faire ne dit une branche contenue dans la branche de travail poussée que si l'origine a encore cette branche de travail

> statut : fait · origine : L-0017 · besoin : B-0292 · lu : backlog@e07d146b · ref : J-2026-11-24-AJ

Un commit : `a_faire` (`engine/socle/human.py`), qui sait déjà les
branches de l'origine (ADR-0090), ne garde une branche contenue dans la
branche de travail poussée que si l'origine a encore cette branche de
travail ; une note de version.

## Fait quand

- [x] un test de `tests/test_humain.py` supprime sur l'origine la branche de travail poussée et lit que l'état ne dit plus qu'elle garde une autre branche
