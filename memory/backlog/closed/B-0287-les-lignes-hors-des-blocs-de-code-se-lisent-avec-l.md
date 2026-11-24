<!-- socle: couche=backlog zone=publique -->
# B-0287 — Les lignes hors des blocs de code se lisent avec les clôtures de CommonMark : un bloc ~~~ qui contient ``` ne fait plus lire le reste du fichier comme du code

> statut : abandonné · origine : J-2026-11-18-R · lu : backlog@7a9bcd93 · ref : D-0168

Relevé à la correction des bloquants de la passe 1 de L-0016
(J-2026-11-18-R), défaut voisin non corrigé dans le lot (politique,
point 6). `lignes_hors_code` (`engine/socle/memory.py`) bascule dedans
ou dehors à chaque ligne de clôture, quel qu'en soit le caractère ou la
longueur : un bloc ouvert par ~~~ qui contient une ligne ``` se croit
fermé, et la suite du bloc se lit comme du texte ; le bloc suivant
inverse alors tout le reste du fichier. Les contrôles qui s'en servent
(les références et les liens de la mémoire) y voient du code comme du
texte, et du texte comme du code : un lien cassé écrit après n'est plus
signalé. Le hook de fin de tour lit déjà les clôtures au sens strict
(ADR-0089, `engine/socle/human.py`).

Abandonné le 24 novembre 2026 par D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`), sous « X2 — imaginé par un relecteur, jamais vu, rattrapé ou bénin » : un bloc de code ouvert par `~~~` qui contient ```` ``` ```` fausse la lecture des liens ; jamais vu. Il revient s'il est vu en usage réel.

## Satisfait quand

- [ ] un texte où un bloc ~~~ contient une ligne ``` est lu par les contrôles de la mémoire comme CommonMark le rend : le bloc entier est du code, la suite du texte n'en est pas
