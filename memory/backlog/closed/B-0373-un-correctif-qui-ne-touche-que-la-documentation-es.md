<!-- socle: couche=backlog zone=publique -->
# B-0373 — Un correctif qui ne touche que la documentation est refusé faute d'un test qu'aucun test ne peut donner

> statut : fait · origine : J-2026-11-27-U · ref : D-0235, T-0212, J-2026-11-27-V · lu : backlog@4d53be09

Chez chess (`docs/fabrication/chess/cout-et-frictions-2026-11-26.md`, §4), un commit de documentation titré
« Correction : … » a dû passer sur une autre branche. Confirmé
(`docs/fabrication/chess/relecture-cout-et-frictions-2026-11-27.md`) : `FIX_DEFAUT` (`engine/socle/checks_tests.py`) lit
« correction » comme un correctif ; depuis B-0359, un correctif qui ne
touche que la mémoire n'est plus jugé, mais un correctif qui ne touche
que la documentation reste refusé comme hors de tout adaptateur. Le
préfixe français reste lu : l'agent écrit ses titres en français
(ADR-0027).

Retenu par Théo le 27 novembre (D-0235, point 3) : la documentation et
la mémoire.

## Modèle de menace

`tests.regression` arrête un correctif sans le test qui le prouve. Il
laisse passer désormais, avec un avertissement, un correctif qui ne
touche que la documentation et la mémoire : rien qu'un test prouverait.
Un correctif qui touche aussi un autre fichier reste jugé comme avant.

## Satisfait quand

- [x] un correctif qui ne touche que la documentation et la mémoire passe `tests.regression`, avec un avertissement
- [x] un correctif qui touche aussi un autre fichier reste jugé comme avant
