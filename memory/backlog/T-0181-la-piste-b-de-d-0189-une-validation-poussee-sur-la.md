<!-- socle: couche=backlog zone=publique -->
# T-0181 — La piste B de D-0189 : une validation poussée sur la branche, ou fusionnée et citée par une tâche ouverte dont ce qu'elle nomme n'a pas bougé, couvre son changement ; l'avertissement de la réponse seule retiré, avec ses tests

> statut : ouvert · origine : J-2026-11-25-J · besoin : B-0347 · ref : D-0189, T-0179 · lu : backlog@5eb2c337

Un commit, par un sous-agent : la piste B de
`docs/fabrication/reponse-avant-le-lot-specification.md`, que Théo a
validée (D-0189, J-2026-11-25-J) : « La règle » et son tableau de cas,
« Ce qui disparaît », « Modèle de menace ». Le contrôle compte une
validation ajoutée sur la branche depuis son départ comme une de la
plage ; une validation déjà fusionnée, si une tâche ouverte la cite et
que ce qu'elle nomme n'a pas bougé depuis le parent du commit de sa
demande. Se retirent `demandes.reponse-seule`, sa fonction de plage, sa
mention au hook avant push, ses deux défauts injectés et les tests que
D-0189 nomme ; reste
`test_une_reponse_consignee_mais_pas_commitee_n_est_plus_en_attente`.
La règle du même push se retire des gabarits de `socle-request` et de
`socle-batch` et du skill `delegate-lot` ; les copies protégées se
remettent sur une demande courte. La note de version, en français et en
anglais.

Ce push porte aussi la réponse de D-0189, consignée depuis le texte
exact de Théo au journal (J-2026-11-25-J) : le moteur d'avant ne la
compte que dans la plage du retrait de ses tests.

## Fait quand

- [ ] chaque cas du tableau de « La règle » a son test, qui échoue sur le commit parent ; la règle nouvelle a son défaut injecté et son témoin sain
- [ ] les tests et les deux défauts injectés que nomme D-0189 sont retirés, et sa réponse consignée dans le même push
- [ ] les gabarits de `socle-request` et de `socle-batch`, et le skill `delegate-lot`, ne disent plus la règle du même push ; leurs copies protégées remises
- [ ] la note de version le dit, en français et en anglais
