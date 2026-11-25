<!-- socle: couche=backlog zone=publique -->
# L-0041 — Lot de B-0353 : en mode amont, les copies des skills du socle et les tests de leur texte suivent leur gabarit sans validation

> statut : en cours · origine : J-2026-11-25-V · après : L-0039, T-0184, T-0185 · lu : backlog@1a1f2dc6

Les deux tâches de B-0353, sur l'option A que Théo a retenue (D-0197) et
la conception de ADR-0110 : deux exceptions du mode amont dans les
contrôles du cliquet (`engine/socle/checks_ratchet.py`,
`engine/socle/checks_tests.py`), leurs tests, l'architecture et
`delegate-lot`. Elles touchent le même garde-fou, la validation des
changements que l'agent ne fait pas seul : une revue adversariale les
relit ensemble. Aucune note de version : rien ne change en mode projet.

## Revues

### Passe 1 — 2026-11-25

Commits : 63e10abd..5cc6cf1f
