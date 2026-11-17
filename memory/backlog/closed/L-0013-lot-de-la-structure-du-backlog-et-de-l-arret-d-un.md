<!-- socle: couche=backlog zone=publique -->
# L-0013 — Lot de la structure du backlog et de l'arrêt d'un chantier qui tourne en rond, coupé du lot L-0011

> statut : fait · origine : J-2026-11-16-R · ref : J-2026-11-17-C · après : L-0011, T-0046, T-0047, T-0048 · lu : backlog@5a24a9b3 · ancien : B-0269

Coupé du lot L-0011 le 16 novembre (J-2026-11-16-R) : les deux entrées de
ce lot dont la spécification attend Théo. D'abord la structure du backlog
(B-0265), que D-0121 place en premier, sa spécification soumise par
D-0123 ; puis l'arrêt d'un chantier qui tourne en rond (B-0263), soumis
par D-0124, qui écrit l'historique des revues dans l'entrée du lot, que
la structure renumérote. Les deux touchent le format du backlog, les
skills `socle-batch` et `socle-review` et leurs gabarits, le guide et
les contrôles du backlog : une seule revue les juge.

Hors des entrées : les tests dont la structure change la valeur attendue
se nomment dans une demande, validée avant leur push ; deux sessions sont
probables, la seconde pour la migration de ce dépôt et le reclassement.

B-0270 y entre le 16 novembre (J-2026-11-16-S), relevé par la revue du lot L-0011 : il touche le gabarit du skill `socle-review`, comme B-0263.

T-0049 et T-0050, les tâches de B-0265 qui restent, passent au lot L-0014 le
16 novembre (J-2026-11-16-V) : la consigne de la session était B-0265, B-0263
puis B-0270, et T-0049 demande une session à lui seul.

## Revues

### Passe 1 — 2026-11-16

Commits : 42c246b..8719a8f

- Bloquant : la migration garde la priorité d'un lot ou d'un jalon
- Bloquant : une citation par un ancien numéro échappe à la lecture prouvée
- Bloquant : deux refus des formes du backlog sans défaut injecté
- Ouvre : T-0051, T-0052, T-0053

Recul : les trois bloquants de cette passe, la première du lot, viennent de la migration et des contrôles neufs de la structure du backlog, sans passe précédente à qui les comparer ; les entrées que le lot ouvre, T-0051 à T-0053, sont de la nature de celles qu'il ferme, des défauts de cette même structure, réunis au lot L-0014 ; aucun lot clos n'avait touché ces fichiers neufs. La correction est légère, et la passe suivante relit une autre tâche, T-0047 : continuer.

### Passe 2 — 2026-11-16

Commits : 36be954..1f8e85f

- Bloquant : la clôture d'un lot ne juge que la forme du dernier recul · cause nouvelle
- Bloquant : l'arrêt se lève par une demande qui ne vise pas le lot · cause nouvelle
- Ouvre : T-0054, T-0055, B-0273

Recul : les deux bloquants de cette passe n'ont pas la cause de ceux de la passe 1, venus de la migration : ils viennent de la clôture et de l'arrêt que T-0047 pose, et leur correction applique à la clôture les règles déjà écrites pour la passe, sans conception nouvelle ; les entrées ouvertes, T-0054, T-0055 et B-0273, sont des défauts de l'historique des revues, de la nature de ce que le lot ferme, sauf B-0273, antérieur ; aucun lot clos n'avait touché cette section, neuve. La passe suivante relira une autre tâche, T-0048 : continuer.

### Passe 3 — 2026-11-17

Commits : 9bec13d..1de6b24

- Ouvre : rien

Recul : cette passe n'a aucun bloquant, quand la passe 1 en avait trois, venus de la migration, et la passe 2 deux, venus de la clôture et de l'arrêt que T-0047 pose : aucune cause ne revient. Elle n'ouvre aucune entrée ; le lot ferme T-0048 et B-0270, un geste du skill qu'un projet équipé ne pouvait pas faire. Le lot L-0011, seul lot clos à avoir touché ce gabarit, avait ouvert B-0270 lui-même, une entrée de cette nature, que celui-ci ferme sans en rouvrir. Il ne reste aucune tâche au lot, qui se clôt : continuer.
