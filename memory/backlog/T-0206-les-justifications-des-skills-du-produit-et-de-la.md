<!-- socle: couche=backlog zone=publique -->
# T-0206 — Les justifications des skills du produit et de la section du socle d'AGENTS.md sorties vers le guide, déplacées et non coupées

> statut : ouvert · origine : J-2026-11-26-AU · besoin : B-0354 · ref : D-0223, D-0224 · lu : backlog@6ba8e676

Sur D-0218, les skills du produit et la section du socle d'`AGENTS.md`,
chargés en entier à chaque usage, gardent leur plafond : ce qui y
justifie une règle sans la dire (le pourquoi, l'incident qui l'a fait
naître) sort vers le guide (`engine/socle/HELP.md` et sa version
anglaise), déplacé mot pour mot, et la règle reste. Marges mesurées le
26 novembre, sur 8 000 octets : `socle-batch` 8, `socle-resume` 7,
`socle-request` 31, `socle-handoff` 293 ; `AGENTS.md` de ce dépôt, 74 sur
16 000. Un lot de plus de 150 lignes qui change des textes du produit :
revue adversariale, note de version française et anglaise.

Les justifications sorties, quatre textes restent sous 600 octets de
marge, ce qui y reste ordonnant une règle (J-2026-11-26-BD) : Théo
choisit de relever le plafond des skills de 8 000 à 10 000 octets, ici
et dans le gabarit des garde-fous (D-0223, J-2026-11-26-BF), sur une
validation qui nomme la clé et les tests qu'il touche.

## Fait quand

- [ ] chaque skill du produit, en français et en anglais, laisse au moins 600 octets sous son plafond, relevé à 10 000 sur D-0223, et un test le mesure
- [ ] la clé du plafond des skills vaut 10 000 dans `.socle/guardrails.toml` et les deux gabarits des garde-fous, sur une validation de Théo qui nomme la clé et les tests touchés ; la note de version, française et anglaise, le dit
- [x] la section du socle d'`AGENTS.md` laisse au moins 600 octets sous le plafond de 16 000 de ce dépôt, en français et en anglais
- [x] chaque passage sorti se retrouve dans le guide, français et anglais, et aucune règle n'est perdue : la revue compare les règles avant et après
- [x] la note de version, française et anglaise, le dit
