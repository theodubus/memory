<!-- socle: couche=backlog zone=publique -->
# B-0199 — La conduite d'un lot dans le produit : sous-agents, revue, intégration, fusion, une session par lot, seuils de consommation, passation

> statut : fait · origine : J-2026-11-13-F · ref : J-2026-11-14-Z · priorité : haute · lu : backlog@225764b5

Théo, le 13 novembre : « Tout ce qui est utile doit intégrer le socle »
(J-2026-11-13-F). Ce dépôt mène ses lots par une procédure à lui, le skill
`.claude/skills/delegate-lot/SKILL.md`, que l'installeur ne pose pas :
annoncer le lot, un sous-agent par sujet dans un worktree, la revue sans
contexte avant tout push, l'intégration et la renumérotation des
collisions, l'attente de la CI (« success sur <sha court> »), la fusion
par l'agent, puis le rangement. S'y ajoutent ce que B-0173 a mesuré et
écrit (`docs/fabrication/consommation.md`) : une session par lot, au plus
deux sous-agents, aucun au-delà des seuils de la fenêtre, et le
changement de session avec le prompt de la suivante ; et ce que le
13 novembre a montré : un commit pas encore relu sauvé en correctif avant
de passer la main.

Les consignes de Théo qui valent pour tout projet en font partie (un lot
par session, une limite proche qui change l'ordre et jamais la
profondeur, un réveil pour toute attente annoncée) ; ses préférences
propres restent à la couche des consignes (B-0161). C'est la première
pièce de B-0162 (la proposition 7 de D-0093), que la consigne du 13 rend
voulue ; le skill de ce dépôt se réduit ensuite à ce qui lui est propre.

Le 13 novembre, Théo retient la priorité haute proposée (D-0108@96eeead5) :
le sujet fait partie de ceux à finir avant de revenir aux nouvelles
fonctions.

Le 14 novembre, Théo demande d'apprendre à l'atelier et au socle à
traiter ensemble les sujets qui se traitent facilement ensemble
(J-2026-11-14-M) ; les lots ne vivaient alors que dans la prose du
chantier actif. Former un lot fait partie de sa conduite : réunir les
sujets prêts qui touchent les mêmes fichiers, le même garde-fou ou les
mêmes tests, une seule revue les jugeant ensemble ; et garder le lot dans
la mémoire, relié à ses sujets, pour que l'état le montre et qu'une
session neuve le retrouve.

Le 14 novembre (J-2026-11-14-U, ADR-0079) : les lots sont dans la
mémoire (`forme : lot`) et l'état montre le prochain. Le skill du
produit, `socle-batch`, est écrit, mais le poser change la valeur
attendue de deux tests qui comptent les skills du socle : il attend,
avec la copie protégée de ce dépôt, une demande validée.

La revue du lot 2 (J-2026-11-14-X) : le premier critère dit
« l'auto-test » ; ce qui vérifie que le skill est posé et protégé est un
test du moteur, `tests/test_skills.py` (`TestLaConduiteDUnLot`), comme
pour les autres skills du socle. L'auto-test injecte des défauts aux
contrôles, et poser un skill n'en est pas un.

## Satisfait quand

- [x] l'installeur pose un skill du socle qui conduit un lot, ses règles de consommation et le changement de session compris, et l'auto-test vérifie qu'il est posé et protégé
- [x] `.claude/skills/delegate-lot/SKILL.md` ne garde que ce qui est propre à ce dépôt
- [x] un lot se forme des sujets prêts qui touchent les mêmes fichiers, garde-fou ou tests ; la mémoire le relie à ses sujets, l'état montre le prochain, et un test le montre
