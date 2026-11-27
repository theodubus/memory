<!-- socle: couche=backlog zone=publique -->
# T-0211 — Les refus des lectures, des fichiers protégés et des écrivains qui citent un chemin protégé disent leur correction

> statut : ouvert · origine : J-2026-11-27-U · besoin : B-0372 · ref : D-0235 · lu : backlog@4d53be09

Les messages de `memoire.lectures` et du hook de l'agent, et
l'exemption de la consigne née dans la plage, selon le modèle de menace de
son besoin.

## Fait quand

- [ ] un test montre le refus d'une consigne citée sans empreinte, qui donne l'empreinte à citer
- [ ] un test montre qu'une consigne créée dans la plage jugée s'y cite sans empreinte, et qu'une consigne d'avant la plage reste refusée sans elle
- [ ] des tests lisent les deux lignes ajoutées aux messages du hook
- [ ] le défaut injecté et le témoin sain de l'exemption sont dans `engine/socle/selftest.py`, et la note de version est écrite
