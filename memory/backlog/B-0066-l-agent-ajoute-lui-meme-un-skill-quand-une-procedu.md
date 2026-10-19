<!-- socle: couche=backlog zone=publique -->
# B-0066 — L'agent ajoute lui-même un skill quand une procédure revient

> statut : ouvert · origine : J-2026-10-19-C · lu : backlog@dbd16c96

Demandé par Théo (texte exact au journal) : que l'agent ajoute des skills
de lui-même quand c'est nécessaire. Un skill est une procédure, dans un
dossier avec son fichier SKILL.md, que l'agent charge à la demande sur sa
description au lieu de la relire à chaque session ; Claude Code, Codex et
d'autres agents lisent le même format.

Pertinent ici pour deux raisons :

- le fichier d'instructions du projet est relu en entier à chaque session
  (les budgets de B-0010) ; les procédures rares du socle (poser une
  demande, relayer une réponse, basculer en privé, ranger le backlog)
  pourraient en sortir, vers des skills posés par l'installeur ;
- un projet a ses propres procédures qui reviennent (lancer le banc,
  publier une version), que l'agent reconstitue à chaque fois ; il
  pourrait l'écrire en skill la deuxième fois.

À régler avant d'écrire :

- le moteur ne connaît aucun agent : les skills vivent côté agent, comme
  les hooks ; le moteur peut seulement les poser, les lire et les
  contrôler ;
- un skill oriente l'agent, il ne doit contredire ni les instructions ni la
  politique (contourner un hook, écrire un fichier protégé, répondre à la
  place de l'humain) ; les hooks refusent toujours l'acte, mais un contrôle
  pourrait refuser le skill lui-même, avec son défaut injecté ;
- un skill dit comment faire, la mémoire dit ce qui est et pourquoi : il ne
  recopie ni fait ni valeur liée, et le refus des copies devrait s'y
  appliquer ;
- « quand nécessaire » : une règle mesurable (la même procédure refaite
  plusieurs fois au journal ?) plutôt qu'un jugement, et si l'ajout est
  libre ou passe par une ADR (point 3 de la politique) ;
- BMAD Method fait des skills sa forme principale, et l'un de ses modules
  en fabrique : à regarder avant de concevoir (J-2026-10-19-D).
