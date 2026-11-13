<!-- socle: couche=backlog zone=publique -->
# B-0199 — La conduite d'un lot dans le produit : sous-agents, revue, intégration, fusion, une session par lot, seuils de consommation, passation

> statut : ouvert · origine : J-2026-11-13-F · priorité : haute · lu : backlog@225764b5

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

## Fait quand

- [ ] l'installeur pose un skill du socle qui conduit un lot, ses règles de consommation et le changement de session compris, et l'auto-test vérifie qu'il est posé et protégé
- [ ] `.claude/skills/delegate-lot/SKILL.md` ne garde que ce qui est propre à ce dépôt
