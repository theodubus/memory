<!-- socle: couche=decisions zone=publique -->
# ADR-0012 — Un second adaptateur Python, sous pytest avec mutmut

> statut : acceptée · date : 2026-10-10 · source : J-2026-10-10-W@0891c986 · lu : decisions@042a80a1

## Contexte

Le jalon 6 éprouve le socle sur un second langage, dynamique, avec un outil
de mutation (B-0001@11079f77). L'outil candidat du cadrage pour Python,
mutmut, n'exécute les tests que sous pytest. L'adaptateur `python` s'en
tient à la bibliothèque standard (`unittest`), pour qu'un projet comme ce
dépôt n'ait aucune dépendance ; il ne peut donc pas porter mutmut.

## Décision

Deux adaptateurs Python sont maintenus :

- `python` : `unittest`, compilation de chaque fichier, mutation déclarée
  absente avec son remplacement ;
- `python-pytest` : pytest pour les tests et le rejeu des correctifs, mutmut
  pour la mutation, sa sortie lue par le lecteur `mutmut` du moteur. Ses
  modules de mutation supposent la disposition `src/` ; un projet dont le
  paquet est à la racine les nomme dans sa copie.

Les deux partagent la langue (`language = "python"`) : la section `[code]`
d'un projet qui n'en a pas se prend dans l'adaptateur `python`.

## Conséquences

Un projet Python choisit son adaptateur à l'installation. Un projet sous
pytest qui prendrait l'adaptateur `python` le verrait vite : depuis Python
3.12, `unittest` qui ne trouve aucun test rend un code d'erreur. Le
balayage de mutation reste à lancer à la main ou par un workflow propre au
projet, comme pour Rust : le workflow de mutation générique est au backlog.

Pour défaire : retirer `python-pytest.toml` ; les projets qui l'ont copié
gardent leur copie.
