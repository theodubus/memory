<!-- socle: couche=backlog zone=publique -->
# B-0200 — La fusion de sa pull request par l'agent, une option de la politique que l'humain active

> statut : fait · origine : J-2026-11-13-F · ref : T-0020, T-0064, J-2026-11-20-AS · lu : backlog@e0c4802b

Ici, l'agent fusionne lui-même sa pull request : CI verte, revue faite,
aucune demande en attente sur son contenu (D-0092, « Règles propres à ce
dépôt » d'AGENTS.md). chess a écrit la même règle de son côté
(`docs/fabrication/chess/mise-a-jour-2026-11-13.md`). Le produit
l'offrirait comme une option de la politique, que l'humain seul active ;
la fusion reste refusée par le hook tant qu'elle n'est pas activée
(politique, point 4). Consigne de Théo du 13 novembre : tout ce qui est
utile intègre le socle (J-2026-11-13-F).

## Satisfait quand

- [x] dans un projet équipé dont l'humain l'a voulu, l'agent fusionne lui-même sa pull request aux conditions de D-0092 ; sans ce choix, la fusion lui reste refusée
