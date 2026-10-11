<!-- socle: couche=demandes zone=publique -->
# D-0012 — Approuver un changement fait par l'humain lui-même

> date : 2026-10-11 · origine : `socle approve`

## Décision demandée

L'humain approuve un changement qu'il a fait lui-même sur un garde-fou ou un fichier protégé.

## Contexte

Écrite et validée d'un seul geste par `socle approve`, une commande que le hook de l'agent refuse : elle ne sert qu'à l'humain, pour que ses propres changements protégés restent visibles et tracés. Raison donnée : Migration de ce dépôt au format 2 de la mémoire (B-0036@e2148746, ADR-0018@61948166)

## Éléments cités

- `.github/CODEOWNERS` — fichier protégé modifié par l'humain lui-même ; empreinte nouvelle `sha256:be43c9d3a58db389`.
- `.github/workflows/socle.yml` — fichier protégé modifié par l'humain lui-même ; empreinte nouvelle `sha256:42e6c28c5731a7c9`.
- `.socle/adapter.toml` — fichier protégé modifié par l'humain lui-même ; empreinte nouvelle `sha256:7af70234a26a4826`.
- `.socle/engine.lock` — fichier protégé modifié par l'humain lui-même ; empreinte nouvelle `sha256:c1dc9555cb027105`.
- `.socle/policy.toml` — fichier protégé modifié par l'humain lui-même ; empreinte nouvelle `sha256:8975d4f71c8f1148`.
- `.socle/socle` — fichier protégé modifié par l'humain lui-même ; empreinte nouvelle `sha256:5653c010d49b03b4`.

## Où regarder

Le diff du commit qui porte cette demande ; les fichiers et clés cités ci-dessus, voir [le format des demandes](../../moteur/socle/FORMAT.md).

## Options

Approuver garde le changement : effort nul, risque porté par l'humain, réversible par un nouveau changement approuvé. Ne pas approuver laisse la CI refuser le changement, ce qui est réversible et sans effort.

## Conséquences

Si l'humain valide, la CI accepte le changement cité. S'il refuse, la CI le refuse. Sans réponse, rien ne passe : cette demande naît avec sa réponse.

## Recommandation

Vérifié : les empreintes et les clés citées ci-dessus sont celles de l'arbre au moment de l'approbation. Supposé : rien, l'humain décide seul.

## Réponses possibles

- `valider` — la CI accepte le changement cité.
- `contexte-insuffisant` — sans objet ici ; présent parce que toute demande le propose.
