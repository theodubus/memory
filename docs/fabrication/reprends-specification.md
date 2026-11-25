# La reprise sur une demande de reprendre : spécification

Soumise à Théo le 25 novembre 2026, avant son code, par la demande de
T-0180. Elle répond à B-0346, sur les trois propositions que Théo a
retenues le 24 novembre (D-0177), et change la passation programmée
validée par D-0174 : dans sa spécification
(`docs/fabrication/passation-programmee-specification.md`), « Le prompt
et sa garde » est remplacé par ce qui suit, et le prompt de « La
façon » devient le texte de la tâche programmée (plus bas) ; dans le
skill `socle-handoff`, « Le prompt à copier » et « La session neuve ».
Les modes, le moment, les bornes et la pull request ouverte ne changent
pas ; le compte de la chaîne change seulement de support.

Théo l'a validée le 25 novembre (D-0190) avec une réserve
(J-2026-11-25-J, J-2026-11-25-K) : la reprise part sur toute demande de
reprendre ou de continuer, quelle qu'en soit la forme, pas sur le seul
mot « reprends », qui n'en est qu'un exemple. Ce texte l'applique.

## Ce qu'elle fait

Aujourd'hui, la session qui passe la main donne un prompt de neuf lignes
(`socle handoff prompt`) : l'humain le colle dans une session neuve, ou
la tâche programmée l'envoie. Il porte la garde, `socle handoff check`
et ses trois arguments, le lot et ce qui attend.

Désormais, la session qui part écrit sa passation dans le dépôt, la
commite et la pousse. La session neuve, d'un compte comme d'un autre,
n'a besoin que d'une demande de reprendre, quelle qu'en soit la forme :
« reprends », « continue », « reprends les travaux ». Elle trouve la
passation, juge sa garde, la reprend et la retire. Le mode « prompt à
copier » de ce dépôt (D-0173) reste : son prompt devient cette demande,
sans rien à recopier de la passation.

## La passation, un fichier du dépôt

`handoff.md`, sous `memory/`, une couche nouvelle du format
(`couche=passation`), publique, un seul fichier par branche au plus :

```markdown
<!-- socle: couche=passation zone=publique -->
# Passation

> écrite : 2026-11-25T03:10:00Z · branche : ccr-6e3cd575-ol24kp · chaîne : 0

Ce qui attend : la CI du commit de tête.
```

**Son estampille**, l'heure `écrite` et la `branche`, l'identifie : pas
le commit qui la porte, que la fusion d'une pull request par squash ou
par rebase remplace par un autre, plus récent. Réécrite, la passation
reçoit une heure nouvelle : le fichier change toujours, et le commit qui
la réécrit compte. Elle ne porte pas le lot : la session neuve, une fois
placée, le lit dans l'état, calculé sur la même mémoire ; la passation
ne nomme ainsi rien qui puisse être privé, hors de ce qui attend, que
les contrôles de fuite jugent comme tout fichier public.

## L'écrire : `socle handoff write`

`socle handoff write` remplace `socle handoff prompt`, avec les mêmes
options (`--waiting`, `--scheduled`, `--chain`) et, en session
programmée, les mêmes refus : la borne de la chaîne, le lot sans tâche
prête. Il écrit le fichier ; l'agent le commite en dernier, avec le
reste du rangement s'il veut, et pousse. Plus rien ne se pousse
ensuite ; un commit nécessaire après réécrit la passation dans ce même
commit (D-0177). Quand l'agent fusionne sa pull request, la passation
est dans son dernier commit, avant la fusion : la branche ne repart pas
seule après (`socle-batch`, « Livrer »).

Le push fait, la session qui part lance elle-même `socle handoff check`
sans argument et doit y retrouver sa passation, en attente ; sinon elle
ne programme rien et le dit. C'est ce qui remplace le refus d'une tête
non poussée de `prompt` : la commande refuse quand le clone porte une
passation que l'origine n'a pas, non commitée ou non poussée, ou suivie
d'un commit qui n'est sur aucune branche distante, ou quand un fichier
suivi a un changement non commité.

Le récap du mode « prompt à copier » dit de demander la reprise dans une
session neuve, « reprends » par exemple : n'importe quelle formulation
convient. La tâche programmée envoie un texte distinct, « reprends —
session programmée » : la session qu'elle réveille sait ainsi que la
demande ne vient pas de l'humain (la chaîne, plus bas). La session
programmée est créée comme aujourd'hui (`source_revision`,
`outcome_branch`, son modèle et son effort).

## La trouver

Après `git fetch --prune origin` (sans `--prune`, une branche supprimée
sur l'origine reste dans le clone, et la pull request fusionnée par
squash ou par rebase se refuse comme aujourd'hui) :

- **Les passations connues** : le fichier `handoff.md` à la tête de
  chaque branche distante, la branche par défaut comprise, et celui
  qu'un commit d'une branche distante a retiré. Celle dont l'heure
  `écrite` est la plus récente est la passation ; aucune, aucune
  n'attend.
- **Reprise** : une branche distante porte un commit qui retire un
  `handoff.md` de la même estampille. Si ce retrait n'est pas encore
  dans la branche par défaut, une session l'a reprise et y travaille :
  la garde refuse, en nommant sa branche et son heure. S'il y est,
  aucune n'attend.
- **Sinon**, elle attend, sur la branche que nomme son estampille.

Une pull request fusionnée porte la passation dans la branche par
défaut, sous la même estampille, jusqu'à ce qu'une session la retire :
le retrait, sur quelque branche que ce soit, la dit reprise, quel que
soit le commit qui l'a portée dans la branche par défaut. Le retrait
compte aussi quand la session qui reprend le pousse sur la branche même
de la passation, dont la tête ne la porte alors plus.

## La garde : `socle handoff check`

Sans argument, la commande trouve la passation, puis juge sa garde comme
aujourd'hui, ses trois arguments tirés du dépôt (D-0177) :

- `--ref` : `origin/<la branche de l'estampille>` ;
- `--head` : le dernier commit de cette branche qui a écrit cette
  estampille ; si la branche n'existe plus, le commit de la branche par
  défaut qui l'y a portée : celui de la passation après un commit de
  fusion, le commit de squash ou de rebase sinon ;
- `--since` : l'heure `écrite`, qui précède de peu la date du commit de
  la passation, celle que retient D-0177 ; jamais la date d'une fusion,
  qui laisserait passer la mémoire écrite ailleurs entre la passation et
  la fusion.

Les refus sont ceux d'aujourd'hui : la branche a bougé depuis la
passation ; une autre branche porte, depuis l'heure `écrite`, un commit
qui touche `memory/` sans venir de la passation. S'y ajoute la
passation déjà reprise (plus haut). Un cas change : la pull request
fusionnée par squash ou par rebase, sa branche supprimée, que la garde
refuse aujourd'hui faute de retrouver la tête nommée ; le commit qui
porte la passation dans la branche par défaut devient la tête, et la
session y repart. La mémoire écrite ailleurs depuis l'heure `écrite` la
fait toujours refuser : encore sur une autre branche, comme aujourd'hui ;
déjà fusionnée dans la branche par défaut avant ce squash ou ce rebase,
donc ancêtre de la tête, parce que la garde juge alors aussi les
ancêtres de la tête qui touchent `memory/`, écrits (date d'auteur, que
le rebase garde) après l'heure `écrite`, hors du commit qui porte la
passation. Les commits du lot, rejoués par le rebase, ont été écrits
avant cette heure ; ceux d'une autre session, après. Acceptée, la commande dit où se placer, la
chaîne, ce qui attend, et que le premier commit retire la passation.

Avec ses trois arguments, elle juge comme aujourd'hui : la reprise après
une limite d'usage (skill `socle-resume`) les lui donne toujours.

## Reprendre, ou rien à reprendre

Sur tout premier message d'une session neuve qui demande de reprendre
ou de continuer le travail, quelle qu'en soit la forme (« reprends »,
« continue », « reprends les travaux »), l'agent lance `git fetch
--prune origin` puis `python3 .socle/socle handoff check`. Aucun contrôle ne
lit le message de l'humain : c'est l'agent qui reconnaît la demande ;
le mot « reprends » n'en est qu'un exemple, dans le récap, l'état et
le gabarit d'`AGENTS.md`.

- **Acceptée** : il se place où la garde le dit, et son premier commit
  retire `handoff.md`, poussé aussitôt (D-0177). La pull request ouverte
  de cette branche devient la sienne, comme aujourd'hui.
- **Refusée** : il ne fait rien d'autre que le dire, avec la raison,
  dont la passation déjà reprise par une autre session.
- **Aucune passation** : il fait ce que fait une session neuve, l'état,
  le chantier actif, le prochain lot, et son premier message dit
  qu'aucune passation n'attendait (D-0177).

La même demande dans une session qui a déjà travaillé garde son sens
d'aujourd'hui : continuer le travail en cours, ou la reprise après une
limite (skill `socle-resume`).

**La chaîne**, qui borne les lots menés sans message de l'humain
(D-0174) : la session réveillée par « reprends — session programmée »
prend celle de la passation, plus un ; un premier message autre, tapé
par l'humain, la remet à zéro, comme le prompt collé aujourd'hui. Dans
le doute, la chaîne de la passation, plus un : la borne ne cède pas.

## Ce que dit l'état

Une ligne, d'après le clone tel qu'il est (l'état ne lance pas `git
fetch`) : `passation : en attente sur origin/<branche>, écrite à
<heure> — une demande de reprendre (« reprends ») la reprend` ; rien
quand aucune n'attend. Le démarrage d'une session neuve la montre ; le
hook de l'agent ne change pas (ADR-0098).

## Modèle de menace

La garde est un garde-fou : elle empêche deux sessions de faire le même
travail.

**Ce qu'elle arrête, comme aujourd'hui.** Une session neuve dont la
branche a bougé depuis la passation ; une autre session qui a écrit la
mémoire du projet depuis. Et, nouveau : une seconde session qui demande
de reprendre après que la première a poussé son retrait, tant que ce
retrait n'est pas entré dans la branche par défaut.

**Ce qu'elle laisse passer.**

- Deux sessions qui demandent de reprendre avant qu'aucune ait poussé
  son retrait, du `git fetch` au push : toutes deux reprennent. Le
  même prompt collé deux fois fait de même aujourd'hui.
- Une seconde demande de reprendre après que le retrait est entré dans
  la branche par défaut, la pull request de la session qui a repris
  fusionnée pendant qu'elle travaille encore : aucune passation
  n'attend, et elle fait ce que fait une session neuve, comme une
  session ouverte sans prompt aujourd'hui. La fenêtre va de cette
  fusion à la passation suivante.
- La pull request fusionnée par squash ou par rebase, sa branche
  supprimée, que la garde refusait : la session repart de la branche
  par défaut. Des commits poussés sur la branche après la passation,
  absorbés par le squash, ne se voient plus ; leur travail est dans la
  branche par défaut, d'où la session repart.

**Ce qu'elle ne voit pas.** Une passation que personne n'a poussée : la
session qui part la cherche elle-même après son push, et le dit. Une
passation laissée sans reprise, puis une autre écrite ailleurs : la
plus récente seule compte.

## Où cela s'écrit

- Le moteur : `socle handoff write` et `socle handoff check` sans
  argument (`engine/socle/handoff.py`, la ligne de commande), la ligne de
  l'état, la couche `passation` du format (`FORMAT.md`) et ses contrôles
  (un seul fichier, son en-tête, ses champs). Les défauts injectés de la
  garde sans argument : la passation déjà reprise ; le squash dont une
  autre branche a écrit la mémoire depuis l'heure `écrite` ; le témoin
  sain du squash, sa branche supprimée. Ceux du prompt deviennent ceux
  de `write` et de la vérification après le push.
- Les skills `socle-handoff` (« Programmer », « Le prompt à copier »,
  « La session neuve ») et `socle-batch` (« Changer de session »), en
  français et en anglais ; le gabarit d'`AGENTS.md` (la reprise sur une
  demande de reprendre, au démarrage) ; `HELP.md` ; une note de version.
- Dans ce dépôt, le skill `delegate-lot` (« Changer de session ») : le
  récap dit de demander la reprise (« reprends », par exemple) au lieu
  de donner le prompt.
- Les tests qui lisent le prompt ou la commande `handoff prompt`, que la
  demande nomme un à un, changent ou disparaissent.

## Non essayé

Vérifié par les tests de la tâche pour ce qui se teste avec git seul ;
le reste, au premier usage réel : qu'une session neuve d'un autre compte
rapatrie toutes les branches distantes, ce que le clone de ce dépôt fait
aujourd'hui (`+refs/heads/*:refs/remotes/origin/*`).
