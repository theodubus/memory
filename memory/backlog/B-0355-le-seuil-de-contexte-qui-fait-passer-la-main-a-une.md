<!-- socle: couche=backlog zone=publique -->
# B-0355 — Le seuil de contexte qui fait passer la main à une session neuve se fonde sur une mesure de l'usage

> statut : ouvert · origine : J-2026-11-26-A · ref : D-0194 · lu : backlog@62db4107

La règle de D-0194 fait ranger une session dont la conversation passe
300 000 jetons de contexte, « au-delà, chaque appel coûte de plus en
plus » (`docs/fabrication/organisation-proportionnee.md`). Le
raisonnement tient (chaque appel relit tout le contexte : 46,8 millions de
jetons relus du cache pour 170 000 écrits dans la session du 25-26
novembre), mais le nombre n'a jamais été mesuré contre l'usage, ni
contre le coût d'une passation : la session du 25 novembre, rangée au
milieu de L-0042, a fait d'un commit trois correctifs à réintégrer.
Théo, le 26 novembre : « je veux pas que ce soit une décision par defaut
non reflechie » (J-2026-11-26-A).

## Satisfait quand

- [ ] le seuil, ou ce qui le remplace, s'appuie sur des points de la semaine mesurés par lot, selon la taille du contexte et le coût d'une passation, et Théo l'a retenu
