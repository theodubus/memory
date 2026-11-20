<!-- socle: couche=backlog zone=publique -->
# B-0233 — Rien ne signale un lot qui ne tient pas en une session ou dont les sujets ne partagent rien : JA-0005 a réuni 22 sujets sous la forme d'un lot

> statut : fait · origine : J-2026-11-15-J · ref : J-2026-11-20-AD · lu : backlog@e9d08c28

Le 14 novembre, JA-0005 est né sous la forme d'un lot (ADR-0079) pour
réunir « les sujets ouverts qui ne rejoignent aucun autre lot » ; les
revues y ont ajouté les leurs, jusqu'à 22 sujets qui ne partagent ni
fichiers ni tests. L'état l'a montré comme « prochain lot », et Théo l'a
lu ainsi (J-2026-11-15-J). La règle existe (ADR-0079, point 4 ; le skill
`socle-batch` : les mêmes fichiers, le même garde-fou ou les mêmes
tests, ce qui se mène en une session), mais rien ne montre qu'elle est
tordue.

À trancher en le menant : un avertissement de l'état et du rappel de fin
de tour sur un lot qui attend plus de sujets qu'une session n'en mène,
le seuil mesuré sur les lots faits ; ce que l'état peut savoir des
fichiers d'un sujet pas encore fait ; et le skill `socle-batch` qui dit
qu'un ensemble à finir avant une étape est un jalon, ses lots formés
dessous. Il rejoint le jalon JA-0005 à son découpage (D-0118).

## Satisfait quand

- [x] un lot qui ne se mène pas en une session se voit avant qu'on le mène, et un ensemble à finir avant une étape se forme en jalon, ses lots dessous
