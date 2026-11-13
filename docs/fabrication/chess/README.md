# Essai du socle sur chess

Les fichiers de ce répertoire préparent l'installation du socle sur
`theodubus/chess` (jalon 8). Rien n'y a été poussé : les essais tournent sur
un clone jetable.

- `docs/fabrication/chess/adaptateur.toml` — l'adaptateur proposé : l'adaptateur Rust
  maintenu, plus les étapes propres à chess reprises de sa CI et de son
  script de vérification. À valider par Théo à l'installation.
- `docs/fabrication/chess/mutation-caps.toml` — les plafonds de mutation de chess, repris
  tels quels avec le renvoi à leur raison écrite.

- `docs/fabrication/chess/essai-a-blanc-2026-11-11.md` — le compte rendu de l'essai à blanc du
  11 novembre 2026, avec la version publiée du socle.
- `docs/fabrication/chess/installation-2026-11-11.md` — le compte rendu de l'arrêt de
  l'installation réelle à son étape 3, sur une condition fausse du prompt.
- `docs/fabrication/chess/installation-2026-11-12.md` — le compte rendu de l'installation
  faite, et les neuf constats qu'elle a rendus côté socle.
- `docs/fabrication/chess/mise-a-jour-2026-11-13.md` — le compte rendu de la mise à
  jour faite, et les huit gênes qu'elle a rendues côté socle.
- `docs/fabrication/chess/prompt-mise-a-jour.md` — le prompt de la mise à jour du socle sur
  chess, qui dit aussi ce qui a été ajouté et corrigé depuis l'installation.
- `docs/fabrication/chess/prompt-installation.md` — les deux prompts de l'installation, à
  coller dans la session de chess : installer, puis poser la feuille de route.

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
