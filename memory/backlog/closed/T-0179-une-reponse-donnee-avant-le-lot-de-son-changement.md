<!-- socle: couche=backlog zone=publique -->
# T-0179 — La réponse donnée avant le lot de son changement : la spécification soumise à Théo, qui choisit entre la consigner depuis le journal au lot et une validation que la CI compte hors de sa plage

> statut : fait · origine : J-2026-11-24-AV · besoin : B-0347 · ref : J-2026-11-25-J, D-0180, T-0134, B-0142, J-2026-11-24-AZ · lu : backlog@23ed6516

Un commit : une demande soumet à Théo la spécification qui lève la
contradiction de B-0347. Formée d'abord comme une règle des skills (le
texte exact de la réponse au journal tout de suite, la réponse consignée
par le lot qui fait le changement), elle sort de L-0036 à l'écriture
(J-2026-11-24-AZ) : une demande écrite dont la réponse attend au journal
reste « en attente » dans l'état, que l'humain voit et que le récap lui
redemanderait. Deux pistes, à peser dans la spécification avec leur
modèle de menace :

- la règle des skills, réservée aux questions posées dans la
  conversation (la variante légère, décision consignée en séance au
  lot), la demande écrite d'un test se posant dans la session du lot
  qui le change ;
- `tests.attendus` et le cliquet comptent aussi une validation déjà
  poussée, hors de la plage, tant que le test qu'elle nomme n'a pas
  changé depuis elle : un assouplissement d'un garde-fou, que seule une
  demande validée permet.

## Fait quand

- [x] une demande soumet la spécification à Théo, et sa réponse est consignée au journal
