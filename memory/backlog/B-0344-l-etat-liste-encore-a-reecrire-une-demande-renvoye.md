<!-- socle: couche=backlog zone=publique -->
# B-0344 — L'état liste encore « à réécrire » une demande renvoyée qu'une demande nouvelle a déjà remplacée

> statut : ouvert · origine : J-2026-11-24-AC · lu : backlog@3b9c4fd5

`socle state` liste toute demande de statut « renvoyée » sous
« RENVOYÉE (contexte insuffisant) : D-NNNN — à réécrire en une demande
qui la remplace », même quand une demande nouvelle l'a remplacée et a
reçu sa réponse : D-0160, remplacée par D-0174 le 24 novembre, y
figure encore (J-2026-11-24-AC). Rien, dans le format des demandes, ne
dit qu'une demande en remplace une autre ; le texte de D-0174 le dit
seulement en prose. Une session neuve, qui ne sait que ce que l'état
lui montre, peut réécrire la demande une seconde fois.

## Satisfait quand

- [ ] une demande renvoyée que remplace une demande posée n'est plus listée « à réécrire » par l'état, et un test le montre
- [ ] une demande renvoyée sans remplaçante l'est toujours, et un test le montre
