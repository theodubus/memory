<!-- socle: couche=backlog zone=publique -->
# B-0256 — Le hook de l'agent ne suit ni l'état qu'un eval laisse, ni le dossier où s'appelle une fonction : la suppression du projet y passe

> statut : abandonné · origine : J-2026-11-16-C · priorité : haute · ref : J-2026-11-16-G · lu : backlog@b973ac90

Vus en corrigeant les trois bloquants de la seconde passe de la revue du
lot L-0004 (J-2026-11-16-C), voisins d'eux : le découpage
(`commands._analyser`) suit désormais l'appel d'une fonction dans un
`eval`, mais ni le reste de ce qu'un `eval` change, ni le dossier d'où
s'appelle une fonction. Vérifié sur bash, dans un dossier jetable : `eval`
s'exécute dans le shell courant, et le corps d'une fonction dans le
dossier de son appel.

- `eval "cd memory"; rm -rf ../../<racine>` passe le hook : le `cd` lu
  par l'`eval` ne vaut pas pour la suite (sa lecture part d'une copie de
  l'état) ; bash supprime le projet.
- `f() { rm -rf ../../<racine>; }; cd memory; f` passe : le corps se juge
  une fois, à sa définition, depuis le dossier où il s'écrit, et non
  depuis celui de son appel ; bash supprime le projet.

L'un et l'autre passaient avant le lot L-0004 (d1d296e) comme après.
`protege.fichiers` attrape ensuite l'écriture d'un fichier protégé par ces
formes (un risque accepté, D-0111) ; rien ne rattrape la suppression du
projet : ADR-0080 (sa première conséquence) ouvre ce sujet, de priorité
haute comme B-0250.

La piste : rendre inconnu, après un `eval`, ce que sa lecture change (le
dossier, puis chaque variable), comme après l'appel d'une fonction, ou
suivre l'état où sa lecture finit ; relire le corps d'une fonction à
chaque appel, depuis le dossier de l'appel, pour juger ce qu'il écrit ou
supprime par un chemin relatif.

Abandonné le 16 novembre selon D-0120 (J-2026-11-16-G) : ce qu'un `eval` change, et le corps d'une fonction jugé à sa définition, qu'aucun agent n'écrit dans son travail, va à la liste des formes connues que le hook ne juge pas (B-0261).

## Satisfait quand

- [ ] `eval "cd memory"; rm -rf ../../<racine>` et `f() { rm -rf ../../<racine>; }; cd memory; f` sont refusés par le hook, `eval "cd memory"; ls` et `f() { rm -rf build; }; f` passent, et un test le montre
- [ ] le corps d'une fonction se juge à son appel, avec les fonctions connues alors : `g() { f; rm -rf ../../<racine>; }; f() { cd memory; }; g`, et ses variantes par une substitution ou un `eval` dans le corps, sont refusés (J-2026-11-16-F), et un test le montre
