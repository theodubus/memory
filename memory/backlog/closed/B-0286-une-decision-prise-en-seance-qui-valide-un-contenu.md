<!-- socle: couche=backlog zone=publique -->
# B-0286 — Une décision prise en séance qui valide un contenu montré dans la conversation (un format, un exemple) ne garde pas ce contenu : la spécification qui en découle peut le perdre sans que rien ne le voie

> statut : fait · origine : J-2026-11-18-N · lu : backlog@496c1e8a · ref : J-2026-11-19-C

Le 16 novembre, Théo a validé en séance (D-0127) une vue de la suite
montrée dans la conversation, avec ses exemples ; la décision consignée
ne garde que la question et sa réponse, le journal ne recopie pas la
proposition, et B-0274 l'a résumée sans ses tableaux. L'implémentation,
puis la revue, ont jugé contre ce résumé : aucune n'a pu voir l'écart,
que Théo a relevé à la livraison (J-2026-11-18-N). Une décision en séance
qui approuve un contenu (un format, un exemple, un texte) doit le garder
là où la spécification et la revue le lisent ; `socle decision` a
`--about <chemin>`, qui ne vaut que pour un fichier déjà écrit.

## Satisfait quand

- [x] le contenu qu'une décision prise en séance approuve se lit, mot pour mot, depuis la décision, et la spécification qui en découle le cite
- [x] le relecteur d'un lot qui sert une telle décision reçoit ce contenu dans son dossier
