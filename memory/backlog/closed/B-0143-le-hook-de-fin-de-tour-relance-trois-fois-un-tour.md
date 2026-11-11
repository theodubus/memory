<!-- socle: couche=backlog zone=publique -->
# B-0143 — Le hook de fin de tour relance trois fois un tour qui ne peut rien corriger, et l'agent répète son récap à chaque fois

> statut : fait · origine : J-2026-11-09-K · lu : backlog@c0d85cf2 · ref : J-2026-11-11-D

Quand un contrôle de fin de tour échoue sur ce que l'agent ne peut pas
corriger (ici, un fichier protégé changé par erreur, que le hook lui
interdit de remettre, J-2026-11-09-B), le hook de fin de tour bloque
quand même la fin, trois fois par tour, avec le même rapport ; l'agent
répond chaque fois par un récap complet, puisque sa réponse est une fin de
tour. Théo l'a remarqué (J-2026-11-09-K). Chaque relance relit toute la
conversation et coûte de la fenêtre d'usage ; pendant une limite, elle est
refusée (B-0133).

Pistes : un échec identique à celui de la tentative précédente, sans
changement de l'arbre entre les deux, ne relance plus ; ou un contrôle
qui sait que l'agent ne peut pas corriger (un fichier protégé hors de ses
commits) avertit au lieu de bloquer en fin de tour, le commit et la CI
refusant toujours ; et une relance accepte une réponse courte, sans
redire le récap. Toucher au hook de fin de tour : une demande.

Fait quand :
- [x] un tour dont l'échec ne change pas entre deux tentatives ne se relance plus, ou la raison de garder la relance est écrite, et un test le montre
