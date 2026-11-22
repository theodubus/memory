<!-- socle: couche=backlog zone=publique -->
# T-0132 — Les pistes de la branche repartie après la fusion, essayées en session cloud contre le hook de fin de tour du conteneur, et la règle retenue soumise à Théo

> statut : ouvert · origine : J-2026-11-21-Q · besoin : B-0300 · lu : backlog@6c894b15

Un commit : dans une session cloud, après la fusion d'une pull request, chaque piste de B-0300 essayée contre le hook de fin de tour du conteneur : ne pas déplacer la branche locale ; élaguer la référence distante (`git fetch --prune`) avant de la faire repartir ; la session suivante repart sur sa propre branche. Le relevé dans `docs/fabrication/`, et une demande, qui cite B-0300, soumet à Théo la règle retenue pour le gabarit de `socle-batch`.

## Fait quand

- [ ] le relevé des pistes essayées est dans `docs/fabrication/`
- [ ] une demande soumet la règle à Théo, et sa réponse est consignée au journal
