<!-- socle: couche=demandes zone=publique -->
# D-0143 — Retenir la proposition du 20 novembre pour arrêter de tourner en rond sur le hook de l'agent

> date : 2026-11-20 · forme : séance

## Question posée

Retenir la proposition du 20 novembre pour arrêter de tourner en rond sur le hook de l'agent ?

Le code déjà là. À garder : l'analyse des commandes (engine/socle/hooks.py, engine/socle/commands.py) et ses tests : elle sert les trois cas que rien d'autre ne rattrape (un push forcé ou sur main, la suppression du projet avec .git, le réglage local de Claude Code que git ne suit pas et qui peut couper les hooks) ; elle est payée, testée, et marche ; la retirer ou la simplifier serait un nouveau chantier du hook, la boucle elle-même ; son coût courant, quelques refus à tort, est acceptable. Le tri des constats et le recul, qui servent à tous les lots. À enlever : la liste des formes exotiques et la procédure qui les signale (D-0128, au lot L-0006) ; les entrées ouvertes du hook au backlog, B-0230 et T-0002 (D-0142 sans objet), B-0305, B-0306 et T-0108, B-0307 et T-0109, B-0308, B-0302 ; la vérification après coup proposée plus tôt, retirée.

La proposition :
1. La règle, une décision qui remplace ADR-0082 : le hook est terminé ; on n'y touche que sur une preuve : un refus à tort qui a bloqué un vrai travail, ou un contournement réellement écrit par un agent dans une session (pas imaginé par un relecteur), dont l'effet ne serait rattrapé par rien d'autre. Toute entrée du hook cite cette preuve (un lien vers la session ou le journal), sinon elle ne s'ouvre pas.
2. Couper la source : la revue d'un lot qui touche le hook ne cherche plus de contournements ; elle vérifie seulement qu'il ne casse rien (pas de régression). Une trouvaille de contournement est écartée d'office.
3. Vider le backlog du hook : fermer les entrées listées, en renvoyant à cette décision.
4. L'écrire là où chaque session le lit : une ligne dans AGENTS.md (lu à chaque démarrage), les consignes du chantier actif, et le skill delegate-lot (lu à chaque lot, qui écrit la consigne du relecteur).

Si Théo valide : l'agent écrit la décision qui remplace ADR-0082 et les trois lignes, ferme les entrées, et fusionne la pull request 71 (le code de L-0019 reste).
