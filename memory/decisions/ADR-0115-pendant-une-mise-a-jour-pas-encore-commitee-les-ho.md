<!-- socle: couche=decisions zone=publique -->
# ADR-0115 — Pendant une mise à jour pas encore commitée, les hooks git avant commit et avant push ne refusent que les constats que le commit ou le push apporte

> statut : acceptée · date : 2026-11-26 · source : B-0357@e9aa1964, ADR-0098@3081a5ed, B-0148@cb313256, T-0200@1729de24 · lu : decisions@e50c2b18

## Contexte

La gêne 1 de la mise à jour de chess du 26 novembre (B-0357@e9aa1964) :
en session cloud, la mise à jour fait commiter et pousser la demande
seule, puis les fichiers protégés (B-0148@cb313256). Le hook avant commit
de git l'a refusée : il juge l'index avec le moteur de l'arbre de
travail, le neuf, qui refuse ce que la mise à jour n'a pas encore
commité, le backlog à l'ancien format (`memoire.formes`) et l'ancien
chantier actif (`memoire.budgets`) ; le hook avant push de même, sur le
dernier commit. Chess l'a contourné par un stash et `git commit --only`.
C'est la preuve qu'ADR-0098@3081a5ed demande pour toucher aux hooks : un
refus à tort qui a bloqué un vrai travail dans une session. T-0200@1729de24 a déjà
retiré de l'index les renommages de la migration.

## Décision

1. **Une mise à jour en cours** : dans un projet installé, hors du mode
   amont, la copie du moteur (le dossier `engine_dir` du verrou) diffère,
   dans l'arbre de travail, de celle du dernier commit (`git status
   --porcelain` sur ce dossier, fichiers non suivis compris).
2. Pendant une mise à jour en cours, le hook avant commit qui trouve à
   refuser juge aussi le dernier commit, avec le même moteur et contre la
   même base ; une erreur de l'index qui s'y trouve aussi (même contrôle,
   même chemin, même message, autant de fois) s'écarte. Le hook avant
   push de même, sur le commit qui part, en jugeant la base elle-même.
   Les constats de la plage poussée, qui comparent à une base, et les
   étapes rapides de l'adaptateur ne changent pas.
3. Quand il en écarte, le hook le dit en une ligne : une mise à jour du
   moteur est en cours, et les constats déjà commités sont laissés à la
   CI ; il le dit aussi quand il refuse pour un constat nouveau.
4. Hors d'une mise à jour, en mode amont, sans dernier commit ou sans
   base, rien ne change.

Écartées : juger avec le moteur du dernier commit, qu'il faudrait
extraire, et que la CI applique déjà à ce commit ; couper les hooks
pendant la mise à jour, qui laisserait passer un constat nouveau.

## Modèle de menace

Celui de B-0357@e9aa1964. Le garde-fou qui change : les hooks git avant
commit et avant push, le temps d'une mise à jour pas encore commitée. Ce
qui reste arrêté : tout constat que le commit ou le push apporte. Ce qui
passe : un constat déjà dans l'arbre d'où le commit part ; la CI juge
chaque commit poussé avec le moteur qu'il contient, et le commit qui pose
le moteur neuf avec lui, sur tout l'arbre. Un agent qui laisserait une
copie modifiée du moteur pour relâcher les hooks n'obtient que cela, et
la copie est protégée : `protege.fichiers` la refuse en CI sans demande
validée.

## Conséquences

Le hook qui refuse pendant une mise à jour lance ses contrôles deux fois.
Le moteur qui juge est celui de l'arbre : la mise à jour qui apporte ce
changement en profite déjà. Se défait en retirant le second jugement des
deux hooks (`hooks.git_pre_commit`, `hooks.git_pre_push`).
