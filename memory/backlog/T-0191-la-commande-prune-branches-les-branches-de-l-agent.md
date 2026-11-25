<!-- socle: couche=backlog zone=publique -->
# T-0191 — La commande prune-branches : les branches de l'agent contenues ailleurs, vérifiées sur l'origine et supprimées sous bail ; l'état, le hook avant push, le message du hook, la politique

> statut : ouvert · origine : J-2026-11-25-AF · besoin : B-0351 · lu : backlog@1c4b30e5 · ref : D-0202

Selon `docs/fabrication/branches-de-l-agent-specification.md` : la
commande `socle prune-branches` et son `--dry-run`, les refus de l'origine
gardés dans le dossier local du socle, la ligne de l'état pour l'agent et
les listes de l'humain qui ne donnent plus que ses branches, le hook avant
push qui laisse passer une suppression seule, le message du hook de
l'agent qui nomme la commande, la clé `prune_branches` des gabarits de la
politique ; une décision (ADR) pour le mécanisme.

## Fait quand

- [ ] dans un dépôt d'essai, une branche de l'agent contenue dans la branche par défaut se supprime, et une branche de l'humain, une branche non contenue ou une branche qui a bougé depuis la vérification restent, chacune avec son test
- [ ] `prune_branches = false` rend toutes les branches à l'humain, et la commande refuse
- [ ] un refus de l'origine redonne la branche à l'humain dans l'état
