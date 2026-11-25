<!-- socle: couche=backlog zone=publique -->
# T-0182 — La reprise en session neuve sur toute demande de reprendre, sans prompt : la passation écrite dans handoff.md, que la session neuve trouve, juge et retire, selon la spécification de D-0190 élargie par la réserve de Théo

> statut : fait · origine : J-2026-11-25-K · besoin : B-0346 · après : T-0181 · ref : J-2026-11-25-T, D-0190, T-0180 · lu : backlog@5eb2c337

Par un sous-agent, en un ou deux commits : la spécification
`docs/fabrication/reprends-specification.md`, que Théo a validée
(D-0190) avec sa réserve (J-2026-11-25-J, J-2026-11-25-K), d'abord
corrigée : la reprise part sur tout premier message d'une session neuve
qui demande de reprendre ou de continuer, quelle qu'en soit la forme
(« reprends », « continue », « reprends les travaux ») ; le mot n'est
qu'un exemple, dans le récap, l'état et le gabarit d'`AGENTS.md`. Puis
ce que dit sa section « Où cela s'écrit » : le moteur (`socle handoff
write`, `socle handoff check` sans argument, la ligne de l'état, la
couche `passation` du format et ses contrôles, leurs défauts injectés),
les skills `socle-handoff` et `socle-batch`, le gabarit d'`AGENTS.md`,
`HELP.md`, le skill `delegate-lot`, une note de version en français et
en anglais.

Le push qui change les tests que D-0190 nomme porte sa réponse,
consignée depuis le texte exact de Théo au journal : avant T-0181, le
moteur ne la compte que dans cette plage.

## Fait quand

- [x] la spécification dit qu'une demande de reprendre, quelle qu'en soit la forme, lance la reprise, et la session tenue par un test qui lit le gabarit d'`AGENTS.md`
- [x] `socle handoff write` et `socle handoff check` sans argument tiennent les cas de la spécification, chacun par un test qui échoue sur le commit parent, avec leurs défauts injectés et leur témoin sain
- [x] les tests que D-0190 nomme sont changés ou retirés, et sa réponse consignée dans le même push
- [x] les skills, le gabarit d'`AGENTS.md`, `HELP.md` et la note de version le disent ; les copies protégées remises
