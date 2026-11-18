<!-- socle: couche=backlog zone=publique -->
# T-0024 — L'état élague les branches distantes disparues avant de les donner à supprimer, ou dit que sa liste date du dernier fetch

> statut : fait · origine : J-2026-11-12-O · besoin : B-0193 · lu : backlog@9966bbbd · ref : J-2026-11-18-X, J-2026-11-18-Y, ADR-0090

Un commit : `branches_a_supprimer` (`engine/socle/human.py`), ou un hook qui va déjà chercher l'origine, élague ; à défaut, le message dit d'où vient la liste et comment la rafraîchir ; un correctif, avec son test qui échoue sur le commit parent.

## Fait quand

- [x] une branche supprimée sur l'origine, que le clone garde encore, n'est plus donnée à supprimer, ou le message dit qu'elle vient du dernier fetch et comment élaguer ; un test qui échoue sur le commit parent le prouve
