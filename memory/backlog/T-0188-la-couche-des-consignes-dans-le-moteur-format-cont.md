<!-- socle: couche=backlog zone=publique -->
# T-0188 — La couche des consignes dans le moteur : format, contrôles, démarrage, lecture prouvée, socle new directive, archive, installeur

> statut : ouvert · origine : J-2026-11-25-AD · besoin : B-0161 · lu : backlog@192f6745 · après : T-0187

Le moteur selon la spécification validée
(`docs/fabrication/consignes-specification.md`) : le préfixe `C-` et la
couche `consignes` (`engine/socle/memory.py`), les contrôles de format,
de levée, d'ajout seul et de lecture prouvée, avec leurs défauts injectés
et leurs témoins sains (`engine/socle/selftest.py`), le groupe du
démarrage et ses parts (`engine/socle/state.py`), `socle new directive`,
`socle show C-NNNN`, `socle archive`, l'installeur et les gabarits de la
mémoire et des garde-fous, le format 4.

## Fait quand

- [ ] une entrée du journal qui cite une consigne sans son empreinte, ou avec une empreinte périmée, est refusée, et le témoin qui porte l'empreinte actuelle passe
- [ ] une consigne levée sans demande validée, ou dont le texte exact change, est refusée
- [ ] l'état injecte la ligne de résumé de chaque consigne en vigueur, et pas les levées
