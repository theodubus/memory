<!-- socle: couche=backlog zone=publique -->
# B-0324 — À une mise à jour, l'installeur n'imprime en entier que les notes de version qui demandent une action ; des autres, le titre et le fichier

> statut : fait · ref : T-0121, J-2026-11-22-D · origine : J-2026-11-21-A · lu : backlog@18f4b4cb

La suggestion 3 de la revue de cap 2 (J-2026-11-21-A), que Théo
retient : « Valider 3 sur apres une mise à jour » (D-0151). À une mise à
jour, `texte_des_notes` (`engine/socle/installer.py`) imprime chaque note
de version entière : depuis le 14 novembre, 71 notes dans
`engine/socle/CHANGES.md`, dont 57 disent « À faire : rien ». La
prochaine mise à jour de chess se lirait en 14 notes au lieu de 71 si
l'installeur n'imprimait en entier que celles dont « À faire » demande
quelque chose, et des autres le titre et le fichier. Une décision
réversible et mesurable (politique, point 3).

Sa place dans les jalons attendait la réponse de Théo sur le sens de
« sur apres une mise à jour ». Le 21 novembre, Théo : « avant la mise à
jour de chess » (D-0152, J-2026-11-21-D). Il rejoint JA-0005, et sa tâche
T-0121 L-0021, le lot de l'installeur qui suit L-0008.

## Satisfait quand

- [x] à une mise à jour, l'installeur imprime en entier les notes de version dont « À faire » n'est pas « rien », et des autres leur titre et le fichier où les lire, en français et en anglais, et un test le montre
