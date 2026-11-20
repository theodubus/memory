<!-- socle: couche=backlog zone=publique -->
# T-0117 — Une décision donnée n'autorise que ce que nomme le texte de l'humain, sa section « Décision donnée »

> statut : ouvert · origine : J-2026-11-20-AC · besoin : B-0313 · lu : backlog@74fc5e24

Un commit : pour une décision donnée (`Demande.donnee`, déjà
définie et inutilisée), `_justifie`, `_valide_par` et
`demandes.reponse-seule` ne lisent ce qu'elle autorise que dans sa
section « Décision donnée » ; un défaut injecté et son témoin sain dans
l'auto-test.

## Fait quand

- [ ] un test, une clé des garde-fous ou un fichier protégé que seul le titre d'une décision donnée nomme n'est pas autorisé, et un test qui échoue sur le commit parent le montre
- [ ] nommé dans le texte de l'humain, il l'est encore, et un test le montre
