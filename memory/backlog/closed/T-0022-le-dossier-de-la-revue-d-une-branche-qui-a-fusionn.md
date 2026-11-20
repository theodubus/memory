<!-- socle: couche=backlog zone=publique -->
# T-0022 — Le dossier de la revue retire ce qu'une fusion de la branche par défaut a apporté à la branche du lot

> statut : fait · origine : J-2026-11-15-K · ref : J-2026-11-20-AJ · besoin : B-0241 · lu : backlog@9966bbbd

Un commit : `base_par_defaut` (`engine/socle/review.py`) mesure le lot sans ce que la fusion de la branche par défaut a apporté ; un correctif, avec son test qui échoue sur le commit parent.

## Fait quand

- [x] le dossier d'un lot dont la branche a fusionné la branche par défaut ne montre ni le code ni les entrées closes que la fusion a apportés, et un test qui échoue sur le commit parent le prouve
