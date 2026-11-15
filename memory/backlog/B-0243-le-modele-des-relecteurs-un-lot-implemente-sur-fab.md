<!-- socle: couche=backlog zone=publique -->
# B-0243 — Le modèle des relecteurs : un lot implémenté sur Fable, et le relecteur à froid d'une demande, encore du modèle de la session

> statut : ouvert · origine : J-2026-11-15-K · lu : backlog@90ff4f28

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

## Fait quand

- [ ] le skill `socle-review`, en français et en anglais, dit qu'un lot implémenté sur Fable fait demander à l'humain, avant la revue, s'il veut aussi Fable pour le relecteur (D-0119)
- [ ] le skill `socle-batch`, en français et en anglais, dit qu'aucun sous-agent n'implémente sur Fable sauf si l'humain le veut (D-0119)
- [ ] le skill `socle-request` dit le modèle du relecteur à froid, explicitement à son lancement
