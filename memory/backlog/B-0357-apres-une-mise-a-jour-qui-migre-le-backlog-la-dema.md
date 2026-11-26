<!-- socle: couche=backlog zone=publique -->
# B-0357 — Après une mise à jour qui migre le backlog, la demande seule ne se commite ni ne se pousse sans contournement : les hooks git la jugent avec le moteur neuf de l'arbre de travail

> statut : ouvert · origine : J-2026-11-26-AA · ref : B-0323, ADR-0098 · lu : backlog@35e9325c

La gêne 1 de la mise à jour de chess du 26 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-26.md`) : en session cloud,
l'installeur fait commiter la demande seule, puis les fichiers protégés
(B-0148). Le hook avant commit l'a refusée : il juge l'index avec le
moteur de l'arbre de travail, le neuf, qui refuse ce que la mise à jour
n'a pas encore commité, le backlog à l'ancien format (`memoire.formes`)
et l'ancien chantier actif (`memoire.budgets`) ; le hook avant push de
même sur le dernier commit. Chess l'a contourné par `git stash
--include-untracked`, `git commit --only`, le push, puis `git stash
pop`. De plus, la migration du backlog met ses renommages dans l'index
(`git add` dans `migration.migrer_backlog`) : un commit de la demande les
emporte, et `git stash --keep-index` les y laisse.

C'est la preuve qu'ADR-0098 demande : un refus à tort qui a bloqué un
vrai travail dans une session.

La conception retenue, réversible, s'écrit en ADR dans le lot : la
migration ne met plus rien dans l'index (T-0200) ; dans un projet
installé dont la copie du moteur, dans l'arbre de travail, diffère de
celle du dernier commit, une mise à jour pas encore commitée, les hooks
avant commit et avant push jugent avec le moteur neuf, mais ne refusent
que les constats que le commit ou le push apporte, ceux que le même
moteur trouve aussi dans l'arbre d'où il part (le dernier commit, la
base) s'écartant (T-0201). En mode amont, rien ne change.

## Modèle de menace

Le garde-fou qui change : les hooks git avant commit et avant push, le
temps d'une mise à jour pas encore commitée. Ce qu'ils arrêtent : un
commit ou un push qui apporte un défaut que l'agent n'a pas vu. Ce qui
reste arrêté : tout constat nouveau. Ce qui passe : un constat déjà
présent dans l'arbre d'où part le commit, qui y était déjà commité ; la
CI juge chaque commit poussé avec le moteur qu'il contient, et le commit
qui pose le moteur neuf avec ce moteur, sur tout l'arbre. Un agent qui
laisserait une copie modifiée du moteur pour relâcher les hooks
contournerait le socle (X1) : la copie du moteur est protégée, et
`protege.fichiers` la refuse en CI sans demande validée.

## Satisfait quand

- [ ] après une mise à jour qui migre le backlog, la demande seule se commite et se pousse par `git add` sur son fichier, `git commit` et `git push`, sans stash ni `--only`, et les fichiers de la mise à jour se commitent ensuite
