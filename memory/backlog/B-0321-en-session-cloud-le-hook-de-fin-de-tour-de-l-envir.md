<!-- socle: couche=backlog zone=publique -->
# B-0321 — En session cloud, le hook de fin de tour de l'environnement laisse conclure sans vérifier le push un tour qu'un hook de fin de tour a relancé, et une branche que l'origine n'a jamais reçue

> statut : ouvert · origine : J-2026-11-20-AR · ref : B-0262, T-0023, B-0318 · lu : backlog@689e597f

La revue de L-0020 (J-2026-11-20-AR) a lu le hook de fin de tour de
l'environnement cloud, `~/.claude/stop-hook-git-check.sh`, que le relevé
de T-0023 (`docs/fabrication/garanties-hors-du-hook.md`) tenait pour la
couche qui rattrape la suppression du projet. Deux trous :

- il sort sans rien vérifier quand `stop_hook_active` vaut vrai, sur tout
  arrêt d'un tour qu'un hook de fin de tour a déjà relancé ; le hook de
  fin de tour du socle en relance souvent (le récap sans ses deux
  lignes, `verify --fast` rouge), et un commit fait pendant la relance
  peut finir le tour sans être poussé ;
- il compare la branche à `origin/<branche>`, sinon à `origin/HEAD` ;
  dans un clone sans `origin/HEAD`, une branche que l'origine n'a jamais
  reçue n'a aucun commit non poussé à ses yeux.

Le hook de l'environnement n'est pas au socle ; le sien peut combler le
manque. Piste : en session cloud, le hook de fin de tour du socle
avertit d'un commit non poussé, ou d'une branche sans branche distante,
sur un arrêt où `stop_hook_active` vaut vrai, sans refuser deux fois.

## Satisfait quand

- [ ] en session cloud, un tour relancé par un hook de fin de tour, ou mené sur une branche que l'origine n'a jamais reçue, ne se conclut plus avec un commit non poussé sans que l'agent en soit averti
