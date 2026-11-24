<!-- socle: couche=backlog zone=publique -->
# B-0300 — En session cloud, le hook de fin de tour du conteneur fait pousser la branche repartie de la branche par défaut après la fusion, et recrée la branche distante que GitHub a supprimée

> statut : abandonné · origine : J-2026-11-19-AB · lu : backlog@f0badc5f · ref : D-0168

Mesuré le 19 novembre, après la fusion de la pull request #69
(J-2026-11-19-AB). Le skill `socle-batch` dit qu'après la fusion, la
branche locale repart de la branche par défaut et ne se pousse qu'avec le
premier commit du lot suivant : seule, elle recréerait la branche
distante (B-0220). En session cloud de Claude Code, le hook de fin de
tour du conteneur, qui n'est pas celui du socle, compare la branche à sa
référence distante restée dans le clone et refuse de conclure tant
qu'un commit n'est pas poussé : « There are 1 unpushed commit(s) on
branch … Please push these changes ». La branche avancée en avance
rapide sur le commit de fusion en a un ; la pousser a recréé
`ccr-e554c5dd-1gyrlv` sur GitHub, que la fusion avait supprimée. Les
deux règles se contredisent à chaque lot livré dans une session cloud.

Pistes, à mesurer : ne pas déplacer la branche locale après la fusion
dans une session qui ne mène plus de lot ; élaguer la référence
distante (`git fetch --prune`) avant de la faire repartir, si le hook du
conteneur ne juge alors plus rien ; ou dire que la session suivante
repart de la branche par défaut sur sa propre branche.

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « D-0165 — une légère gêne que l'agent règle lui-même » : après la fusion, en session cloud, la branche repartie se pousse et recrée la branche distante ; l'agent ne la déplace pas, la session qui fusionne n'en menant plus d'autre. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] après la fusion d'un lot en session cloud, la session conclut sans pousser une branche qui n'a rien de plus que la branche par défaut, et sans que la branche distante supprimée par la fusion réapparaisse
