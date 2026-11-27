<!-- socle: couche=backlog zone=publique -->
# T-0207 — La feuille de route rendue en une seule forme, A2-d, dans le terminal et en Markdown, selon sa spécification : les deux formats actuels et l'option --by retirés

> statut : ouvert · origine : J-2026-11-27-E · besoin : B-0364 · ref : D-0212, D-0214 · lu : backlog@ae9a1848

Le rendu de `socle roadmap` (`engine/socle/roadmap.py`) selon
`docs/fabrication/feuille-de-route-specification.md` : « Maintenant »,
« Ensuite » en `X. [K/N] titre` alignés, seul le premier jalon ouvert
déplié, « Pour toi », « En réserve », en ses deux rendus, le terminal et
Markdown. Le calcul de la suite ne change pas. Les tests qui lisent les
deux formats actuels ou `--by` changent ou disparaissent : une demande
les nomme, chacun avec ce qui le remplace, une fois le code écrit ; ils
ne se commitent qu'après sa réponse. Plus de 150 lignes de code et de
tests, un format que d'autres parties lisent : revue adversariale.

## Fait quand

- [ ] le rendu du terminal et le rendu Markdown suivent la spécification, en français et en anglais, et des tests le prouvent point par point, comme elle les énumère
- [ ] les formats compact et détaillé, leur légende et l'option `--by` n'existent plus, et un test le vérifie
- [ ] la demande qui nomme les tests changés ou supprimés est validée par Théo
