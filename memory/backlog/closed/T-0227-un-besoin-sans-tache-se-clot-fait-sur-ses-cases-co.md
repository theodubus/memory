<!-- socle: couche=backlog zone=publique -->
# T-0227 — Un besoin sans tâche se clôt « fait » sur ses cases cochées, et l'état ne dit « à fermer » qu'un besoin que socle close accepterait (D-0243)

> statut : fait · origine : J-2026-11-28-B · ref : D-0243, ce commit · besoin : B-0386 · lu : backlog@2b83126f

Un commit, sur la décision de Théo du 28 novembre (D-0243, l'option A) :
`memoire.formes` accepte « fait » un besoin qui n'a jamais eu de tâche,
sur sa section « Satisfait quand » cochée, et garde la règle d'ADR-0083
pour un besoin qui a eu des tâches ; l'état (`ordre`) ne dit « à
fermer » qu'un besoin que `socle close` accepterait. La spécification
s'écrit d'abord, en ADR.

## Fait quand

- [x] `memoire.formes` accepte « fait » un besoin sans aucune tâche dont la section « Satisfait quand » a au moins une case, toutes cochées, et refuse un besoin fait dont les tâches sont toutes abandonnées, comme un besoin fait sans tâche ni case
- [x] l'état ne dit « à fermer » qu'un besoin que `socle close` accepterait : un besoin sans tâche, ses cases cochées, y est ; un besoin aux tâches closes dont une case reste vide n'y est pas
- [x] le défaut injecté `besoin-fait-sans-tache-faite` est un besoin fait dont la seule tâche est abandonnée ; un défaut injecté pour le besoin fait sans tâche ni case ; un témoin : un besoin pour l'humain sans tâche, ses cases cochées, se clôt par `socle close` et passe le commit et la CI
- [x] `engine/socle/FORMAT.md`, l'ADR et la note de version, en français et en anglais, le disent
