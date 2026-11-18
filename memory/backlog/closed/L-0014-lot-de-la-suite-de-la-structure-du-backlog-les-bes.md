<!-- socle: couche=backlog zone=publique -->
# L-0014 — Lot de la suite de la structure du backlog : les besoins découpés, les textes qui disent encore « sujet », l'ancien numéro dans le hook et les liens, la migration qui perd un contenu

> statut : fait · origine : J-2026-11-16-V · après : L-0012, T-0049, T-0050, T-0051, T-0052, T-0053, T-0057, T-0058, D-0133 · lu : backlog@186c07f1 · ref : J-2026-11-18-M

Formé le 16 novembre (J-2026-11-16-V) : la suite de B-0265, la
structure du backlog en quatre formes, que le lot L-0013 laisse. T-0049
et T-0050 en sortent, pour que L-0013 se close en une session ; les trois
constats de sa revue que le format laisse au backlog y entrent. Toutes
servent B-0265 et touchent le backlog, sa migration
(`engine/socle/migration.py`) et ses textes : une seule revue les juge.
Après L-0012, que Théo a placé juste après L-0013.

T-0050 change des textes que des tests lisent mot pour mot : une demande
à Théo nomme ces tests avant leur push. T-0052 se fait avant la mise à
jour de chess.

T-0057 et T-0058 y entrent le 16 novembre (J-2026-11-16-AD) : la vue de la
suite que Théo a validée (B-0274), qui lit le même backlog.

## Revues

### Passe 1 — 2026-11-18

Commits : 28755ed..34e0908

- Bloquant : le refus d'un ancien numéro par le hook, changé sans modèle de menace écrit
- Bloquant : T-0069 dans aucun lot, contre la consigne qu'aucune tâche ne reste à part
- Bloquant : la case de T-0049 qui dit les critères des tâches vérifiés par un test, faux pour dix tâches qui livrent une demande ou un relevé
- Ouvre : T-0083, T-0084, T-0085, T-0086, B-0285

Recul : première passe, sans précédente à comparer ; ses trois bloquants ont trois causes distinctes : un garde-fou changé sans modèle de menace écrit, une tâche laissée hors des lots, une case cochée plus large que ce qu'elle tient. Les entrées qu'elle ouvre côtoient ce que le lot ferme sans le refaire : T-0083 resserre le refus que pose T-0051, T-0085 complète les liens de la suite de T-0058, T-0084 et T-0086 récrivent des critères du backlog, B-0285 vise une règle du prochain jalon antérieure au lot. Les lots clos qui ont touché les mêmes fichiers (le hook, la revue, le backlog) ont déjà ouvert un garde-fou sans modèle de menace, L-0012 à sa passe 1 : la consigne des sous-agents le demande d'abord, et l'orchestrateur le vérifie désormais au compte rendu. La correction tient en une décision et quelques lignes de la mémoire, sans conception nouvelle : pas de passe de plus ; le lot se clôt aux réponses de Théo à D-0132 et D-0133. Décision : continuer
