<!-- socle: couche=decisions zone=publique -->
# ADR-0001 — Moteur en Python 3.11+, bibliothèque standard seule ; configuration en TOML

> statut : acceptée · date : 2026-10-10 · source : J-2026-10-10-C

## Contexte

Le cadrage laissait ouvertes deux questions liées : le langage du moteur
(« portable et sans service externe ») et le format des fichiers d'adaptateur
et de politique (TOML ou YAML). Le moteur est copié tel quel dans chaque
projet et son empreinte vérifiée en CI : un binaire par plateforme, ou une
chaîne de compilation imposée à un projet qui n'est pas dans ce langage,
iraient contre la portabilité.

## Décision

Python 3.11 ou plus récent, bibliothèque standard seule. TOML pour les
fichiers de configuration, lu par `tomllib`. Décidé par Théo à
l'initialisation, sur l'option recommandée.

## Conséquences

- Aucune dépendance à installer ; les runners GitHub ont Python.
- Le python3 fourni par macOS est en 3.9 : le lanceur refuse en clair une
  version trop ancienne.
- `tests/test_moteur.py` refuse tout import hors de la bibliothèque standard.
- La défaire voudrait dire réécrire le moteur : coûteux, d'où la question
  posée plutôt que tranchée par l'agent.
