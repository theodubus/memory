<!-- socle: couche=demandes zone=publique -->
# D-0003 — Protéger la branche par défaut de ce dépôt et laisser une pull request défectueuse prouver que la CI la bloque

> date : 2026-10-10 · bloque : la porte du jalon 5

## Décision demandée

Configurer toi-même, sur GitHub, la protection de la branche par défaut de
`theodubus/memory`, puis me laisser ouvrir une pull request volontairement
défectueuse pour prouver que la CI la bloque.

## Contexte

Le cadrage pose que seule la CI est incontournable, à condition que la
branche soit protégée : sans protection, un push direct la contourne. La
porte du jalon 5 est « la CI bloque une pull request défectueuse ». Je ne
peux ni configurer la protection (réglage du dépôt, action externe réservée
à l'humain par le point 4 de la politique) ni ouvrir de pull request sans ton
accord.

Ce qui est déjà prouvé sans toi : l'auto-test injecte chaque défaut connu
dans un projet jetable et vérifie que la commande de CI le refuse, par son
code de sortie. Ce qui manque : que GitHub empêche réellement la fusion quand
cette commande échoue.

Réglages à poser dans Settings, Branches, sur la branche par défaut (`main`
une fois la première pull request fusionnée) : exiger une pull request,
exiger la réussite du check « Socle — verify, contrôles, auto-test », exiger
la revue des code owners (le fichier CODEOWNERS te nomme sur `.socle/`,
`.github/`, `.claude/settings.json` et les réponses humaines), interdire les
force-push.

## Éléments cités

- `.github/workflows/socle.yml` — le workflow de CI posé par l'installeur, qui lance la commande de CI du socle à chaque push et à chaque pull request.
- `.github/CODEOWNERS` — le fichier qui exige ta revue sur ce qui définit les garde-fous.

## Options

- **Protéger et autoriser la pull request de démonstration** : effort de
  cinq minutes pour toi ; risque nul, la pull request de démonstration est
  fermée sans fusion ; réversible.
- **Protéger sans démonstration** : même effort ; la porte reste prouvée en
  local seulement, par l'auto-test ; réversible.
- **Ne pas protéger** : effort nul ; la CI devient contournable, ce qui
  retire au dispositif sa seule garantie ; réversible.

## Conséquences

Si tu valides, j'ouvre une pull request avec un défaut injecté, je montre le
check rouge et la fusion bloquée, puis je la ferme. Si tu refuses, la porte
du jalon 5 reste prouvée en local seulement, et la limite est écrite dans la
mémoire. Sans réponse, rien ne change : la demande reste dans l'état dérivé,
et la CI tourne sans pouvoir bloquer une fusion.

## Recommandation

Protéger et autoriser la démonstration. Vérifié : l'auto-test fait échouer la
commande de CI sur chaque défaut injecté, et ses témoins sains passent.
Supposé : que le check porte bien sur GitHub le nom écrit dans le workflow,
« Socle — verify, contrôles, auto-test » — je ne l'ai pas vu tourner.

## Réponses possibles

- `valider` — la branche est protégée ; ouvre la pull request de démonstration, puis ferme-la.
- `proteger-seulement` — la branche est protégée ; pas de pull request de démonstration.
- `refuser` — pas de protection pour l'instant.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit.
