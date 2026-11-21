<!-- socle: couche=demandes zone=publique -->
# D-0153 — Les trois cas du tri T-0120 : B-0048 sorti de JA-0005, abandonné ou gardé ; B-0192 abandonné, gardé dans L-0021 ou déplacé vers JA-0006 ; B-0095 abandonné ou gardé ?

> date : 2026-11-21 · forme : séance

## Question posée

Les trois cas de jugement du tri du backlog ouvert (T-0120, J-2026-11-21-M), posés à Théo dans la conversation le 21 novembre, chacun avec ses choix :

1. B-0048 (une action externe validée par une demande reste refusée par le hook ; T-0008 bloquée, T-0071 la suit) : aucun refus nouveau depuis D-0026, et B-0048 empêche JA-0005 de se fermer, donc la mise à jour de chess (JA-0006). a. le sortir de JA-0005, comme B-0179, le sujet gardé en tête au backlog ; b. l'abandonner en renvoyant à D-0026, T-0008 et T-0071 avec lui ; c. le garder dans JA-0005. Recommandation : a.

2. B-0192 (la classe d'un test dans la clé de son constat toléré ; T-0032 dans L-0021), basse priorité depuis le 12 novembre, à clore sans suite si aucun projet n'en a besoin. a. l'abandonner maintenant, L-0021 passant de 7 à 6 tâches ; b. le garder dans L-0021 ; c. le déplacer vers JA-0006, la mise à jour de chess, seul projet qui pourrait en montrer le besoin, clos sans suite sinon. Recommandation : c.

3. B-0095 (un projet à deux langages n'a qu'un adaptateur) : les adaptateurs multiples existent (ADR-0051), le pilote a pris Kotlin, B-0147 et B-0179 suivent ce qu'il a montré. a. l'abandonner en renvoyant à ADR-0051, B-0147 et B-0179 ; b. le garder jusqu'à la reprise du pilote. Recommandation : a.

Réponses : `valider` (les trois recommandations, 1 a, 2 c, 3 a), `refuser`, `contexte-insuffisant`, ou un choix par cas ; Théo répond « 1 a / 2 c / 3 a », les trois recommandations.
