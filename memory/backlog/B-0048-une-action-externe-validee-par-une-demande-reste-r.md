<!-- socle: couche=backlog zone=publique -->
# B-0048 — Une action externe validée par une demande reste refusée par le hook

> statut : ouvert · origine : J-2026-10-12-M · lu : backlog@47ec3e4f

Mesuré à R6 : D-0016 autorise de pousser l'historique du projet d'échecs
dans la copie, et le hook refuse quand même `git push … main:main`, faute
de savoir qu'une validation existe. Le push revient alors à l'humain, même
validé. Piste : une demande validée qui nomme l'action exacte (le dépôt et
la branche) la laisse passer au hook, une fois. Voisin de B-0018.

D-0026, réponse de Théo `rien` (J-2026-10-14-V) : « rien pour l'instant, on
se le garde en tete et on voit si ça finit par etre bloquant ». Le sujet
reste ouvert pour cela : chaque refus nouveau d'une action validée se note
ici, avec sa date. Seule option qui garderait le geste de l'humain pour
preuve, si le refus devient bloquant : une fois, après sa fusion sur `main`.

Le 22 oct., il reprend B-0018, abandonné à son profit (J-2026-10-22-G) : le
refus d'un push vers la branche par défaut d'un dépôt local jetable, même
sujet (un push refusé que l'humain juge légitime) et même réponse de Théo.

## Satisfait quand

- [ ] si un refus nouveau d'une action validée bloque le travail, noté ici avec sa date (la condition de D-0026, J-2026-11-18-L), une action externe que Théo a validée par une demande qui la nomme exactement (le dépôt, la branche) se fait par l'agent, une fois, au lieu de lui revenir ; sans cette demande, ou une seconde fois, elle reste refusée ; sans refus nouveau, rien ne se redemande
