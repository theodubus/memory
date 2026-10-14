<!-- socle: couche=demandes zone=publique -->
# D-0026 — Laisser passer au hook, une seule fois, l'action externe qu'une demande validée nomme, et un push vers un dépôt local

> date : 2026-10-14 · lu : decisions@c92d474a

## Décision demandée

Choisir si le hook de l'agent laisse passer, une seule fois, une action
externe ou irréversible que tu as validée par une demande, et s'il cesse de
refuser un push vers un dépôt qui n'est qu'un dossier local.

## Contexte

La politique du projet dit qu'une action irréversible ou externe (push
forcé, push sur la branche par défaut, publication, suppression distante,
dépense) exige toujours une demande, et que le hook de l'agent la refuse.
Le hook refuse en effet, mais il refuse aussi après ta validation : il ne
lit pas les demandes. Le 12 oct., tu avais validé le push de l'historique
du projet d'échecs dans sa copie ; le hook a refusé `git push … main:main`,
et le push t'est revenu. Une validation ne sert donc qu'à t'en confier
l'exécution, même quand l'action est exactement celle que tu as lue.

Un second refus, voisin : le hook refuse un push vers la branche `main`
d'un dépôt d'origine qui n'est qu'un dossier local, comme les projets
jetables du banc. Ce n'est pas une publication, puisque rien ne quitte la
machine ; le refus large est le plus sûr, mais il bloque des essais sans
danger.

Ce qui changerait : une demande pourrait nommer la commande exacte (par
exemple `git push origin main:main`, et le dépôt visé) ; validée par toi,
elle laisserait passer cette commande-là, une fois, et le passage se
noterait pour ne pas servir deux fois. Toute autre commande, même voisine,
resterait refusée. Ce serait un assouplissement d'un garde-fou de la
politique : c'est à toi de le décider.

## Éléments cités

- B-0048@768cadea — le sujet du backlog : une action externe validée par une
  demande reste refusée par le hook, constaté le 12 oct.
- B-0018@6b28637e — le sujet voisin : le hook refuse un push vers la branche
  par défaut d'un dépôt d'origine qui n'est qu'un dossier local.
- D-0016@76d914c7 — ta demande validée du 12 oct., qui autorisait le push de
  l'historique du projet d'échecs dans sa copie, et que le hook a refusé
  quand même.
- J-2026-10-12-M@0e53508c — l'entrée du journal qui constate ce refus.

## Où regarder

- [ce que le hook juge irréversible](https://github.com/theodubus/memory/blob/e146ff693306b0345bec08ee16a2bd34097d9395/engine/socle/hooks.py#L303-L330) :
  la liste des actions refusées, dont le push sur la branche par défaut.
- [le refus lui-même](https://github.com/theodubus/memory/blob/e146ff693306b0345bec08ee16a2bd34097d9395/engine/socle/hooks.py#L474-L482) :
  il ne consulte aucune demande.
- [la règle de la politique](https://github.com/theodubus/memory/blob/e146ff693306b0345bec08ee16a2bd34097d9395/AGENTS.md#L119) :
  le point 4, « toujours une demande. Le hook la refuse ».

À vérifier : que l'assouplissement proposé te convient, et sur lequel des
deux refus.

## Options

- **Une fois, et le dépôt local** : une demande validée qui nomme la
  commande exacte la laisse passer une fois ; un push vers un dossier local
  n'est plus refusé. Effort : une journée environ, avec ses défauts
  injectés. Risque faible : seule la commande lue et validée passe, une
  seule fois, et un passage se voit dans la trace. Réversible : retirer
  la règle remet le refus.
- **Une fois seulement** : la première moitié, sans toucher au refus d'un
  push local. Effort et risque du même ordre ; réversible.
- **Le dépôt local seulement** : un push vers un dossier local n'est plus
  refusé ; tout le reste ne change pas. Effort faible ; risque faible ;
  réversible.
- **Rien** : le hook refuse comme aujourd'hui ; son message dit seulement
  que l'action revient à toi, avec sa commande. Effort faible ; aucun
  risque ; l'exécution des actions validées reste à toi.

## Conséquences

- Si tu valides une des trois premières options : je l'écris, avec un
  défaut injecté qui montre qu'une commande voisine reste refusée et
  qu'un second passage l'est aussi, puis je te dis ce que la politique
  devrait en dire.
- Si tu refuses : je n'écris que le message plus clair, et les deux sujets
  se closent avec ta raison.
- Sans réponse : rien ne change, et je passe au sujet suivant de l'ordre
  que tu as validé (ce qui reste en français dans un projet anglais).

## Recommandation

Une fois, et le dépôt local. Vérifié : le hook a refusé le push que tu
avais validé le 12 oct., et il ne lit aucune demande ; un push vers un
dossier local ne quitte pas la machine. Supposé : qu'une commande exacte,
lue dans la demande, suffit à ce que tu saches ce que tu autorises ; et
qu'un dépôt d'origine local se reconnaît sans erreur à son adresse (un
chemin, pas une URL).

## Réponses possibles

- `une-fois-et-local` — les deux assouplissements.
- `une-fois` — seulement l'action validée, une fois.
- `local` — seulement le push vers un dossier local.
- `rien` — le hook refuse comme aujourd'hui, avec un message plus clair.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
