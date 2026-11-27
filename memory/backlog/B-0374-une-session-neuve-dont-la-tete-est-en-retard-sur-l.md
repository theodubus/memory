<!-- socle: couche=backlog zone=publique -->
# B-0374 — Une session neuve dont la tête est en retard sur la passation qui l'attend ne le sait pas : l'état injecté ne le dit pas

> statut : ouvert · origine : J-2026-11-27-U · ref : D-0235 · lu : backlog@4d53be09

Chez chess (`docs/fabrication/chess/cout-et-frictions-2026-11-26.md`, §7), le 26 au soir, une session programmée a
démarré sur un commit vieux de trois heures, ses instructions, ses skills
et ses hooks compris ; il a fallu une session sonde. Ici, le 27 novembre,
une session est partie de `main` quand la passation portait un commit
plus récent : l'état injecté donnait un chantier actif périmé, sans dire
l'écart, que seule la garde a montré (`docs/fabrication/chess/relecture-cout-et-frictions-2026-11-27.md`).

Retenu par Théo le 27 novembre (D-0235, point 4) : quand une passation
attend et que la tête locale est un ancêtre strict de sa référence,
l'état le dit en tête, avec les fichiers d'instructions, de skills et de
hooks qui changent entre les deux ; le skill de passation fait lire ce
diff avant tout travail. L'état n'écrit rien.

## Satisfait quand

- [ ] quand une passation attend sur une référence dont la tête locale est un ancêtre strict, l'état le dit en tête, avec les fichiers d'instructions, de skills et de hooks qui changent entre les deux
- [ ] sans écart, l'état n'en dit rien
- [ ] le skill de passation fait lire ce diff avant tout travail
