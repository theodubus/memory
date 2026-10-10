<!-- socle: couche=actif zone=publique -->
# Chantier actif

Réécrit au fil du travail et borné. Ce qui en sort s'archive dans le journal.

## En cours

Session du 10 oct. 2026 : jalons 1 à 5 du cadrage, faits ; leurs portes
humaines attendent en file.

- Jalon 1, inventaire de chess : porte en attente (D-0001).
- Jalon 2, noyau mémoire : l'audit tourne sur chess (J-2026-10-10-F) ; le
  format attend sa validation (D-0002).
- Jalon 3, `verify` et adaptateur Rust : la CI de chess passe sous
  `socle verify` (J-2026-10-10-H).
- Jalon 4, garde-fous et auto-test : chaque défaut injecté est attrapé
  (F-0002) ; une échappatoire attend sa validation (D-0004).
- Jalon 5, hooks et CI : en service sur ce dépôt et sur GitHub
  (J-2026-10-10-G) ; `main` est protégée, la vraie porte attend le check
  exigé et l'accord pour une pull request de démonstration (D-0003).
- Les quatre demandes ont été réécrites après le retour de Théo
  (J-2026-10-10-I), et le contrat des demandes durci en conséquence.

## Prochaines étapes

- Lire les réponses aux demandes D-0001 à D-0004 et en tirer les suites.
- Après D-0002 : jalon 8, l'installation réelle sur chess (B-0003).
- Puis jalon 6 sur un projet jetable (B-0001).
