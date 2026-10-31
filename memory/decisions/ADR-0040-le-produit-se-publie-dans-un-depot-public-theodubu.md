<!-- socle: couche=decisions zone=publique -->
# ADR-0040 — Le produit se publie dans un dépôt public, theodubus/socle, sous MIT, par un workflow à chaque fusion

> statut : acceptée · date : 2026-10-31 · source : D-0056@d6c50c78 · lu : decisions@4007cd0e

## Contexte

Le produit et l'atelier sont séparés dans ce dépôt (ADR-0033@ef7d0d5b), et
un dépôt de distribution était prévu à la première version mûre
(B-0083@09a071c2). En session cloud, installer ou mettre à jour le socle
obligeait à ajouter ce dépôt privé à la session du projet, qui passait à
deux dépôts et perdait ses hooks à la reprise : trois incidents sur le
pilote. Théo a validé la publication (D-0056@d6c50c78) sous licence MIT
(D-0057@eefaeecf), a créé le dépôt public et le secret du jeton.

## Décision

- **Le dépôt public `theodubus/socle`** contient le produit seul : le moteur
  sous `socle/`, un README (`engine/README.md` ici) et la licence MIT que
  Théo y a posée. L'atelier, sa mémoire, ses tests et ses bancs restent ici,
  privés.
- **Un workflow de ce dépôt** (`.github/workflows/distribution.yml`) l'y
  publie à chaque fusion sur `main` qui touche `engine/`, et à la demande,
  avec un jeton à accès fin qui n'écrit que dans le dépôt public ; il ne
  publie que si quelque chose change.
- **L'installation et la mise à jour** clonent ce dépôt public, sans
  l'ajouter à la session : `PYTHONPATH=/tmp/socle python3 -m socle
  install`. Le README, le guide et l'étape de l'installeur le disent.

## Conséquences

Une session de projet reste sur son seul dépôt pour installer comme pour
mettre à jour ; la procédure en deux sessions ne sert plus que si un
second dépôt doit être ajouté. Le prix : le moteur est lisible par tous,
et une publication ne se reprend pas tout à fait. Ce qui reste supposé :
qu'une session cloud clone un dépôt public sans l'ajouter ; la première
installation ou mise à jour le dira. Pour défaire : rendre le dépôt
privé, retirer le workflow et revenir au clone de ce dépôt.
