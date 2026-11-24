<!-- socle: couche=backlog zone=publique -->
# B-0192 — Mettre la classe d'un test dans la clé de son constat toléré demande une vraie lecture de la structure du fichier

> statut : abandonné · origine : J-2026-11-12-H · priorité : basse · lu : backlog@172a367b · ref : D-0168

La clé d'un test creux toléré par l'adoption ne dit pas la classe du
test : deux tests de même nom, dans deux classes d'un même fichier, ont la
même clé (ADR-0069). Le lot B-0190 a tenté d'y mettre la classe, lue par
une expression régulière ; sa revue a montré que cela ne tient pas d'un
langage à l'autre, et qu'une lecture fausse change la clé de constats déjà
tolérés (ADR-0070). La partie a été retirée. Théo, le 12 novembre : « Ok
reste retirée et sujet basse priorité ».

À reprendre seulement si un projet en a besoin, avec une vraie lecture de
la structure du fichier, langage par langage.

Le 21 novembre, Théo le fait passer à JA-0006 (D-0153,
J-2026-11-21-O) : il se juge à la mise à jour de chess.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « Attendus d'un fait qui n'arrive pas : ils reviennent s'il arrive » : la classe d'un test dans la clé d'un constat toléré : aucun projet n'en a eu besoin, ce que son critère prévoit pour se clore.

## Satisfait quand

- [ ] deux tests de même nom, dans deux classes d'un même fichier, se tolèrent séparément sans qu'aucun constat déjà toléré change de clé ; ou, aucun projet n'en ayant eu besoin, le besoin se clôt sans suite
