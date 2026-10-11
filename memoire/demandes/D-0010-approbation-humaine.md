<!-- socle: couche=demandes zone=publique -->
# D-0010 — Approuver un changement fait par l'humain lui-même

> date : 2026-10-11 · origine : `socle approve`

## Décision demandée

L'humain approuve un changement qu'il a fait lui-même sur un garde-fou ou un fichier protégé.

## Contexte

Écrite et validée d'un seul geste par `socle approve`, une commande que le hook de l'agent refuse : elle ne sert qu'à l'humain, pour que ses propres changements protégés restent visibles et tracés. Raison donnée : Étape de mémoire privée en CI, hook du message de commit, et verrou qui note le format de la mémoire (B-0019@50bfd468)

## Éléments cités

- `.github/workflows/socle.yml` — fichier protégé modifié par l'humain lui-même ; empreinte nouvelle `sha256:f319848693cde3f7`.
- `.socle/git-hooks/commit-msg` — fichier protégé modifié par l'humain lui-même ; empreinte nouvelle `sha256:0d197607ea2ca648`.
- `.socle/moteur.lock` — fichier protégé modifié par l'humain lui-même ; empreinte nouvelle `sha256:abee9a47e58d87c3`.

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
