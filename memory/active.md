<!-- socle: couche=actif zone=publique -->
# Chantier actif

Réécrit au fil du travail et borné. Ce qui en sort s'archive dans le journal.

## En cours

B-0029 fait (ADR-0019, J-2026-10-11-O) : le privé se choisit couche par
couche (`[private] layers`) et entrée par entrée (`--private`, `--public`),
et `socle prive basculer <ID>` passe une entrée publique en privé en ne
laissant que son identifiant. Ce dépôt est au format 2 depuis la migration
faite par Théo (B-0036, commit bba48a6).

## Prochaines étapes

1. B-0031 : la langue de la mémoire au choix du projet (mots-clés, statuts,
   titres des gabarits), les chemins étant déjà en anglais (ADR-0018).
2. B-0030 : les adaptateurs JS/TS, Go, Java, Ruby et PHP, chacun éprouvé sur
   un projet jetable.
3. À la demande de Théo, plus tard : B-0035 (la documentation du projet),
   précédé de B-0034 (le parcours de l'utilisateur) ; B-0033 et B-0037.
