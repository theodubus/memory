<!-- socle: couche=backlog zone=publique -->
# B-0275 — Une dispense écrite hors du dernier paragraphe du message de commit est ignorée sans le dire : le refus de docs.correspondance redemande le trailer qu'il a sous les yeux

> statut : ouvert · origine : J-2026-11-17-D · lu : backlog@3ea7d22a

Mesuré le 17 novembre (J-2026-11-17-D) : un commit dont le message porte
`Dispense-doc: <raison>` dans un paragraphe à part, suivi d'un paragraphe
de lignes d'attribution (`Co-Authored-By`…), n'est pas dispensé. Les
trailers ne se lisent que dans le dernier paragraphe du message, comme
git les lit ; le refus de `docs.correspondance` redemande alors « un
trailer de commit `Dispense-doc: <raison>` », que l'agent croit avoir
écrit. Il ne le voit qu'en relisant le message par `git
interpret-trailers --parse`. La dispense de test (`Dispense-test`) et le
trailer `Corrige` se lisent de même. Tout agent qui signe ses commits
peut l'écrire ainsi ; le push est refusé, et le corriger demande de
réécrire le commit.

## Satisfait quand

- [ ] une dispense écrite hors du bloc final de trailers ne laisse plus l'agent sans savoir pourquoi elle ne vaut pas
