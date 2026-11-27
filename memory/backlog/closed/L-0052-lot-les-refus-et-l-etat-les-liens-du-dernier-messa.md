<!-- socle: couche=backlog zone=publique -->
# L-0052 — Lot — les refus et l'état : les liens du dernier message, trois refus qui disent leur correction, le correctif de documentation, la session en retard sur sa passation

> statut : fait · origine : J-2026-11-27-U · ref : D-0235, J-2026-11-27-Z · après : L-0051, T-0210, T-0211, T-0212, T-0213 · lu : backlog@4d53be09

Le premier lot de ce que D-0235 retient (point 12) : les refus et l'état,
quatre tâches qui changent ce que le moteur refuse ou dit à l'agent, au
démarrage comme en fin de tour. T-0210 et T-0211 touchent le hook de
l'agent (`engine/socle/hooks.py`), qui s'ouvre sur la preuve de D-0235
(ADR-0098), et leurs contrôles (`engine/socle/links.py`,
`engine/socle/checks_memory.py`) ; T-0212 le contrôle des correctifs
(`engine/socle/checks_tests.py`) ; T-0213 l'état
(`engine/socle/state.py`) et le gabarit du skill `socle-handoff`. Environ
200 lignes de code, tests compris davantage : une revue adversariale.

## Revues

### Passe 1 — 2026-11-27

Commits : 429064e7..42933329

- Bloquant : une consigne privée d'avant la plage se citait sans empreinte, sa base privée jamais lue
- Bloquant : le hook commit-msg annonçait « la CI le refusera » pour un correctif de la seule documentation ou mémoire
- Ouvre : rien
