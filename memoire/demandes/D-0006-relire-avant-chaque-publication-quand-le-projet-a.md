<!-- socle: couche=demandes zone=publique -->
# D-0006 — Relire avant chaque publication quand le projet a une mémoire privée ?

> date : 2026-10-10 · bloque : une pièce du jalon 7

## Décision demandée

Dans un projet qui a une mémoire privée, faut-il qu'un humain relise ce que
l'agent s'apprête à publier sur le dépôt public avant que ce soit poussé, et
si oui, à chaque push ou par lots ?

## Contexte

Le jalon 7 ajoute une mémoire privée, en option : des notes du projet qui ne
doivent pas être publiques (idées, motivations, pistes abandonnées). Elles
vivent soit dans un dépôt privé à côté du dépôt public, soit chiffrées dans
le dépôt public.

L'agent lit tout, le privé compris. Il peut donc en recopier un morceau dans
ce qu'il publie : un message de commit, un commentaire de code, la
description d'une pull request. Sur un dépôt public, ce qui est poussé y
reste, même supprimé ensuite (forks, caches). Et une branche poussée est
publique tout de suite, bien avant sa fusion : relire à la fusion est trop
tard.

Les contrôles automatiques n'attrapent qu'une copie mot pour mot : un
identifiant d'entrée privée (contrôle déjà en place), ou un terme d'une
liste de termes privés (l'objet d'une autre demande, posée en même temps).
La même idée reformulée passe tous les scripts. Seule une relecture humaine
avant la publication l'attrape ; elle coûte du temps à chaque fois.

La question ne concerne que les projets qui choisissent une mémoire privée.
Sans elle, rien ne change, et ce dépôt-ci n'en a pas.

## Éléments cités

- B-0002@901e277f — le sujet du backlog qui porte le jalon 7 : les deux modes de mémoire privée, le verrou du dépôt privé, la liste de termes refusés, le signal « mémoire privée indisponible », et les arbitrages sur les fuites que voici.

## Où regarder

- Le problème des fuites et les pistes, dont celle-ci :
  [cadrage, section « Prévention des fuites par l'agent »](../archives/cadrage-2026-10-10.md#prévention-des-fuites-par-lagent--pistes-à-arbitrer-à-la-fabrication),
  ligne « Relecture humaine avant chaque push public », et la liste
  « Arbitrages à faire pendant la fabrication » en fin de section.
- Les deux modes de mémoire privée :
  [cadrage, section « Mode dépôt compagnon »](../archives/cadrage-2026-10-10.md#mode-dépôt-compagnon)
  et la suivante.

Ce qu'il faut vérifier : que le risque d'une reformulation publiée vaut, pour
toi, le temps d'une relecture.

## Options

- **Aucune relecture obligatoire** : les contrôles automatiques seuls.
  Effort nul ; risque : une reformulation de privé part en public, sans
  retour possible ; réversible, la relecture s'active plus tard.
- **Relecture à chaque push** : le hook de l'agent et le hook git avant push
  refusent de pousser vers le dépôt public tant que l'humain n'a pas approuvé
  le commit exact (une commande, réservée à l'humain comme les autres
  approbations). Effort : une relecture par push, plusieurs par jour ;
  risque : la lassitude, qui fait approuver sans lire ; réversible.
- **Relecture par lots, sur une branche non publiée** : même mécanisme, mais
  l'agent accumule ses commits sans les publier et demande une relecture
  quand un lot est prêt. Effort : une relecture par lot ; risque : le travail
  n'est pas visible sur le dépôt public avant la relecture. En mode dépôt
  privé, la branche peut vivre dans le dépôt privé, où tu la vois sur
  GitHub ; en mode chiffré, il n'y a pas d'endroit privé sur GitHub, et tu
  relis le diff que l'agent montre dans la conversation. Réversible.

## Conséquences

Si tu valides, je construis la relecture par lots : un réglage de la
politique, actif par défaut dans les projets à mémoire privée, et le refus du
push vers le dépôt public tant que le dernier commit n'est pas approuvé. Si
tu refuses, dis laquelle des autres options tu préfères. Sans réponse, je
construis le reste du jalon 7 sans cette pièce, et rien ne bloque la
publication au-delà des contrôles automatiques.

## Recommandation

La relecture par lots. Vérifié : le contrôle des identifiants privés existe
et l'auto-test l'éprouve ; aucun contrôle ne voit une reformulation, le
cadrage le dit et rien dans le moteur ne le contredit. Supposé : qu'une
relecture par lot reste assez légère pour être vraiment faite ; à mesurer
au jalon 9, sur un agent réel.

## Réponses possibles

- `valider` — relecture par lots sur une branche non publiée, active par défaut avec une mémoire privée.
- `chaque-push` — relecture obligatoire avant chaque push vers le dépôt public.
- `aucune` — pas de relecture obligatoire ; les contrôles automatiques seuls.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
