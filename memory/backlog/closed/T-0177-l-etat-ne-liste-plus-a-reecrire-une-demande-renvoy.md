<!-- socle: couche=backlog zone=publique -->
# T-0177 — L'état ne liste plus « à réécrire » une demande renvoyée qu'une demande posée cite dans ses éléments cités

> statut : fait · origine : J-2026-11-24-AV · besoin : B-0344 · ref : D-0180, J-2026-11-24-BA · lu : backlog@0c12b8a3

Un commit : `socle state` (`engine/socle/state.py`, la ligne « RENVOYÉE
(contexte insuffisant) ») ne liste plus une demande renvoyée qu'une
demande plus récente cite dans sa section « Éléments cités », comme
D-0174 cite D-0160 (« la demande précédente, renvoyée le 23 novembre
faute de contexte, que celle-ci remplace ») : la demande qui remplace
cite naturellement celle qu'elle réécrit, et une demande répondue est
gelée, si bien qu'un champ nouveau ne marquerait pas D-0174. Le skill
`socle-request` (gabarit et anglais) et `FORMAT.md` disent que la
demande qui en remplace une renvoyée la cite dans ses éléments cités ;
une note de version.

## Fait quand

- [x] une demande renvoyée qu'une demande posée cite dans ses éléments cités n'est plus listée « à réécrire » par l'état, et un test le montre
- [x] une demande renvoyée que rien ne cite l'est toujours, et un test le montre
