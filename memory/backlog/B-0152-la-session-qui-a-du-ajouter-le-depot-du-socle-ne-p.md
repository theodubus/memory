<!-- socle: couche=backlog zone=publique -->
# B-0152 — La session qui a dû ajouter le dépôt du socle ne peut pas commiter les fichiers protégés d'une mise à jour, que « Et maintenant » lui dit de commiter sans attendre

> statut : ouvert · origine : J-2026-11-10-J · lu : backlog@f7e6772f

En session cloud, une mise à jour qui change des fichiers protégés dit,
à la session qui a dû ajouter le dépôt du socle, d'y « commiter, pousser
la branche et ouvrir la pull request, d'une traite et sans rien
attendre », la demande se posant dans une session neuve. Mais le hook
avant commit refuse un fichier protégé changé qu'aucune demande en
attente ne couvre (`protege.fichiers`, éprouvé par l'auto-test) : cette
session ne peut pas commiter ce qu'on lui dit de commiter. Relevé par la
revue de B-0148 (J-2026-11-10-J) ; le README déconseille déjà d'ajouter
le dépôt du socle à la session.

## Satisfait quand

- [ ] la session qui a dû ajouter le dépôt du socle fait ce que « Et maintenant » lui dit sans buter sur le hook avant commit
