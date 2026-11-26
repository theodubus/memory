<!-- socle: couche=backlog zone=publique -->
# L-0046 — Lot — les petites gênes de la mise à jour de chess : CODEOWNERS, correctif de mémoire, commande prise pour une branche, notes datées (T-0196 à T-0199)

> statut : fait · origine : J-2026-11-26-AA · lu : backlog@358e3475 · après : L-0045, T-0196, T-0197, T-0198, T-0199 · ref : J-2026-11-26-AH

Les quatre corrections courtes que la mise à jour de chess du
26 novembre a montrées (JA-0006), chacune sa correction claire et son
test : l'installeur (`_codeowners` pour T-0196, les notes de version
pour T-0199), `tests.regression` (T-0197), la lecture de « Pour toi »
par la fin de tour (`links.py`, T-0198). Chacune change ce que reçoit un
projet : sa note de version, française et anglaise, et son point au
prompt de la prochaine mise à jour de chess. T-0197 et T-0198 changent
chacune un garde-fou, `tests.regression` et un refus de la fin de tour :
leur modèle de menace est dans B-0359 et B-0360, écrit à la revue ; la
revue est adversariale.

## Revues

### Passe 1 — 2026-11-26

Commits : 49d3e3d2..1929f510

- Bloquant : la limite d'un clone superficiel datait la copie remplacée (T-0199)
- Bloquant : T-0197 et T-0198 changent un garde-fou sans modèle de menace
- Ouvre : rien
