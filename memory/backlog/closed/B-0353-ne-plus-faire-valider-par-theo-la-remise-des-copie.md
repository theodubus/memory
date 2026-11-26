<!-- socle: couche=backlog zone=publique -->
# B-0353 — Ne plus faire valider par Théo la remise des copies des skills du socle dans ce dépôt, ni les tests qui lisent leur texte mot pour mot : l'expérience les juge, pas lui

> statut : fait · origine : J-2026-11-25-T · ref : D-0197, D-0196, D-0188, D-0175, D-0168, L-0043, J-2026-11-26-E, J-2026-11-26-K · lu : backlog@3dca4b15

Chaque lot qui change un skill du produit finit sur une demande à Théo :
remettre les copies protégées de `.claude/skills/` et changer les tests
qui lisent leur texte (D-0175, D-0188, D-0196). Théo, le 25 novembre :
« C'est pénible de valider a chaque fois les skills, alors qu'en soit moi
humain ne suis pas plus capable de dire s'ils sont bons ou pas, c'est
l'expérience qui le dit » (J-2026-11-25-T). Dans ce dépôt, en mode
amont, l'agent écrit lui-même les gabarits que les copies reproduisent :
la protection des copies n'ajoute qu'une signature. Retirer la demande
assouplit un garde-fou (politique, point 1) : sa conception passe par la
question d'intention posée à Théo le même jour : il retient l'option A
(D-0197, J-2026-11-25-V), dans ce dépôt seulement ; chess ne change pas.

## Satisfait quand

- [x] un lot qui change un skill du produit se livre sans demande à Théo pour remettre ses copies ni pour les tests qui lisent son texte, sans que l'agent puisse changer une copie autrement que depuis son gabarit
