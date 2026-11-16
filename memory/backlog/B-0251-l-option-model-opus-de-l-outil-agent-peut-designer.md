<!-- socle: couche=backlog zone=publique -->
# B-0251 — L'option model opus de l'outil Agent peut désigner un Opus plus ancien que celui de la session : un sous-agent servi par un moindre modèle sans que rien le dise

> statut : ouvert · origine : J-2026-11-16-A · lu : backlog@1fd23187

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

La piste : le skill dit de vérifier le modèle qui sert un sous-agent (le
détail de consommation de la session, `modelUsage`) et, pour le plus
capable, de laisser le sous-agent hériter du modèle de la session (sans
`model`) quand c'est lui ; le gabarit du skill du produit le dit aussi.

## Fait quand

- [ ] le skill `socle-batch` et son gabarit disent comment s'assurer du modèle qui sert un sous-agent, et qu'un alias peut désigner une version plus ancienne que celle de la session
