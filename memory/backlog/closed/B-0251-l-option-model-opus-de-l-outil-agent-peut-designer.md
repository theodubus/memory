<!-- socle: couche=backlog zone=publique -->
# B-0251 — L'option model opus de l'outil Agent peut désigner un Opus plus ancien que celui de la session : un sous-agent servi par un moindre modèle sans que rien le dise

> statut : fait · origine : J-2026-11-16-A · priorité : haute · ref : J-2026-11-16-Q, J-2026-11-16-G · lu : backlog@1fd23187

Le skill `socle-batch` fait donner à chaque sous-agent son modèle
explicitement, à son lancement (outil `Agent` : `model`). Sous Claude
Code, cette option ne prend qu'un alias (`opus`, `sonnet`, `haiku`,
`fable`), et l'alias `opus` a désigné le 15 novembre `claude-opus-4-8`,
quand la session tournait sur `claude-opus-5-5` (J-2026-11-16-A) : les
deux implémenteurs du lot B-0234 ont été servis par un Opus plus ancien
que celui de la session, ce qu'aucune sortie ne disait sauf la
notification d'un sous-agent coupé (« model sent to the API ») et le
détail de consommation de `list_events`. Le relecteur doit être le plus
capable jusqu'à Opus, jamais un moindre que l'implémenteur (D-0117) :
l'alias ne le garantit pas.

Théo élargit le sujet le 16 novembre (J-2026-11-16-G) : chaque modèle
demandé tourne sur sa dernière version, Sonnet, Haiku ou Fable comme
Opus, pour un sous-agent comme pour la session ; et il veut le sujet fait
prochainement (priorité haute, au lot B-0264).

La piste : le skill dit, pour chaque famille demandée, de vérifier la
version qui sert réellement un sous-agent (le détail de consommation de
la session, `modelUsage`, ou la notification d'un sous-agent) ; quand
l'alias désigne une version plus ancienne que la dernière de sa famille,
de passer par ce qui la donne (hériter du modèle de la session quand
c'est lui, ou le dire à Théo, qui choisit celui de la session) ; et de
l'écrire au récap. Le gabarit du skill du produit le dit aussi.

## Fait quand

- [x] le skill `socle-batch` et son gabarit disent que chaque modèle demandé, pour un sous-agent comme pour la session, tourne sur la dernière version de sa famille, comment le vérifier, et quoi faire quand un alias désigne une version plus ancienne
- [x] le récap d'un lot dit la version qui a servi chaque sous-agent
