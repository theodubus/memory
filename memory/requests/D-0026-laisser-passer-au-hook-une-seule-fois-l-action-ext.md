<!-- socle: couche=demandes zone=publique -->
# D-0026 — Laisser passer au hook, une seule fois, l'action externe qu'une demande validée nomme, et un push vers un dépôt local

> date : 2026-10-14 · lu : decisions@c92d474a

## Décision demandée

Choisir si le hook de Claude Code qui refuse mes actions externes laisse
passer, une seule fois, une action que tu as validée par une demande, et sur
quelle preuve de ta validation ; et s'il cesse de refuser un push vers la
branche `main` d'un dépôt qui n'est qu'un dossier du conteneur. Réécrite
après tes questions du 14 oct. : ma recommandation a changé.

## Contexte

Trois gardes s'appliquent à un push que je lance ; une seule est en cause :

- le hook `PreToolUse` de Claude Code lit chacune de mes commandes avant
  qu'elle s'exécute, et refuse les actions irréversibles ou externes : push
  forcé, push sur la branche par défaut, suppression d'une branche distante,
  publication, fusion d'une pull request (par `gh` comme par mon outil
  GitHub). C'est lui que cette demande assouplirait ;
- le hook git `pre-push` lance `verify --fast` et juge la plage qui part
  comme la CI la jugera, pour tout push, vers GitHub comme vers un dossier.
  Il ne change pas ;
- la CI de GitHub tourne à chaque push vers GitHub. Elle ne change pas.

Premier refus. La politique dit qu'une action externe exige toujours une
demande, et que le hook la refuse. Il refuse aussi après ta validation : il
ne lit pas les demandes. Le 12 oct., tu avais validé le push de l'historique
du projet d'échecs dans sa copie ; le hook a refusé `git push … main:main`,
et le push t'est revenu.

Ce que prouve une réponse relayée. Ta réponse, donnée dans la conversation,
c'est moi qui l'écris dans le dépôt (`socle answer … --relayed
--quote-file`), avec ton texte tel que je le recopie. Ni les hooks ni la CI
ne lisent la conversation, et sur GitHub j'agis sous ton compte : la pull
request que j'ai ouverte pour la langue du projet, celle que tu as fusionnée
le 14 oct., porte `theodubus` comme auteur, comme tes propres gestes. Rien
de vérifiable par une machine ne distingue donc ta réponse d'une réponse que
j'aurais mal relayée ou inventée. Aujourd'hui, une telle réponse n'aboutit
qu'à un commit, que tu vois dans le diff avant de fusionner : c'est
réversible. Si elle suffisait à débloquer une action externe, l'action
partirait aussitôt, avant toute relecture. Seule, une réponse relayée
protège d'une erreur (une commande voisine, un second passage), pas d'une
réponse mal relayée.

Une preuve que je ne peux pas fabriquer : ta fusion. Le hook me refuse la
fusion d'une pull request et tout push sur `main`. Une demande et sa réponse
présentes sur la branche `main` de GitHub y sont donc arrivées par une
fusion de ta main, après que tu as pu les lire dans le diff. Le hook
pourrait l'exiger, en demandant à GitHub où en est `main` plutôt qu'à la
copie locale, que je peux réécrire. Le prix : une fusion par action
validée, faisable depuis ton téléphone, mais qui amène aussi sur `main` tout
le travail de la branche.

Une limite commune : une session dont les hooks de l'agent ne sont pas
chargés ne refuse rien du tout. Aucune option ne la couvre ; seule la
consigne de ne rien pousser, que l'état rappelle depuis B-0060.

Second refus. Le hook refuse aussi un push vers la branche `main` d'un dépôt
d'origine qui n'est qu'un dossier du conteneur, comme ceux des projets
jetables. « Local » veut dire cela : une adresse qui est un chemin sur la
machine où je travaille, pas une URL. Seul ce refus-là serait levé : push
forcé et suppression resteraient refusés, et un push vers GitHub ne
changerait en rien. Le gain est mince : les bancs poussent par leurs propres
scripts, que ce hook ne voit pas, et le refus n'a gêné qu'une fois, le
10 oct., pour un push fait à la main. Le risque n'est pas nul : un dossier
local peut être le dépôt du projet lui-même (un push y déplacerait sa
branche `main`), ou un dossier réseau monté.

## Éléments cités

- B-0048@768cadea — le sujet du backlog : une action externe validée par une
  demande reste refusée par le hook, constaté le 12 oct.
- B-0018@6b28637e — le sujet voisin : le hook refuse un push vers la branche
  par défaut d'un dépôt d'origine qui n'est qu'un dossier local.
- D-0016@76d914c7 — ta demande validée du 12 oct., qui autorisait le push de
  l'historique du projet d'échecs dans sa copie, et que le hook a refusé
  quand même.
- J-2026-10-12-M@0e53508c — l'entrée du journal qui constate ce refus.
- B-0060@dbb8bbfe — le sujet, fait, qui fait dire à l'état et refuser au
  commit une session dont les hooks de l'agent ne sont pas chargés.

## Où regarder

- [ce que le hook de Claude Code juge irréversible](https://github.com/theodubus/memory/blob/e146ff693306b0345bec08ee16a2bd34097d9395/engine/socle/hooks.py#L303-L330) :
  la liste des commandes refusées, dont le push sur la branche par défaut,
  quelle que soit la destination.
- [les outils GitHub qu'il me refuse](https://github.com/theodubus/memory/blob/e146ff693306b0345bec08ee16a2bd34097d9395/engine/socle/hooks.py#L42-L45) :
  dont la fusion d'une pull request.
- [le refus lui-même](https://github.com/theodubus/memory/blob/e146ff693306b0345bec08ee16a2bd34097d9395/engine/socle/hooks.py#L474-L482) :
  il ne consulte aucune demande.
- [ce qu'il exige d'une réponse relayée](https://github.com/theodubus/memory/blob/e146ff693306b0345bec08ee16a2bd34097d9395/engine/socle/hooks.py#L496-L504) :
  le drapeau `--relayed` et une citation, rien qui prouve que le texte est
  le tien.
- [le hook git avant push](https://github.com/theodubus/memory/blob/e146ff693306b0345bec08ee16a2bd34097d9395/engine/socle/hooks.py#L1075-L1107) :
  il vérifie tout push, quelle que soit sa destination, et n'est pas en
  cause.
- [la règle de la politique](https://github.com/theodubus/memory/blob/e146ff693306b0345bec08ee16a2bd34097d9395/AGENTS.md#L119) :
  le point 4, « toujours une demande. Le hook la refuse ».

À vérifier : que tu acceptes, ou non, une preuve de validation autre que ton
propre geste, et laquelle.

## Options

- **Une fois, après ta fusion** : une demande validée qui nomme la commande
  exacte la laisse passer une fois, si la demande et ta réponse sont sur la
  branche `main` de GitHub ; le passage se note pour ne pas resservir.
  Effort : une journée environ, avec ses défauts injectés (une commande
  voisine, un second passage, une réponse absente de `main`, une copie
  locale de `main` réécrite). Risque faible : la preuve est ton geste ; une
  fusion faite sans lire validerait quand même. Sans réseau, le hook ne
  peut pas interroger GitHub, et refuse. Réversible : retirer la règle
  remet le refus.
- **Une fois, sur réponse relayée** : la même chose, sans exiger ta fusion.
  Effort du même ordre. Risque moyen : une réponse mal relayée ou inventée
  débloquerait l'action avant ta relecture. Réversible pour la règle, pas
  pour une action déjà partie.
- **Le dépôt local** : un push vers la branche `main` d'un dépôt d'origine
  qui est un chemin du conteneur n'est plus refusé, sauf vers le dépôt du
  projet lui-même. Se combine avec l'une des deux précédentes. Effort
  faible ; risque faible ; gain mince ; réversible.
- **Rien** : le hook refuse comme aujourd'hui ; son message dit qu'une
  validation ne débloque pas l'action, et je te donne la commande exacte,
  où la lancer et ce qu'elle doit produire. Effort faible ; aucun risque ;
  chaque action validée, tu la fais toi-même, sur une machine qui a ton
  accès.

## Conséquences

- Si tu valides une option « une fois » : je l'écris, avec ses défauts
  injectés, puis je te propose le texte que le point 4 de la politique
  devrait prendre ; toi seul le modifies.
- Si tu valides « le dépôt local » : je l'écris, avec un défaut injecté qui
  montre qu'un push vers GitHub, et vers le dépôt du projet, reste refusé.
- Si tu réponds `rien` : je n'écris que le message plus clair, et B-0048 et
  B-0018 se closent avec ta raison.
- Sans réponse : rien ne change ; je termine l'essai de la CI des
  adaptateurs sur ton dépôt jetable, puis je passe à ce qui reste en
  français dans un projet anglais.

## Recommandation

Rien, pour l'instant. Vérifié : une réponse relayée est écrite par moi, et
rien ne la distingue de la tienne ; sur GitHub j'agis sous ton compte ; le
hook me refuse la fusion d'une pull request ; une seule action validée a été
refusée en cinq jours (le 12 oct.), et le refus vers un dossier local n'a
gêné qu'une fois. Supposé : que les actions externes validées restent
rares. Si elles deviennent fréquentes, « une fois, après ta fusion » est la
seule option qui garde ton geste pour preuve. Je ne recommande pas « une
fois, sur réponse relayée » : elle ôterait la seule garantie qui ne dépend
pas de moi.

## Réponses possibles

- `une-fois-apres-fusion` — l'action validée passe une fois, si la demande et ta réponse sont sur `main`.
- `une-fois-apres-fusion-et-local` — la même chose, et le push vers un dossier du conteneur.
- `une-fois` — l'action validée passe une fois, sur réponse relayée.
- `local` — seulement le push vers un dossier du conteneur.
- `rien` — le hook refuse comme aujourd'hui, avec un message plus clair.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
