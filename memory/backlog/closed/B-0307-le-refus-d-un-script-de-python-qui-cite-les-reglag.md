<!-- socle: couche=backlog zone=publique -->
# B-0307 — Le refus d'un script de python qui cite les réglages de Claude Code ne dit ni qu'il les cite ni comment faire autrement, et le guide ne dit pas qu'une simple mention les fait refuser

> statut : abandonné · origine : commit:3e83907e · ref : D-0143 · lu : backlog@aa725b6b

Relevé par la passe 1 de la revue de L-0019, sur le commit relu, et
rencontré par l'orchestrateur du lot : depuis T-0001 (ADR-0094), un
heredoc donné à python qui écrit un fichier du projet dont le texte
nomme le fichier des réglages partagés de Claude Code, ou qui le lit
pour en extraire une valeur, est refusé, comme un `python -c` l'était
déjà (B-0206). Le refus est voulu : un script qui cite un réglage en
toutes lettres peut l'écrire. Mais son message ne dit que « les réglages
de Claude Code commandent ses hooks, seul l'humain les modifie », ni
qu'il vient d'une simple citation par le script, ni le remède, quand le
refus d'un autre fichier protégé dit « cité par … » et « se lit par
`cat` » ; et ni le guide ni la note de version 2026-11-19-p ne disent
à un projet installé qu'une mention ou une lecture est refusée. Ce
dépôt cite ces réglages partout. Refuser moins, ne juger que les
littéraux qui atteignent une écriture, s'écarterait du modèle « cité en
toutes lettres » : hors de ce besoin.

Abandonné le 20 novembre par D-0143 (ADR-0098) : le hook de l'agent est terminé, et cette entrée ne cite aucune preuve vue dans une session.

## Satisfait quand

- [ ] le refus d'un réglage de Claude Code cité par un script de python dit qui le cite et comment faire autrement, et le guide le dit
