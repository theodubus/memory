<!-- socle: couche=backlog zone=publique -->
# B-0131 — La plage d'un push qui n'envoie pas la branche courante juge la demande en attente dans l'arbre de travail, pas dans la référence poussée

> statut : abandonné · origine : J-2026-11-08-F · ref : J-2026-11-14-L · lu : backlog@00a31f75

Relevé par la revue du correctif de D-0071 (J-2026-11-08-F), hors de ce
qu'il change. La tolérance d'un fichier protégé sous une demande en
attente lit la demande dans l'arbre de travail, et la compare à l'amont de
la branche courante. Un push d'une autre branche, depuis un checkout qui
n'a pas la demande, est donc refusé, alors que D-0071 le laisserait
partir. Le refus existait avant le correctif ; il ne gêne que ce geste
rare, l'agent poussant sa branche courante.

À faire : juger la demande dans la référence poussée, pas dans l'arbre.

Abandonné le 14 novembre, sur la décision de Théo (D-0111, J-2026-11-14-L) :
un cas exotique. Le sujet le dit lui-même, il ne gêne qu'un geste rare,
l'agent poussant sa branche courante, et le refus se voit.

## Satisfait quand

- [ ] un push d'une branche autre que la courante laisse partir le fichier protégé qu'une demande en attente de cette branche couvre, la CI exigée
