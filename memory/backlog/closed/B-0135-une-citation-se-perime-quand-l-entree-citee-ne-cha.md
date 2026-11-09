<!-- socle: couche=backlog zone=publique -->
# B-0135 — Une citation se périme quand l'entrée citée ne change que ses métadonnées, et une demande et son sujet qui se citent l'un l'autre se périment dans l'ordre d'écriture

> statut : fait · origine : J-2026-11-08-S · lu : backlog@7b6c36fe · après : D-0086 · ref : J-2026-11-09-V

Une empreinte de lecture couvre tout le texte de l'entrée citée : ajouter
`après : D-NNNN` à un sujet, ou changer son statut, périme chaque citation
de ce sujet, qu'il faut relire et récrire, souvent en plusieurs allers et
retours. Une demande qui cite le sujet qui l'attend, et ce sujet qui
l'attend en retour, se périment selon l'ordre où on les écrit (le pilote :
D-0036 et B-0020, J-2026-11-08-S). Ce dépôt l'a rencontré aussi, à chaque
changement de statut d'une ADR citée.

Pistes : une empreinte qui ne couvre pas la ligne des métadonnées, ou une
commande qui récrit les citations périmées d'une entrée qu'on vient de
changer.

Fait quand :
- [x] changer les métadonnées d'une entrée ne périme plus ses citations, ou une commande les récrit, avec un test
