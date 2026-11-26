<!-- socle: couche=backlog zone=publique -->
# T-0197 — Un correctif qui ne touche que la mémoire n'est pas jugé par tests.regression, et le dit d'un avertissement

> statut : fait · origine : J-2026-11-26-AA · besoin : B-0359 · lu : backlog@dd11ac18 · ref : J-2026-11-26-AH

Dans `checks_tests.regression`, avant `hors_de_tout_adaptateur` : un
correctif dont tous les fichiers (hors tiers) sont dans le dossier de la
mémoire s'avertit, « ne touche que la mémoire : non jugé », comme celui
qui ne touche que des fichiers tiers, au lieu du refus.

## Fait quand

- [x] un test : un commit « Correction : … » qui ne change qu'une entrée de la mémoire passe `tests.regression` avec cet avertissement
- [x] le test de D-0088 (un correctif sur `app/main.dart` refusé) passe inchangé
