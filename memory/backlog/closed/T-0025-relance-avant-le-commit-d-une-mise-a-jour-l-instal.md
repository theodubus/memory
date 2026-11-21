<!-- socle: couche=backlog zone=publique -->
# T-0025 — L'installeur lit les notes de version déjà lues dans la copie du moteur du dernier commit

> statut : fait · origine : J-2026-11-14-X · ref : J-2026-11-21-H · besoin : B-0225 · lu : backlog@9966bbbd

Un commit : `engine/socle/installer.py` lit les identifiants des notes dans la copie du dernier commit (`git show HEAD:…`), comme ADR-0052 lit l'historique, plutôt que dans l'arbre ; un correctif, avec son test qui échoue sur le commit parent. `tests/test_notes_de_version.py` fige l'ancien comportement : changer ses valeurs attendues se demande.

## Fait quand

- [x] relancé avant le commit d'une mise à jour, l'installeur nomme les mêmes notes qu'au premier passage, dans le message de commit et dans « Et maintenant », et un test qui échoue sur le commit parent le prouve
