<!-- socle: couche=backlog zone=publique -->
# B-0177 — Le dernier commit d'agent, que lit socle state, peut être le commit tiers d'une autre session

> statut : abandonné · origine : J-2026-11-11-T · ref : J-2026-11-14-L · lu : backlog@b5f49f69

La revue de B-0169 : `dernier_commit_agent`, dans engine/socle/human.py,
prend le dernier commit qui porte un marqueur d'agent, y compris le commit
d'une autre session qui ne touche que des chemins déclarés tiers. Une
réponse de l'humain écrite au terminal puis commitée avant la fusion d'un
tel commit n'est alors plus listée par l'état (`fait_par_l_humain`). Non
reproduit.

Abandonné le 14 novembre, sur la décision de Théo (D-0111, J-2026-11-14-L) :
un cas exotique, jamais reproduit.

## Satisfait quand

- [ ] un test montre qu'un commit qui ne touche que des chemins tiers ne compte pas comme le dernier commit de l'agent, ou que le cas ne se produit pas
