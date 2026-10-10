# Essai du socle sur chess

Les fichiers de ce répertoire préparent l'installation du socle sur
`theodubus/chess` (jalon 8). Rien n'y a été poussé : les essais tournent sur
un clone jetable.

- `docs/chess/adaptateur.toml` — l'adaptateur proposé : l'adaptateur Rust
  maintenu, plus les étapes propres à chess reprises de sa CI et de son
  script de vérification. À valider par Théo à l'installation.
- `docs/chess/mutation-caps.toml` — les plafonds de mutation de chess, repris
  tels quels avec le renvoi à leur raison écrite.

## Ce que les essais ont montré

Porte du jalon 2 (`J-2026-10-10-F`) : en mode adoption, l'audit tourne sur
chess entier en trois secondes et passe, quatre contrôles en avertissement.

Porte du jalon 3 (`J-2026-10-10-H`) : avec cet adaptateur, `socle verify`
exécute les étapes de la CI de chess et elles passent toutes, en quatre
minutes et demie dans le conteneur.

Ce que l'installation sur chess demandera : renommer `CLAUDE.md` en
`AGENTS.md` est une décision, puisque 35 fichiers de chess le nomment ; la
reprise des plafonds de mutation ; une raison écrite sur le test de
déterminisme de la recherche.
