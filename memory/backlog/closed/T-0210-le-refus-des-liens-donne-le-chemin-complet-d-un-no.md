<!-- socle: couche=backlog zone=publique -->
# T-0210 — Le refus des liens donne le chemin complet d'un nom nu, et le message qui ne corrige que les liens d'un récap refusé n'a pas à le redire

> statut : fait · origine : J-2026-11-27-U · besoin : B-0371 · ref : D-0235, J-2026-11-27-X · lu : backlog@4d53be09

Le refus des liens de la fin de tour (`links.problemes`,
`engine/socle/hooks.py`), selon le modèle de menace de son besoin.

## Fait quand

- [x] un test montre le refus d'un nom nu qui désigne un seul fichier suivi, avec son chemin complet, et celui d'un nom qui en désigne plusieurs ou aucun, qui dit de l'écrire sans accents graves
- [x] un test montre qu'un dernier message sans récap passe quand le message refusé du même tour l'était pour ses seuls liens et portait le récap, et qu'il reste refusé sinon
- [x] le défaut injecté et le témoin sain de ce qui passe désormais sont dans `engine/socle/selftest.py`
- [x] la section installée dit la règle des liens en une phrase positive, et la note de version est écrite
