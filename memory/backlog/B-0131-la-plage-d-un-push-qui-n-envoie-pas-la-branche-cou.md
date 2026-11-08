<!-- socle: couche=backlog zone=publique -->
# B-0131 — La plage d'un push qui n'envoie pas la branche courante juge la demande en attente dans l'arbre de travail, pas dans la référence poussée

> statut : ouvert · origine : J-2026-11-08-F · lu : backlog@00a31f75

Relevé par la revue du correctif de D-0071 (J-2026-11-08-F), hors de ce
qu'il change. La tolérance d'un fichier protégé sous une demande en
attente lit la demande dans l'arbre de travail, et la compare à l'amont de
la branche courante. Un push d'une autre branche, depuis un checkout qui
n'a pas la demande, est donc refusé, alors que D-0071 le laisserait
partir. Le refus existait avant le correctif ; il ne gêne que ce geste
rare, l'agent poussant sa branche courante.

À faire : juger la demande dans la référence poussée, pas dans l'arbre.

## Fait quand

- [ ] un push d'une branche autre que la courante laisse partir le fichier protégé qu'une demande en attente de cette branche couvre, la CI exigée
