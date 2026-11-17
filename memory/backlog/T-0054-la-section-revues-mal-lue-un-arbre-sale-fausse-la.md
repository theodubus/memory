<!-- socle: couche=backlog zone=publique -->
# T-0054 — La section Revues mal lue : un arbre sale fausse « la même passe », une ligne de bloquant écrite autrement est ignorée en silence

> statut : ouvert · origine : J-2026-11-16-Y · besoin : B-0263 · lu : backlog@db14eeec

Relevé par la revue de T-0047, passe 2 du lot L-0013 (J-2026-11-16-Y),
constats 1 et 4 pour le backlog. `meme_passe` (`engine/socle/review.py`)
compare l'arbre au HEAD de la passe, alors que le dossier juge l'arbre,
fichiers suivis modifiés compris : une relance sur un état inchangé mais
sale est refusée comme une passe nouvelle sans recul, et la ligne
`Commits` dit `X..X`. Et `LIGNE_BLOQUANT` (`engine/socle/memory.py`) ne lit
que `- Bloquant : …` : `- **Bloquant** : …`, `- Bloquant 1 : …` ou
`1. Bloquant : …` sont ignorés sans erreur, et ni le regard ni la même
cause ne s'exigent alors. Le livrable, un commit : la même passe se
reconnaît sur un arbre sale, et une ligne de bloquant mal écrite est
refusée ou lue.

## Fait quand

- [ ] une relance de `socle review` sur un arbre inchangé, sale, redonne la même passe sans en écrire une autre, et un test le montre
- [ ] une ligne de bloquant écrite autrement que `- Bloquant :` dans une passe est refusée par un contrôle, avec son défaut injecté
