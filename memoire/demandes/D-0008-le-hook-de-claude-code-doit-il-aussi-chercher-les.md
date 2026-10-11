<!-- socle: couche=demandes zone=publique -->
# D-0008 — Le hook de Claude Code doit-il aussi chercher les fuites de privé ?

> date : 2026-10-10 · bloque : une pièce du jalon 7

## Décision demandée

Dans un projet à mémoire privée, le hook que Claude Code appelle avant chaque
action doit-il refuser une écriture publique qui contient du privé, en plus
des hooks git et de la CI, sachant que cette protection-là ne vaut que pour
Claude Code ?

## Contexte

Le jalon 7 ajoute une mémoire privée, en option. L'agent lit tout et peut
recopier du privé (un identifiant d'entrée privée, un terme de la liste des
termes privés) dans ce qu'il publie. Trois endroits peuvent le chercher :

- **le hook de l'agent**, avant chaque écriture de fichier, commande ou appel
  à GitHub : il n'existe que pour Claude Code, et un autre agent ne l'a pas ;
- **les hooks git**, avant chaque commit : ils valent pour tout agent et tout
  humain, mais ne voient que les fichiers et le message du commit, et
  `--no-verify` les contourne en local ;
- **la CI** : rien ne la contourne, mais elle tourne après le push ; sur un
  dépôt public, ce qui est poussé est déjà publié, et elle ne fait que
  constater.

Les descriptions de pull request et les commentaires passent par l'API de
GitHub, pas par git : ni les hooks git ni la CI ne les voient avant leur
publication. Seul le hook de l'agent les voit, au moment où l'agent les
écrit. Le cadrage hésite parce que cette protection lie le socle à Claude
Code ; le moteur, lui, reste le même pour tous.

## Éléments cités

- B-0002@901e277f — le sujet du backlog qui porte le jalon 7, dont les contrôles de fuite font partie.

## Où regarder

- La piste et sa limite :
  [cadrage, section « Prévention des fuites par l'agent »](../archives/cadrage-2026-10-10.md#prévention-des-fuites-par-lagent--pistes-à-arbitrer-à-la-fabrication),
  troisième ligne du tableau, et le dernier des « Arbitrages à faire pendant
  la fabrication ».
- Ce que le hook de l'agent refuse déjà (identifiants inventés, actions
  irréversibles, écriture de fichiers protégés) :
  [instructions du dépôt, « Ce qui tourne tout seul »](../../AGENTS.md#ce-qui-tourne-tout-seul).

Ce qu'il faut vérifier : que l'ajout d'une protection propre à Claude Code te
va, tant que les hooks git et la CI restent la base commune à tous les
agents.

## Options

- **Oui, en plus des hooks git et de la CI** : le hook refuse une écriture
  hors de la zone privée, un message de commit, une description de pull
  request ou un commentaire qui contient un identifiant privé ou un terme de
  la liste. Effort nul pour toi ; risque : un autre agent n'a pas cette
  couche, il garde les hooks git et la CI ; réversible, la couche se retire
  sans toucher au reste.
- **Non, les hooks git et la CI seuls** : effort nul ; risque : une
  description de pull request ou un commentaire qui contient du privé est
  publié sans qu'aucun contrôle l'ait vu ; réversible.

## Conséquences

Si tu valides, j'ajoute la recherche de fuites au hook de l'agent, avec un
défaut injecté par type d'écriture dans l'auto-test, et j'ajoute aussi un
hook git sur le message de commit, pour les autres agents. Si tu refuses, je
n'ajoute que le hook git sur le message de commit. Sans réponse, je construis
le reste du jalon 7 sans cette couche.

## Recommandation

Oui, en plus des hooks git et de la CI. Vérifié : le hook de l'agent lit déjà
chaque écriture et chaque commande pour y chercher des identifiants inventés,
l'auto-test l'éprouve, et c'est le seul étage qui voit une description de
pull request avant sa publication. Supposé : que le coût en temps du hook
reste négligeable avec une liste de quelques centaines de termes.

## Réponses possibles

- `valider` — le hook de l'agent cherche aussi les fuites, en plus des hooks git et de la CI.
- `refuser` — pas de recherche de fuites dans le hook de l'agent ; les hooks git et la CI seuls.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
