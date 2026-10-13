<!-- socle: couche=demandes zone=publique -->
# D-0018 — Déclarer le projet d'échecs comme dépôt cité

> date : 2026-10-13

## Décision demandée

Déclarer le dépôt du projet d'échecs, sous le nom `chess`, parmi les dépôts
cités de ce dépôt (`[references] repos` des garde-fous), pour que ses
chemins cités sous la forme `chess:chemin` ne soient plus signalés.

## Contexte

Le contrôle des références de la mémoire laissait passer toute forme
`x:chemin` sans rien vérifier, sur le modèle de `depot:chemin` qui sert à
citer un fichier d'un autre dépôt : à l'essai sur la copie du projet
d'échecs, l'agent a ainsi écrit `<rustine>.patch:<chemin>`, que rien n'a
regardé. Depuis le correctif du 13 octobre, un dépôt cité se déclare dans
les garde-fous ; un dépôt non déclaré est signalé, en avertissement et une
seule fois par dépôt. En déclarer un est un assouplissement (ses chemins
échappent alors au contrôle, puisqu'ils vivent ailleurs) : le cliquet
l'exige validé par toi, comme une exclusion. Ce dépôt cite le projet
d'échecs 51 fois (l'inventaire de ce qui en a été repris, le relevé de
l'essai sur sa copie, le journal) : chaque vérification, à chaque fin de
tour, au commit et en CI, porte donc cet avertissement. Je ne peux pas
écrire la déclaration sans ta réponse.

## Éléments cités

- **Le correctif du contrôle des références** (sujet de backlog B-0052@ec465313) :
  ce qui précède `:` dans un chemin cité doit être un dépôt déclaré ; une
  URL, une référence de la mémoire ou une révision de git n'en sont pas.
- **L'avertissement actuel** : « dépôt « chess » non déclaré, 51 chemin(s)
  cité(s) que rien ne vérifie ».
- **Les garde-fous de ce dépôt** : la section `[references]`, qui dit déjà
  quels fichiers sont lus et lesquels sont exclus.

## Où regarder

- [le contrôle, `depot_non_declare`](https://github.com/theodubus/memory/blob/0aa518c64d5988b105d376c6dad465fa10e5f42a/moteur/socle/controles_memoire.py#L344) :
  vérifier que seul ce qui précède `:` est jugé, et qu'une URL, une
  référence ou une révision de git n'en sont pas.
- [les garde-fous de ce dépôt, section `[references]`](https://github.com/theodubus/memory/blob/0aa518c64d5988b105d376c6dad465fa10e5f42a/.socle/guardrails.toml#L29) :
  là où s'ajouterait `repos = ["chess"]`.
- [le relevé de l'essai sur la copie](https://github.com/theodubus/memory/blob/0aa518c64d5988b105d376c6dad465fa10e5f42a/docs/essai-chess.md) : le constat 5, et
  l'une des citations `chess:…` qui portent l'avertissement.
- [le sujet B-0052 au backlog](https://github.com/theodubus/memory/blob/0aa518c64d5988b105d376c6dad465fa10e5f42a/memory/backlog.md#b-0052--la-forme-depotchemin-échappe-au-contrôle-des-références) :
  ce qui a été constaté à l'essai.

## Options

- **Déclarer `chess`** : j'ajoute `repos = ["chess"]` aux garde-fous, en
  citant ta réponse. Effort nul ; risque : un chemin `chess:…` faux ne sera
  pas vu, ce qui était déjà le cas avant le correctif ; réversible en
  retirant la ligne.
- **Laisser tel quel** : l'avertissement reste, sans rien bloquer. Effort
  nul ; il encombre chaque vérification.
- **Réécrire les 51 citations en liens vers le dépôt du projet d'échecs** :
  effort moyen ; un lien vers un autre dépôt n'est pas vérifié non plus ;
  réversible.

## Conséquences

- Si tu valides : je déclare `chess`, l'avertissement disparaît, et un
  autre préfixe (`x.patch:`) reste signalé.
- Si tu refuses : l'avertissement reste à chaque vérification.
- Sans réponse : rien ne change, et je continue sur L6.

## Recommandation

Déclarer `chess`. Vérifié : les 51 chemins signalés sont tous de la forme
`chess:…` ; l'avertissement ne bloque rien ; la déclaration ne retire aucun
contrôle sur les fichiers de ce dépôt. Supposé : que tu préfères le nom
court `chess` à celui du dépôt sur GitHub, `theodubus/chess`.

## Réponses possibles

- `declarer` — j'ajoute `chess` aux dépôts cités, en citant ta réponse.
- `laisser` — l'avertissement reste.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
