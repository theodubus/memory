<!-- socle: couche=backlog zone=publique -->
# L-0048 — Lot — les empreintes d'index d'un tour non commité, et le besoin pour l'humain hors du découpage (T-0202, T-0203)

> statut : ouvert · origine : J-2026-11-26-AB · lu : backlog@8b8edb89 · après : L-0047, T-0202, T-0203

Deux corrections courtes du retour d'usage de chess du 26 novembre
(JA-0006) : l'empreinte d'index que `socle new` et `socle show --index`
font citer (`cli.py`, T-0202, son ADR d'abord), et le besoin pour
l'humain hors des besoins à découper (`memory.py`, `FORMAT.md`,
T-0203). Chacune change ce que reçoit un projet : sa note de version,
française et anglaise, et son point au prompt de la prochaine mise à
jour de chess. Aucune ne pose ni ne change de garde-fou : le contrôle
des lectures reste le même.
