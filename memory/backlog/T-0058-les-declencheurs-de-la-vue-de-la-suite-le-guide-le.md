<!-- socle: couche=backlog zone=publique -->
# T-0058 — Les déclencheurs de la vue de la suite : le guide, les instructions du socle, la fin d'un lot, le résumé de la CI et une ligne de l'état

> statut : ouvert · origine : J-2026-11-16-AD · besoin : B-0274 · lu : backlog@d0b4fc0a

La seconde tâche de B-0274 (J-2026-11-16-AD) : les déclencheurs que
la spécification de B-0274 nomme. Le résumé de la CI change le workflow
posé, un fichier protégé : une demande à l'humain le cite.

## Fait quand

- [ ] le guide le dit en une phrase, les instructions du socle disent de coller le format détaillé quand l'humain demande la suite, et le skill `socle-batch` met le format compact dans le récap de la clôture d'un lot
- [ ] le workflow de la CI posé écrit le format détaillé dans le résumé de son exécution, et un test le montre
- [ ] l'état a une ligne qui renvoie à la commande, et le skill `delegate-lot` de l'atelier l'appelle à l'annonce et à la clôture d'un lot
