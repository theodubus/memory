<!-- socle: couche=backlog zone=publique -->
# B-0048 — Une action externe validée par une demande reste refusée par le hook

> statut : ouvert · origine : J-2026-10-12-M · lu : backlog@47ec3e4f

Mesuré à R6 : D-0016 autorise de pousser l'historique du projet d'échecs
dans la copie, et le hook refuse quand même `git push … main:main`, faute
de savoir qu'une validation existe. Le push revient alors à l'humain, même
validé. Piste : une demande validée qui nomme l'action exacte (le dépôt et
la branche) la laisse passer au hook, une fois. Voisin de B-0018.
