<!-- socle: couche=backlog zone=publique -->
# T-0205 — Le plafond de memory/directives.md relevé à 24 000 octets, ici et dans le gabarit des garde-fous du produit, sur une demande validée

> statut : fait · origine : J-2026-11-26-AU · ref : D-0220, D-0221, J-2026-11-26-BB · besoin : B-0354 · lu : backlog@6ba8e676

Sur D-0218 (relever le plafond des consignes par une demande qui en
donne la valeur), la demande D-0220 propose 24 000 octets : le budget de
`memory/directives.md` dans `.socle/guardrails.toml` et dans les deux
gabarits des garde-fous du produit, la valeur attendue de
`tests/test_consignes.py` qui le lit, la spécification des consignes et
la note de version. Relever un budget assouplit un garde-fou : rien ne
se commite avant sa réponse.

## Fait quand

- [x] D-0220 est répondue ; validée, elle couvre le changement des trois garde-fous et de la valeur attendue de `tests/test_consignes.py`
- [x] `.socle/guardrails.toml`, `engine/socle/templates/guardrails.toml` et `engine/socle/templates/guardrails.en.toml` portent le budget validé de `memory/directives.md`, et le test de l'installeur le lit
- [x] `docs/fabrication/consignes-specification.md` et la note de version, française et anglaise, disent la valeur, et qu'un projet installé qui la reprend assouplit un garde-fou
