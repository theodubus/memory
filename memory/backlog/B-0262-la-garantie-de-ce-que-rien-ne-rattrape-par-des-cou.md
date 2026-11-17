<!-- socle: couche=backlog zone=publique -->
# B-0262 — La garantie de ce que rien ne rattrape par des couches qui ne lisent pas le shell : la protection de la branche par défaut contre le push forcé, le push de chaque fin de réponse, la perte d'un dossier qui contient le projet

> statut : ouvert · origine : J-2026-11-16-G · ref : D-0120 · lu : backlog@d9da377d

D-0120@f10e0e80, validée le 16 novembre (J-2026-11-16-G), borne le hook
de l'agent aux formes qu'un agent écrit : une forme exotique qu'il lit de
travers laisse passer ce que rien ne rattrape. La garantie de ces effets
ne peut venir d'un lecteur du shell ; ce sujet étudie celles qui n'en
lisent pas, et dit ce qui reste sans garantie :

- le push forcé : la protection de la branche par défaut sur GitHub (un
  ensemble de règles qui le refuse côté serveur). À vérifier : si celle de
  ce dépôt et de chess le refuse, ou ne fait qu'exiger la CI, et si l'état
  peut le dire comme il dit la CI exigée ;
- la suppression du projet : le push de chaque fin de réponse, que
  l'environnement cloud exige, laisse le projet sur GitHub ; à mesurer
  hors de l'environnement cloud ;
- la suppression d'un dossier qui contient le projet, au-delà du projet
  lui-même : rien ne la borne aujourd'hui, hors du hook. Piste à
  vérifier : le bac à sable de l'outil shell de l'agent, s'il en a un.

## Satisfait quand

- [ ] le « Fait quand » de T-0023 est tenu
