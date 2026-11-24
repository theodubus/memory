<!-- socle: couche=backlog zone=publique -->
# B-0296 — L'essentiel des échecs à la fin de tour : aucune longueur maximale par ligne, et des sorties de tests ou des lignes de trace prennent la place des tests en échec

> statut : abandonné · origine : J-2026-11-19-D · lu : backlog@40a7a5e5 · ref : D-0168

L'essentiel des échecs que donne la fin de tour (T-0096,
`verification.lignes_d_echec`) n'a aucune longueur maximale par ligne :
une ligne de journal JSON finie par `error"}` se recopie entière. Et du
bruit entre dans son plafond : un `self.fail(…)` d'une trace, les
sorties `print` des tests, et, sous unittest `-q`, la ligne où le texte
imprimé par un test se colle aux points de progression
(« F.FEconnection error »). Relevé par la revue de L-0018
(J-2026-11-19-D).

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X3 — peaufine la machinerie sans gêne constatée » : la longueur des lignes de l'essentiel des échecs. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] chaque ligne de l'essentiel des échecs a une longueur bornée
- [ ] les sorties des tests et les lignes de code d'une trace n'y prennent pas la place des tests en échec
