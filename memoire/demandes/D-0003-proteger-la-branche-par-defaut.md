<!-- socle: couche=demandes zone=publique -->
# D-0003 — Puis-je ouvrir une pull request volontairement défectueuse vers `main`, pour prouver que GitHub en bloque la fusion ?

> date : 2026-10-10 · réécrite après ton retour du 10 oct. · bloque : la porte du jalon 5

## Décision demandée

M'autoriser à ouvrir une pull request de démonstration, défectueuse exprès,
puis à la fermer sans la fusionner — une fois le check de CI exigé sur `main`
comme décrit ci-dessous.

## Contexte

La porte du jalon 5 du cadrage est : « la CI bloque une pull request
défectueuse ». Le socle n'est incontournable que si GitHub refuse de
fusionner quand sa CI échoue ; sinon un push ou une fusion passe outre.

Tu as protégé `main`. Il reste à dire à GitHub QUEL check doit passer : sans
« required status checks », une pull request à la CI rouge reste fusionnable.
Le dépôt n'a qu'un workflow, « Socle », avec un seul job. Dans Settings →
Branches → la règle de `main` → « Require status checks to pass before
merging », chercher et cocher ce check, au nom exact :

`Socle — verify, contrôles, auto-test`

GitHub ne le propose que s'il a tourné récemment sur le dépôt : c'est le cas,
il a tourné à chaque push de la branche de travail. Deux autres réglages
utiles : « Require a pull request before merging » (pas de push direct sur
`main`), et « Do not allow bypassing the above settings » si tu veux que la
règle s'applique aussi à toi.

Un réglage à éviter pour l'instant : « Require review from Code Owners ». Le
fichier CODEOWNERS te nomme sur les fichiers du socle, mais tu es seul sur ce
dépôt, et GitHub interdit d'approuver sa propre pull request. Si les pull
requests sont ouvertes sous ton compte, cette option bloquerait toute fusion
qui touche ces fichiers.

Ce qui est déjà prouvé sans toi : sur une copie de ce dépôt, un commit qui
relève un budget de mémoire et cite un fait inexistant fait échouer la
commande de CI sur exactement ces deux contrôles. Ce qui manque : voir GitHub
refuser la fusion.

## Éléments cités

- `Socle — verify, contrôles, auto-test` — le nom du seul job de CI du dépôt, celui à exiger dans la règle de `main`.

## Où regarder

- Le workflow qui définit ce job : [.github/workflows/socle.yml](../../.github/workflows/socle.yml).
- Les réglages : [Settings → Branches du dépôt](https://github.com/theodubus/memory/settings/branches).
- Les derniers passages de la CI : [onglet Actions](https://github.com/theodubus/memory/actions).

Ce qu'il faut vérifier : que le check est coché dans la règle de `main`.

## Options

- **Autoriser la démonstration** : effort de deux minutes pour cocher le
  check ; risque nul, la pull request est fermée sans fusion et sa branche
  supprimée ; réversible.
- **Cocher le check sans démonstration** : même effort ; la porte reste
  prouvée en local seulement ; réversible.
- **Ne rien exiger** : effort nul ; une pull request à la CI rouge reste
  fusionnable, ce qui retire au socle sa seule garantie ; réversible.

## Conséquences

Si tu valides, j'ouvre la pull request, je te montre le check rouge et le
bouton de fusion bloqué, puis je la ferme. Si tu refuses, la porte reste
prouvée en local seulement, et la limite est écrite dans la mémoire. Sans
réponse, je n'ouvre rien ; la demande reste listée à chaque démarrage.

## Recommandation

Cocher le check et autoriser la démonstration. Vérifié : le job porte bien ce
nom sur GitHub (lu dans les deux passages de la CI), et la commande de CI
échoue sur les défauts injectés. Supposé : que ta règle de protection exige
déjà une pull request — je ne peux pas lire tes réglages d'ici.

## Réponses possibles

- `valider` — check coché ; ouvre la pull request de démonstration, puis ferme-la.
- `sans-demonstration` — check coché ; pas de pull request de démonstration.
- `refuser` — rien n'est exigé pour l'instant.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit.
