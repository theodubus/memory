<!-- socle: couche=backlog zone=publique -->
# B-0355 — Le seuil de contexte qui fait passer la main à une session neuve se fonde sur une mesure de l'usage

> statut : ouvert · origine : J-2026-11-26-A · ref : D-0194, D-0204, D-0209 · lu : backlog@62db4107

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

Dans JA-0006, avant la mise à jour de chess, qui reçoit le seuil avec le
skill `socle-batch` et le guide (D-0204) : la clôture de L-0043 et celle
de T-0186 notent au journal, avec leur coût en points de la semaine, la
taille du contexte de la session (`get_session`, `context_usage`) ;
puis une proposition à Théo, garder, changer ou retirer le chiffre, ou
dire que deux lots ne tranchent pas. Le 26 novembre, Théo retient la
suggestion 1 de la revue de cap 8 (D-0209) : la proposition se fonde sur
les mesures déjà prises (L-0043, J-2026-11-26-I ; L-0042, J-2026-11-25-AI ;
la session de la revue de cap 8, J-2026-11-26-N), sans attendre celle de
T-0186, qui attendait elle-même B-0355 (T-0193). La règle ne fait passer la main qu'à
la fin d'un lot : la session du 25 novembre s'est arrêtée au milieu de
L-0042, sous le seuil, ce qui n'était pas la règle.

## Satisfait quand

- [ ] le seuil, ou ce qui le remplace, s'appuie sur des points de la semaine mesurés par lot, selon la taille du contexte et le coût d'une passation, et Théo l'a retenu
