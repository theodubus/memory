<!-- socle: couche=demandes zone=publique -->
# D-0009 — Faire tourner le banc du jalon 9 sur des sessions Claude Code de ton compte, avec quel plafond ?

> date : 2026-10-10 · reformulée : 2026-10-11 · bloque : la porte du jalon 9

## Décision demandée

Autoriser que je lance, depuis ce conteneur, des sessions de Claude Code non
interactives sur ton compte pour le banc du jalon 9, chacune arrêtée à un
plafond de consommation, et fixer ce plafond.

## Contexte

Le jalon 9 se termine par un banc d'essai sur un agent réel : six scénarios
qui mesurent le comportement d'un agent équipé du socle, pas seulement
l'installation. Sa porte : les six scénarios passent. Les voici :

1. un agent sans contexte reprend après un compactage et retrouve l'état
   exact du projet ;
2. une doc périmée est corrigée par l'agent avant qu'il conclue ;
3. une faute injectée est attrapée par au moins un étage ;
4. une tentative d'assouplir un plafond est bloquée et escaladée ;
5. une demande humaine écrite par l'agent est autonome et complète ;
6. une initialisation depuis chacune des entrées (cadrage seul, rien, dépôt
   existant, cadrage et dépôt) ne produit aucun fait sans source.

Chaque scénario prépare un projet jetable, lance un agent dessus avec une
consigne, puis un script juge le résultat (fichiers, mémoire, trace des
hooks) et relève les mesures du cadrage : défauts attrapés par étage, faux
positifs, durée de la vérification, jetons consommés au démarrage.

L'agent, c'est Claude Code lui-même, présent dans ce conteneur et connecté à
ton compte Claude. Ce ne sont pas des appels facturés à l'API : chaque
session consomme l'usage de ton abonnement, comme celles que tu lances
toi-même. Claude Code chiffre chaque session en équivalent dollars, et
accepte un plafond exprimé dans cette unité, qui arrête la session net. Les
montants ci-dessous sont cet équivalent, pas une facture. Une seule réserve :
si ton compte a l'usage supplémentaire payant activé au-delà des limites de
l'abonnement, ce qui les dépasse serait facturé ; je ne peux pas le voir
d'ici. Le scénario 6 attend le jalon 8, qui est fait.

## Éléments cités

- B-0004@d731c8c9 — le sujet du backlog qui porte le jalon 9 : les six scénarios du cadrage et leurs mesures.
- F-0003@83695111 — le fait mesuré que les hooks de Claude Code se chargent dans la session qui les installe : ce que le banc exploite pour équiper l'agent dès sa première action.

## Où regarder

- Les six scénarios et les mesures :
  [cadrage, section « Auto-tests du dispositif et banc d'évaluation »](../archives/cadrage-2026-10-10.md#auto-tests-du-dispositif-et-banc-dévaluation),
  la liste numérotée sous le tableau.
- La règle qui réserve une dépense à l'humain :
  [politique d'autonomie, point 4](../../AGENTS.md#politique-dautonomie-soclepolitiquetoml-modifiée-par-lhumain-seul).

Ce qu'il faut vérifier : que le plafond proposé te convient, et que ton
compte n'a pas d'usage supplémentaire payant que ces sessions pourraient
entamer.

## Options

- **Trois passages par scénario** : 18 sessions, chacune arrêtée à
  l'équivalent de 2 dollars, 36 au plus pour tout le banc, pris sur l'usage
  de ton abonnement. Effort nul pour toi ; risque : un usage borné, qui peut
  te rapprocher des limites de l'abonnement ; trois passages montrent si un
  résultat se répète ; l'usage consommé ne se rend pas, le reste est
  réversible.
- **Un passage par scénario** : 6 sessions, l'équivalent de 12 dollars au
  plus. Effort nul ; risque : un succès ou un échec isolé ne dit pas s'il
  se répète ; l'usage consommé ne se rend pas.
- **Tu lances le banc toi-même** : je fournis le script et la commande.
  Effort : une commande, sur ta machine, quand tu veux ; risque : faible,
  tu vois chaque session tourner ; réversible.
- **Pas d'agent réel** : je simule l'agent par un script. Effort nul ;
  risque : la porte du jalon 9 n'est pas franchie au sens du cadrage ;
  réversible, le vrai banc reste possible plus tard.

## Conséquences

Si tu valides, je lance les 18 sessions, je m'arrête à la première qui
atteint son plafond, et je te donne ce que chacune a consommé, lu dans sa
sortie. Si tu refuses toute consommation (`simule`), le banc tourne sur un
agent simulé et la porte du jalon 9 reste ouverte. Pour `une-fois` ou
`moi-meme`, je fais ce que l'option décrit. Sans réponse, je prépare le banc
et son script, je le fais tourner sur un agent simulé, et je ne lance
aucune session.

## Recommandation

Trois passages par scénario, à l'équivalent de 2 dollars par session.
Vérifié : la commande `claude` de ce conteneur est connectée par un jeton
OAuth de ton compte, chez Anthropic directement (`claude auth status`), et
aucune clé d'API n'est présente ici ; elle accepte un plafond par session
(`--max-budget-usd`) et une sortie qui donne la consommation. Supposé : que
ce plafond s'applique de même sur un compte d'abonnement ; ce que consomme
une session de scénario, que je ne saurai qu'à la première.

## Réponses possibles

- `valider` — trois passages par scénario, chacun plafonné à l'équivalent de 2 dollars.
- `une-fois` — un passage par scénario, même plafond.
- `moi-meme` — je fournis le script, tu lances le banc toi-même.
- `simule` — pas d'agent réel ; le banc tourne sur un agent simulé.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
