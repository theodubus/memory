# La reprise sur « reprends » seul : spécification

Soumise à Théo le 25 novembre 2026, avant son code, par la demande de
T-0180. Elle répond à B-0346, sur les trois propositions que Théo a
retenues le 24 novembre (D-0177), et change la spécification de la
passation programmée validée par D-0174
(`docs/fabrication/passation-programmee-specification.md`) : ses
sections « Le prompt et sa garde » et « La session neuve » sont
remplacées par celles-ci ; les modes, le moment, les bornes et la pull
request ouverte ne changent pas.

## Ce qu'elle fait

Aujourd'hui, la session qui passe la main donne un prompt de neuf lignes
(`socle handoff prompt`) : l'humain le colle dans une session neuve, ou
la tâche programmée l'envoie. Il porte la garde, `socle handoff check`
et ses trois arguments, le lot et ce qui attend.

Désormais, la session qui part écrit sa passation dans le dépôt, la
commite et la pousse. La session neuve, d'un compte comme d'un autre,
n'a besoin que d'un mot : « reprends ». Elle trouve la passation, juge
sa garde, la reprend et la retire.

## La passation, un fichier du dépôt

`handoff.md`, sous `memory/`, une couche nouvelle du format (`couche=passation`),
publique. Un seul fichier, au plus, par branche :

```markdown
<!-- socle: couche=passation zone=publique -->
# Passation

> écrite : 2026-11-25T03:10:00Z · branche : ccr-6e3cd575-ol24kp · chaîne : 0

Ce qui attend : la CI du commit de tête.
```

L'heure change à chaque écriture : réécrite, la passation change
toujours le fichier, et le commit qui la réécrit compte. Elle ne porte
pas sa propre tête, qu'un fichier ne peut pas connaître : la garde la
lit dans git (plus bas). Ni le lot : la session neuve, une fois placée,
le lit dans l'état, calculé sur la même mémoire ; la passation ne nomme
ainsi rien qui puisse être privé, hors de ce qui attend, que les
contrôles de fuite jugent comme tout fichier public.

## L'écrire : `socle handoff write`

`socle handoff write` remplace `socle handoff prompt`, avec les mêmes
options (`--waiting`, `--scheduled`, `--chain`) et les mêmes refus : la
borne de la chaîne et le lot sans tâche prête, en session programmée.
Il écrit le fichier ; l'agent le commite en dernier, avec le reste du
rangement s'il veut, et pousse. Plus rien ne se pousse ensuite ; un
commit nécessaire après réécrit la passation dans ce même commit
(D-0177).

Le récap du mode « prompt à copier » ne donne plus de prompt : « Dans une
session neuve, écrivez « reprends » ». La tâche programmée de la
session programmée envoie « reprends » ; la session qu'elle réveille est
créée comme aujourd'hui (`source_revision`, `outcome_branch`, son modèle
et son effort).

## La trouver

Après `git fetch origin`, la passation en attente est celle du commit le
plus récent, toutes branches distantes confondues, qui touche
`handoff.md` :

- si le fichier existe à ce commit, une passation attend, sur la branche
  qu'il nomme ;
- s'il en est retiré, et que ce retrait n'est pas encore dans la
  branche par défaut, une autre session l'a reprise et y travaille : la
  garde refuse, en nommant sa branche et son heure ;
- s'il en est retiré, et que le retrait est dans la branche par défaut,
  ou si aucun commit ne le touche, aucune n'attend.

Une pull request fusionnée garde la passation dans la branche par
défaut jusqu'à ce qu'une session la retire : la règle du commit le plus
récent l'y voit reprise dès que le retrait est poussé, sur quelque
branche que ce soit.

## La garde : `socle handoff check`

Sans argument, la commande trouve la passation, puis juge sa garde comme
aujourd'hui, ses trois arguments tirés du dépôt (D-0177) :

- `--ref` : `origin/<la branche que nomme la passation>` ;
- `--head` : le dernier commit de cette branche qui a écrit
  `handoff.md` ; si la branche n'existe plus, celui de la branche
  par défaut, où la pull request l'a fusionné ;
- `--since` : la date de ce commit (D-0177).

Les refus sont ceux d'aujourd'hui : la branche a bougé depuis la
passation ; une autre branche porte, depuis, un commit qui touche
`memory/` sans venir de la passation ; la pull request a été fusionnée
par squash. Acceptée, la commande dit où se placer, la chaîne, ce qui
attend, et que le premier commit retire la passation.

Avec ses trois arguments, elle juge comme aujourd'hui : la reprise après
une limite d'usage (skill `socle-resume`) les lui donne toujours.

## Reprendre, ou rien à reprendre

Sur « reprends », comme premier message d'une session, l'agent lance
`git fetch origin` puis `python3 .socle/socle handoff check`.

- **Acceptée** : il se place où la garde le dit, et son premier commit
  retire `handoff.md`, poussé aussitôt : une autre session qui
  cherche ensuite la voit reprise, ou voit la mémoire écrite ailleurs et
  s'arrête (D-0177). La pull request ouverte de cette branche devient la
  sienne, comme aujourd'hui.
- **Refusée** : il ne fait rien d'autre que le dire, avec la raison,
  dont la passation déjà reprise par une autre session.
- **Aucune passation** : il fait ce que fait une session neuve, l'état,
  le chantier actif, le prochain lot, et son premier message dit
  qu'aucune passation n'attendait (D-0177).

« reprends » dans une session qui a déjà travaillé garde son sens
d'aujourd'hui : continuer le travail en cours, ou la reprise après une
limite (skill `socle-resume`).

La chaîne : la session que la tâche programmée réveille reprend celle de
la passation, plus un ; celle où l'humain écrit « reprends » repart de
zéro, comme le prompt collé aujourd'hui.

## Ce que dit l'état

Une ligne, d'après le clone tel qu'il est (l'état ne lance pas `git
fetch`) : `passation : en attente sur origin/<branche>, écrite à <heure>
— « reprends » la reprend` ; rien quand aucune n'attend. Le démarrage d'une session neuve la montre ; le hook de l'agent ne
change pas (ADR-0098).

## Modèle de menace

La garde est un garde-fou : elle empêche deux sessions de faire le même
travail.

**Ce qu'elle arrête, comme aujourd'hui.** Une session neuve dont la
branche a bougé depuis la passation ; une autre session qui a écrit la
mémoire du projet depuis ; une pull request fusionnée par squash. Et,
nouveau : une seconde session qui écrit « reprends » après que la
première a poussé son retrait.

**Ce qu'elle laisse passer.** Deux sessions qui écrivent « reprends »
dans la même minute, avant qu'aucune ait poussé son retrait : toutes
deux reprennent. Aujourd'hui, le même prompt collé deux fois fait de
même. Un retrait poussé sur une branche que le clone n'a pas rapatriée
(un `git fetch` partiel) : la passation y semble attendre encore, mais
la garde voit le commit qui touche la mémoire et refuse.

**Ce qu'elle ne voit pas.** Une passation que personne n'a poussée : la
session neuve ne la trouve pas, et fait ce que fait une session neuve.
Une passation laissée sans reprise, puis une autre écrite ailleurs : la
plus récente seule compte.

## Où cela s'écrit

- Le moteur : `socle handoff write` et `socle handoff check` sans
  argument (`engine/socle/handoff.py`, la ligne de commande), la ligne de
  l'état, la couche `passation` du format (`FORMAT.md`) et ses contrôles
  (un seul fichier, son en-tête, ses champs) ; les défauts injectés de
  la garde, dont un témoin sain par branche disparue, et ceux du prompt
  qui deviennent ceux de `write`.
- Les skills `socle-handoff` (« Programmer », « Le prompt à copier »,
  « La session neuve ») et `socle-batch` (« Changer de session »), en
  français et en anglais ; le gabarit d'`AGENTS.md` (« reprends » au
  démarrage) ; `HELP.md` ; une note de version.
- Dans ce dépôt, le skill `delegate-lot` (« Changer de session ») : le
  récap donne « reprends » au lieu du prompt.
- Les tests qui lisent le prompt ou la commande `handoff prompt`, que la
  demande nomme un à un, changent ou disparaissent.

## Non essayé

Vérifié par les tests de la tâche pour ce qui se teste avec git seul ;
le reste, au premier usage réel : qu'une session neuve d'un autre compte
rapatrie toutes les branches distantes, ce que le clone de ce dépôt fait
aujourd'hui (`+refs/heads/*:refs/remotes/origin/*`).
