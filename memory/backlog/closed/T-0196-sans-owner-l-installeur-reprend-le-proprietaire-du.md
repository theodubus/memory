<!-- socle: couche=backlog zone=publique -->
# T-0196 — Sans --owner, l'installeur reprend le propriétaire du CODEOWNERS en place et le dit

> statut : fait · origine : J-2026-11-26-AA · besoin : B-0358 · lu : backlog@dd11ac18 · ref : J-2026-11-26-AH

`installer._codeowners` : sans `--owner`, le propriétaire se lit sur la
ligne du CODEOWNERS en place qui protège la politique, celle que le
gabarit pose ; trouvé, il complète le fichier comme `--owner` le ferait
et le journal dit « CODEOWNERS : <propriétaire> … » ; la ligne « !! »
ne reste que sans fichier, ou sans cette ligne.

## Fait quand

- [x] un test relance la mise à jour sans `--owner` sur un projet installé avec `--owner` : aucune ligne « !! » sur CODEOWNERS, le propriétaire nommé, une ligne ajoutée au gabarit posée
- [x] un test garde la ligne « !! » sur un projet sans CODEOWNERS
