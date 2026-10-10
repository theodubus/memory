<!-- socle: couche=demandes zone=publique -->
# D-0007 — Qui tient la liste des termes privés, et sous quelle forme ?

> date : 2026-10-10 · bloque : une pièce du jalon 7

## Décision demandée

Dans un projet à mémoire privée, qui a le droit d'ajouter et de retirer des
termes dans la liste des mots qui ne doivent jamais apparaître en public, et
sous quelle forme cette liste est-elle écrite ?

## Contexte

Le jalon 7 ajoute une mémoire privée, en option : des notes qui ne doivent
pas être publiques. L'agent lit tout, et peut recopier sans le vouloir un nom
privé (le nom de code d'une idée, d'un client, d'une piste) dans un fichier
public, un message de commit ou la description d'une pull request ; une fois
poussé sur un dépôt public, c'est définitif.

Le cadrage propose une liste de termes refusés : les contrôles la lisent et
refusent tout fichier ou message public qui contient l'un de ces termes. La
liste elle-même révèle ce qu'elle protège : elle vit donc du côté privé, et
un contributeur sans accès au privé ne peut pas faire ce contrôle (il est
signalé « indisponible », jamais sauté en silence). Les journaux de la CI
d'un dépôt public sont publics : en cas d'échec, ils ne donnent que le
fichier et la ligne, jamais le terme.

Une liste ne protège que ce qu'elle contient, et une reformulation passe :
c'est un filet pour les copies mot pour mot, pas une garantie. Reste à dire
qui la tient à jour, et comment elle s'écrit.

## Éléments cités

- B-0002@901e277f — le sujet du backlog qui porte le jalon 7, dont cette liste de termes refusés fait partie.

## Où regarder

- La piste et ses limites :
  [cadrage, section « Prévention des fuites par l'agent »](../archives/cadrage-2026-10-10.md#prévention-des-fuites-par-lagent--pistes-à-arbitrer-à-la-fabrication),
  première ligne du tableau, et la liste « Arbitrages à faire pendant la
  fabrication » en fin de section.
- Le mécanisme déjà en place pour les garde-fous, que l'option recommandée
  reprend (durcir est libre, assouplir exige ton accord) :
  [politique d'autonomie, point 1](../../AGENTS.md#politique-dautonomie-soclepolitiquetoml-modifiée-par-lhumain-seul).

Ce qu'il faut vérifier : que la répartition des droits te convient, et que la
forme proposée est assez simple pour que tu ajoutes un terme à la main.

## Options

- **L'humain seul tient la liste** : l'agent ne peut pas y écrire. Effort :
  tu ajoutes chaque terme toi-même ; risque : la liste prend du retard, car
  c'est l'agent qui écrit les notes privées et voit passer les noms
  nouveaux ; réversible.
- **L'agent ajoute librement, seul l'humain retire** : ajouter un terme
  durcit le contrôle, comme durcir un garde-fou, donc c'est libre ; en
  retirer un l'assouplit et exige une demande que tu valides. L'agent ajoute
  un terme quand il écrit une note privée qui introduit un nom. Effort
  faible ; risque : un terme trop courant qui bloque à tort, que tu fais
  retirer ; réversible.
- **Pas de liste** : les identifiants privés et la relecture seuls. Effort
  nul ; risque : un nom privé recopié tel quel part en public ; réversible.

La forme proposée, pour les deux premières options : un fichier texte du
côté privé, un terme par ligne, `#` pour un commentaire ; la recherche ignore
la casse et les accents et ne prend que des mots entiers ; une ligne qui
commence par `re:` est une expression régulière. Elle est lue sur les
fichiers publics modifiés, les messages de commit et les descriptions de
pull request.

## Conséquences

Si tu valides, je construis la liste sous cette forme, son contrôle au commit
et en CI, et la règle « ajout libre, retrait sur demande » dans le cliquet.
Si tu refuses, dis laquelle des autres options tu préfères, ou ce qui change
dans la forme. Sans réponse, je construis le reste du jalon 7 sans la liste,
et seuls les identifiants privés sont contrôlés.

## Recommandation

L'agent ajoute librement, seul l'humain retire. Vérifié : le cliquet des
garde-fous applique déjà cette asymétrie, et l'auto-test l'éprouve.
Supposé : que la recherche par mots entiers garde les faux positifs rares ;
à mesurer sur le projet d'essai du jalon.

## Réponses possibles

- `valider` — l'agent ajoute librement, seul l'humain retire, sous la forme proposée.
- `humain-seul` — seul l'humain écrit dans la liste.
- `aucune-liste` — pas de liste de termes ; les identifiants privés et la relecture seuls.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
