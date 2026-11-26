<!-- socle: couche=backlog zone=publique -->
# L-0048 — Lot — les empreintes d'index d'un tour non commité, et le besoin pour l'humain hors du découpage (T-0202, T-0203)

> statut : fait · ref : J-2026-11-26-AR · origine : J-2026-11-26-AB · lu : backlog@8b8edb89 · après : L-0047, T-0202, T-0203

Deux corrections courtes du retour d'usage de chess du 26 novembre
(JA-0006) : l'empreinte d'index que `socle new` et `socle show --index`
font citer (`cli.py`, T-0202, son ADR d'abord), et le besoin pour
l'humain hors des besoins à découper (`memory.py`, `FORMAT.md`,
T-0203). Chacune change ce que reçoit un projet : sa note de version,
française et anglaise, et son point au prompt de la prochaine mise à
jour de chess. Aucune ne pose ni ne change de garde-fou : le contrôle
des lectures reste le même.

## Revues

### Passe 1 — 2026-11-26

Commits : cdf9788a..f9a2c7b1
Relue par l'agent, dossier court (124 lignes de code et de tests, ni
garde-fou ni format lu ailleurs).

- Bloquant : sans base de travail, le hook de l'agent ne juge que l'arbre et refusait l'empreinte du dernier commit
- Ouvre : rien
