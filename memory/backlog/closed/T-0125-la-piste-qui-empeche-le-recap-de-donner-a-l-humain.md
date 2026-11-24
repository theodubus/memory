<!-- socle: couche=backlog zone=publique -->
# T-0125 — La piste qui empêche le récap de donner à l'humain une branche que l'origine n'a plus, soumise à Théo avec la preuve vue en session qu'elle cite

> statut : fait · origine : J-2026-11-21-Q · besoin : B-0311 · lu : backlog@6c894b15 · ref : J-2026-11-24-AI, J-2026-11-24-AO, D-0178

Un commit : une demande, qui cite B-0311, soumet à Théo l'une des deux pistes du besoin, avec sa spécification : le hook de fin de tour juge les branches que « Pour toi » donne à supprimer contre l'origine (`git ls-remote --heads origin`), comme il juge déjà le lien d'une demande citée ; ou une entrée du journal ne donne plus de geste futur à l'humain, l'état seul les calculant. La première change le hook de l'agent (`engine/socle/hooks.py`), qu'ADR-0098 n'ouvre que sur une preuve : la demande cite celle que B-0311 donne, vue en session (J-2026-11-20-Q : l'agent a redemandé plusieurs fois à Théo de supprimer une branche que GitHub n'avait plus, et Théo l'a relevé), et dit qu'ADR-0098 nomme deux preuves, un refus à tort et un contournement, quand celle-ci est un geste faux donné à l'humain. Avec son modèle de menace si la piste pose un refus.

## Fait quand

- [x] une demande soumet à Théo la piste et sa spécification, avec la preuve vue en session qu'elle cite, et sa réponse est consignée au journal
