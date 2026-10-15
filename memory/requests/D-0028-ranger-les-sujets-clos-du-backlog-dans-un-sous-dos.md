<!-- socle: couche=demandes zone=publique -->
# D-0028 — Ranger les sujets clos du backlog dans un sous-dossier

> date : 2026-10-15 · lu : decisions@9a83834a

## Décision demandée

Choisir si les sujets clos du backlog quittent le dossier des sujets
ouverts pour un sous-dossier, « memory/backlog/closed », où le moteur les
range lui-même.

## Contexte

Depuis le 13 oct., le backlog est un dossier, un fichier par sujet. Tu
avais validé qu'un sujet clos reste dans son fichier, à sa place : plus
d'archivage des sujets clos dans le journal, comme au format précédent.
Résultat aujourd'hui : `memory/backlog/` contient 39 fichiers, dont 25 clos
et 14 ouverts, mêlés dans l'ordre de leurs numéros. Tu demandes si cela ne
pollue pas, et si un sous-dossier ou un autre dossier ne vaudrait pas mieux.

Ce qui pollue, et pour qui. Pour l'agent, rien : il ne parcourt pas le
dossier, il lit l'index des sujets ouverts (`socle show --index backlog`)
et l'état, qui ne listent que les ouverts. Pour toi, oui : sur GitHub ou
dans un éditeur, la liste du dossier mêle les deux, et elle grossit à
chaque sujet clos.

Ce qu'un déplacement casserait. Un sujet se cite par son identifiant
(`B-NNNN`), que le moteur retrouve où qu'il soit. Les seuls liens écrits
vers des fichiers de sujets, dans ce dépôt, sont trois permaliens figés à
un commit, dans des demandes déjà répondues : ils restent valides. Un lien
relatif vers le fichier d'un sujet, s'il en existait un, deviendrait mort,
et le contrôle des références le dirait.

Qui rangerait. Pas l'agent à la main : le moteur. `socle archive`, qui ne
fait plus rien au format actuel, déplacerait chaque sujet clos dans
`closed/` (son pendant privé dans « private/backlog/closed ») ; un contrôle
refuserait un sujet clos laissé parmi les ouverts, ou un sujet ouvert
rangé avec les clos ; la mise à jour d'un projet existant ferait le
rangement une fois.

## Éléments cités

- ADR-0025@f97acbb5 — la décision du 13 oct. qui a fait du backlog un
  dossier, un fichier par sujet, et qui garde un sujet clos dans son fichier.
- D-0017@22c858f3 — ta demande validée qui l'a décidé : un dossier, plus
  d'archivage des sujets clos dans le journal, un plafond par sujet.

## Où regarder

- [la décision en vigueur](https://github.com/theodubus/memory/blob/d9e1ea9ebaf228d157905e23b5d8ebab6acec76c/memory/decisions/ADR-0025-le-backlog-un-fichier-par-sujet-format-3.md) :
  le point « Un sujet clos reste dans son fichier », que cette demande
  remplacerait.
- [la commande d'archivage](https://github.com/theodubus/memory/blob/d9e1ea9ebaf228d157905e23b5d8ebab6acec76c/engine/socle/archive.py#L15-L20) :
  au format actuel, elle s'arrête tout de suite ; c'est elle qui rangerait.
- [le dossier tel qu'il est](https://github.com/theodubus/memory/tree/d9e1ea9ebaf228d157905e23b5d8ebab6acec76c/memory/backlog) :
  les sujets ouverts et clos mêlés.

À vérifier : que le sous-dossier te convient mieux qu'un dossier voisin, et
le nom `closed` (les noms de dossiers sont en anglais).

## Options

- **Un sous-dossier « memory/backlog/closed », rangé par le moteur** :
  `socle archive` y déplace les sujets clos ; un contrôle refuse un sujet
  mal rangé, avec son défaut injecté à l'auto-test ; la mise à jour range
  les projets existants. Le backlog reste une seule couche de la mémoire.
  Effort : une demi-journée à une journée. Risque faible : les
  identifiants ne changent pas ; un lien relatif vers un sujet déplacé
  devient mort, et le contrôle des références le signale. Réversible : une
  migration inverse remet les fichiers à plat.
- **Un dossier voisin, « memory/backlog-closed »** : les mêmes mécanismes,
  mais une couche de plus dans l'arborescence de la mémoire et dans ses
  tables. Effort et risque du même ordre ; réversible.
- **Rien** : les sujets clos restent à leur place ; la liste du dossier
  reste mêlée pour toi, l'index et l'état restent propres pour l'agent.
  Effort nul ; aucun risque.

## Conséquences

- Si tu valides le sous-dossier ou le dossier voisin : j'écris une
  décision qui remplace ce point d'ADR-0025, le rangement, son contrôle et
  sa migration, et je range ce dépôt.
- Si tu refuses : rien ne bouge, et la décision du 13 oct. reste entière.
- Sans réponse : rien ne bouge ; je continue l'essai de la CI des
  adaptateurs, puis j'attends que tu me donnes la suite.

## Recommandation

Le sous-dossier `closed/`, rangé par le moteur. Vérifié : 25 des 39
fichiers sont clos ; les seuls liens écrits vers des fichiers de sujets
sont des permaliens, qui restent valides ; l'agent ne lit que l'index des
sujets ouverts. Supposé : qu'aucun projet installé n'écrit de lien relatif
vers le fichier d'un sujet (sinon le contrôle des références le signale à
sa mise à jour), et qu'un rangement par le moteur, plutôt qu'à la main,
suffit à ce que rien ne se mêle de nouveau.

## Réponses possibles

- `sous-dossier` — les sujets clos vont dans « memory/backlog/closed », rangés par le moteur.
- `dossier-voisin` — ils vont dans « memory/backlog-closed ».
- `rien` — ils restent à leur place.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
