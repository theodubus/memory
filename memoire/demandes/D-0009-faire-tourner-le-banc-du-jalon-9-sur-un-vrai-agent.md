<!-- socle: couche=demandes zone=publique -->
# D-0009 — Faire tourner le banc du jalon 9 sur un vrai agent, avec quelle dépense ?

> date : 2026-10-10 · bloque : la porte du jalon 9

## Décision demandée

Autoriser que je lance, depuis ce conteneur, des sessions de Claude Code en
mode non interactif pour le banc du jalon 9, à tes frais, et fixer le
plafond de dépense.

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

L'agent, ce serait Claude Code lui-même, présent dans ce conteneur, en mode
non interactif. Chaque session consomme des jetons, que tu paies : c'est une
dépense, que la politique d'autonomie réserve à ta décision. La commande
accepte un plafond de dépense par session, qui l'arrête net. Le scénario 6
attend le jalon 8, que je fais d'abord.

## Éléments cités

- B-0004@d731c8c9 — le sujet du backlog qui porte le jalon 9 : les six scénarios du cadrage et leurs mesures.
- F-0003@83695111 — le fait mesuré que les hooks de Claude Code se chargent dans la session qui les installe : ce que le banc exploite pour équiper l'agent dès sa première action.

## Où regarder

- Les six scénarios et les mesures :
  [cadrage, section « Auto-tests du dispositif et banc d'évaluation »](../archives/cadrage-2026-10-10.md#auto-tests-du-dispositif-et-banc-dévaluation),
  la liste numérotée sous le tableau.
- La règle qui réserve une dépense à l'humain :
  [politique d'autonomie, point 4](../../AGENTS.md#politique-dautonomie-soclepolitiquetoml-modifiée-par-lhumain-seul).

Ce qu'il faut vérifier : que le plafond proposé te convient, et que la
manière de compter (par session, et en tout) est celle que tu veux.

## Options

- **Trois passages par scénario, plafonnés** : 18 sessions, chacune arrêtée
  à 2 dollars au plus, 36 dollars au pire pour tout le banc. Effort nul pour
  toi ; risque : la dépense, bornée ; trois passages montrent si un
  résultat se répète ; irréversible pour la dépense, réversible pour le
  reste.
- **Un passage par scénario** : 6 sessions, 12 dollars au pire. Moins cher ;
  risque : un succès ou un échec isolé ne dit pas s'il se répète.
- **Tu lances le banc toi-même** : je fournis le script et la commande ;
  la dépense passe par ton propre compte, sur ta machine, quand tu veux.
- **Pas d'agent réel** : je simule l'agent par un script. Gratuit, mais la
  porte du jalon 9 n'est alors pas franchie au sens du cadrage.

## Conséquences

Si tu valides, je lance les 18 sessions après le jalon 8, je m'arrête à la
première qui dépasse son plafond, et je te donne le coût réel lu dans la
sortie de chaque session. Si tu refuses toute dépense (`simule`), le banc
tourne sur un agent simulé et la porte du jalon 9 reste ouverte. Pour
`une-fois` ou `moi-meme`, je fais ce que l'option décrit. Sans réponse, je
prépare le banc et son script, je le fais tourner sur un agent simulé, et je
ne lance aucune session payante.

## Recommandation

Trois passages par scénario, plafonnés à 2 dollars par session. Vérifié : la
commande de Claude Code présente ici accepte un plafond de dépense par
session (`--max-budget-usd`) et une sortie qui donne l'usage. Supposé : le
coût réel d'une session de scénario, que je ne connais pas avant la
première ; et que la session lancée d'ici est facturée au même compte que
celle-ci.

## Réponses possibles

- `valider` — trois passages par scénario, plafonnés à 2 dollars par session.
- `une-fois` — un passage par scénario, même plafond.
- `moi-meme` — je fournis le script, tu lances le banc toi-même.
- `simule` — pas d'agent réel ; le banc tourne sur un agent simulé.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
