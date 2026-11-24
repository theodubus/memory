<!-- socle: couche=backlog zone=publique -->
# T-0179 — Une réponse donnée avant le lot de son changement se recopie aussitôt au journal, et le lot la consigne de là, avec le changement : les skills socle-request et socle-batch le disent

> statut : ouvert · origine : J-2026-11-24-AV · besoin : B-0347 · ref : D-0180, T-0134, B-0142 · lu : backlog@23ed6516

Un commit, qui lève la contradiction de B-0347 sans assouplir la CI (elle
ne compte toujours que les validations de sa plage, B-0142) : quand
l'humain répond avant le lot du changement qu'elle autorise, son texte
exact entre aussitôt au journal, poussé, et la réponse ne se consigne
pas encore ; le lot qui fait le changement la consigne en citant ce
texte (`--quote-file`, l'entrée du journal en référence), et la pousse
avec lui, dans le même push. La section « Relayer une réponse » du
gabarit de `socle-request` et l'étape 1 de celui de `socle-batch` (et
leur anglais) le disent ; une ADR, la décision réversible ; une note de
version. Les copies protégées remises avec celles des autres skills du
lot.

## Fait quand

- [ ] un test lit la règle dans les gabarits de `socle-request` et de `socle-batch`, en français et en anglais
