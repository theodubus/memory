<!-- socle: couche=backlog zone=publique -->
# B-0074 — Installer le socle et BMAD Method en une seule commande

> statut : fait · origine : J-2026-10-20-C · lu : backlog@9b2e2382 · ref : J-2026-10-20-E

Demandé par Théo (texte exact au journal). Aujourd'hui, le produit
combiné s'installe en deux commandes : celle de BMAD (par npm), puis celle
du socle, qui reconnaît BMAD. Une option de l'installeur du socle installe
BMAD d'abord, à une version éprouvée avec le socle, dans la langue du
projet, puis le socle par-dessus : chemins tiers, personnalisation, tout
le reste. Sans Node ni npx, l'installeur le dit avec le remède ; sans uv,
dont les skills de BMAD ont besoin, il prévient. Une installation qui
trouve BMAD déjà là ne le réinstalle pas.
