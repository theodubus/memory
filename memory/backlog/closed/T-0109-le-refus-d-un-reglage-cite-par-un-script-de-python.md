<!-- socle: couche=backlog zone=publique -->
# T-0109 — Le refus d'un réglage cité par un script de python dit qui le cite et le remède, et le guide et une note de version disent qu'une mention ou une lecture est refusée

> statut : abandonné · origine : commit:3e83907e · ref : D-0143 · besoin : B-0307 · lu : backlog@aa725b6b

Un commit : le constat `reglage` que pose `_cites`
(`engine/socle/hooks.py`) dit « cité par `{qui}` » et le remède (un
réglage se lit par `cat`, un fichier qui le nomme s'écrit par l'outil
d'écriture), comme le constat `protege` ; la même phrase dans le guide
(`engine/socle/HELP.md`, `HELP.en.md`) et une note de version.

Abandonné le 20 novembre par D-0143 (ADR-0098) : le hook de l'agent est terminé, et cette entrée ne cite aucune preuve vue dans une session.

## Fait quand

- [ ] le refus de `python3 -c "print(open('.claude/settings.json').read())"` dit « cité par `python3 -c` » et le remède, et un test le montre
- [ ] le guide dit qu'un script de python qui cite un réglage ou un fichier protégé, même pour le lire, est refusé, et comment faire autrement
