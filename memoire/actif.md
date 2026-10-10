<!-- socle: couche=actif zone=publique -->
# Chantier actif

Réécrit au fil du travail et borné. Ce qui en sort s'archive dans le journal.

## En cours

Session du 10 oct. 2026 : jalons 1 à 5 du cadrage, portes humaines en file.

- Jalon 1, inventaire de chess : fait, porte en attente (D-0001).
- Jalon 2, noyau mémoire : fait ; l'audit tourne sur chess entier
  (J-2026-10-10-F). Le format attend sa validation (D-0002).
- Jalon 3, contrat `verify` et adaptateur Rust : adaptateur maintenu écrit,
  adaptateur proposé pour chess dans `docs/chess/adaptateur.toml` ;
  comparaison avec la CI de chess en cours.
- Jalon 4, garde-fous et auto-test : chaque défaut injecté est attrapé
  (F-0002) ; une échappatoire attend sa validation (D-0004).
- Jalon 5, hooks et CI : installés sur ce dépôt, en service dans cette
  session (F-0003) ; la porte réelle attend la protection de branche
  (D-0003).

## Prochaines étapes

- Consigner la comparaison avec la CI de chess quand elle aura tourné.
- Pousser la branche, et voir le check de CI tourner pour de vrai.
- Après les réponses humaines : jalon 6 (B-0001), puis jalon 8 (B-0003).
