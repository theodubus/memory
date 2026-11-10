<!-- socle: couche=backlog zone=publique -->
# B-0139 — À la mise à jour du socle, l'ancien moteur qui juge la CI compte les clés nouvelles des garde-fous pour un assouplissement

> statut : fait · origine : J-2026-11-08-S · lu : backlog@9dbc0778 · ref : J-2026-11-09-S

La mise à jour du socle nomme les réglages nouveaux du gabarit des
garde-fous, à déclarer une fois le moteur nouveau commité, parce que
l'ancien moteur, qui juge encore la CI, compte une clé inconnue pour un
assouplissement (B-0123). Le pilote a vu sa CI rester rouge jusqu'à la
validation des fichiers protégés (J-2026-11-08-S). Chercher un ordre, ou un
jugement par le moteur nouveau, qui laisse la CI verte.

Fait quand :
- [x] une mise à jour qui apporte des clés nouvelles aux garde-fous ne fait plus échouer la CI à cause d'elles, prouvé sur un projet d'essai

Le critère disait « laisse la CI verte » ; précisé sur la revue du lot
(J-2026-11-09-T), parce que la mesure le dément à la lettre. Mesuré
(J-2026-11-09-S) : le moteur nouveau commité avec ses réglages,
`cliquet.garde-fous` passe ; la CI ne reste rouge que sur
`protege.fichiers`, jusqu'à la réponse de l'humain, comme D-0071 le veut
quand la branche par défaut exige la CI du socle. Sans cette exigence, les
fichiers protégés attendent non commités, et l'installeur dit de déclarer
les réglages nouveaux une fois le moteur commité (B-0123). Le symptôme que
le pilote rapportait, une CI rouge jusqu'à la validation, reste donc, par
la décision D-0071, mais plus à cause des clés nouvelles.
