<!-- socle: couche=decisions zone=publique -->
# ADR-0002 — Contenu en français, identifiants en anglais

> statut : remplacée · date : 2026-10-10 · source : J-2026-10-10-C · remplacée-par : ADR-0027

## Contexte

Les projets de Théo, dont `chess`, sont documentés en français. Le socle
génère des fichiers lus par l'humain (AGENTS.md, mémoire, messages des
contrôles) et des fichiers lus par des scripts.

## Décision

Ce que l'humain lit est en français : documentation, mémoire, messages,
commentaires, valeurs de statut (`mesuré`, `supposé`…). Ce qui est du code
est en anglais : noms de commandes (`state`, `check`, `verify`), clés TOML,
identifiants Python publics. Décidé par Théo à l'initialisation.

## Conséquences

Les statuts se comparent sans accents ni majuscules (`Réfuté` vaut
`refute`), pour qu'une saisie humaine ne casse pas un contrôle. Rendre les
messages traduisibles reste possible plus tard, sans changer les clés.
