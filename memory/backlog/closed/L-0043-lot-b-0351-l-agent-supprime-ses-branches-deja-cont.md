<!-- socle: couche=backlog zone=publique -->
# L-0043 — Lot — B-0351 : l'agent supprime ses branches déjà contenues

> statut : fait · origine : J-2026-11-25-AF · lu : backlog@a9d8cc56 · après : L-0042, T-0191, T-0192 · ref : D-0205, J-2026-11-26-K

Les deux tâches de B-0351, sur l'intention que Théo a retenue (D-0202) et
la spécification `docs/fabrication/branches-de-l-agent-specification.md` :
la commande et ce qui l'entoure (T-0191), puis le texte que reçoit un
projet (T-0192). Elles changent un garde-fou, la suppression distante :
une revue adversariale les relit, qui vérifie que rien de ce qui marchait
ne casse. Note de version : oui.

## Revues

### Passe 1 — 2026-11-26

Commits : 3a10ca7d..521a8bc3

- Bloquant : le `git fetch --prune` de la commande, même en `--dry-run`, perdait le commit que seule garde la référence d'une branche disparue
- Ouvre : rien
