<!-- socle: couche=demandes zone=publique -->
# D-0243 — Un besoin qui n'a jamais eu de tâche se clôt-il « fait » sur ses cases cochées, le défaut injecté besoin-fait-sans-tache-faite devenant un besoin fait dont la seule tâche est abandonnée (`A`), ou la clôture écrit-elle une tâche faite (`B`) ?

> date : 2026-11-28 · forme : séance

## Question posée

Clore un besoin sans tâche (B-0386). Aujourd'hui, un besoin ne peut se clore « fait » que si l'une de ses tâches est faite. Deux choix :
- `A`, ma recommandation : un besoin qui n'a jamais eu de tâche se clôt « fait » sur ses cases cochées, en un geste. La règle actuelle reste pour un besoin qui a eu des tâches : si toutes sont abandonnées, lui aussi. L'état ne dit plus « à fermer » qu'un besoin réellement clôturable. Cela change le défaut injecté `besoin-fait-sans-tache-faite` de l'auto-test, qui deviendrait « un besoin fait dont la seule tâche est abandonnée » ; ta réponse l'autorise.
- `B` : la clôture écrit elle-même une tâche faite. La règle ne change pas, mais le backlog garde une tâche fictive.
