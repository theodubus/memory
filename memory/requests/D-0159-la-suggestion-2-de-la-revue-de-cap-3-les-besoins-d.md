<!-- socle: couche=demandes zone=publique -->
# D-0159 — La suggestion 2 de la revue de cap 3 : les besoins de couverture seule qu'une revue ouvre, avant ou après la mise à jour de chess ?

> date : 2026-11-23 · forme : séance

## Question posée

La suggestion 2 de la revue de cap 3 (J-2026-11-23-D), reformulée : une revue de lot trie ses constats ; un défaut bloquant se corrige dans le lot, le reste va au backlog, donc dans JA-0005, qui doit être fini avant la mise à jour de chess. Parmi ces entrées, certaines corrigent une vraie erreur (un message qui dit faux) ; d'autres n'ajoutent que de la couverture à du code qui marche : un test manquant pour un délai pourtant juste (B-0331), trois mutations de bord qui survivent aux tests (B-0332), un message de priorité basse (B-0333). Que faire de ces entrées de couverture seule ?

- `avant` : tout ce qu'une revue ouvre reste avant chess, comme aujourd'hui.
- `apres` : ce qui corrige une erreur reste avant chess ; ce qui n'ajoute que de la couverture passe après la mise à jour de chess.
- `ecarter` : on n'en décide pas maintenant, rien ne change.

À la question de Théo (« Tu recommandes quoi ? »), l'agent recommande `ecarter` : sur les 41 besoins ouverts de JA-0005, trois seulement sont de couverture seule (B-0331, B-0332, B-0333) ; sur les trois derniers lots, les revues ont ouvert 6 besoins pendant que 18 se fermaient ; ce qui rallonge JA-0005 est surtout les 27 tâches sur 53 qui attendent une décision de Théo.

Réponse donnée : `ecarter`.
