<!-- socle: couche=backlog zone=publique -->
# B-0243 — Le modèle des relecteurs : un lot implémenté sur Fable, et le relecteur à froid d'une demande, encore du modèle de la session

> statut : fait · origine : J-2026-11-15-K · ref : J-2026-11-20-AD · lu : backlog@90ff4f28

La revue du lot 5 (J-2026-11-15-K), constats pour le backlog 3 et 4,
de même nature : le modèle qu'un relecteur reçoit.

- Le skill `socle-review` donne au relecteur le modèle le plus capable
  jusqu'à Opus, jamais un moindre que celui qui a implémenté, et Fable
  seulement si l'humain le demande (D-0117). Un lot que l'humain a fait
  implémenter sur Fable met ces trois règles en conflit : le texte ne dit
  pas si son choix vaut aussi pour le relecteur. Théo tranche le 15
  novembre (D-0119, J-2026-11-15-L) : un lot implémenté sur Fable (le
  lot, pas la session qui orchestre), l'agent lui demande, avant la
  revue, s'il veut aussi Fable pour le relecteur ; et, comme pour la
  revue, aucun implémenteur sur Fable sauf si l'humain le veut.
- Le skill `socle-request` donne encore au relecteur à froid d'une
  demande « le modèle de la session », que la règle du modèle de
  `socle-batch` peut faire moins coûteux ; ce relecteur joue l'humain qui
  décide. D-0117 ne vise que la revue d'un lot : à trancher, avec le coût
  de cette relecture (B-0197).

## Satisfait quand

- [x] un lot que l'humain fait implémenter sur Fable n'est relu sur Fable que s'il le veut, et aucun sous-agent n'implémente sur Fable sans lui (D-0119)
- [x] le relecteur à froid d'une demande reçoit le modèle que le skill nomme, pas celui de la session par défaut
