<!-- socle: couche=backlog zone=publique -->
# B-0124 — Une revue adversariale, par un relecteur sans contexte, avant de livrer un lot

> statut : ouvert · origine : J-2026-11-01-O · lu : backlog@b9991d59 · après : D-0070

BMAD faisait relire le travail par des relecteurs indépendants, dont une
« lentille » adversariale qui cherche à le prendre en défaut. Retiré
(D-0051), ce principe est resté dans la répartition entre agents
(B-0055@5f053f9e, des relecteurs sans contexte), qui attend la planification et le
pilote. Théo demande s'il a été abandonné (J-2026-11-01-O).

Une revue adversariale n'a pas besoin d'un agent maître : avant de livrer
un lot, l'agent confie le diff à un relecteur qui n'a pas son contexte,
chargé de le prendre en défaut (ce qui casse, ce qu'aucun test ne prouve,
ce qui contredit la mémoire ou une spécification) ; l'agent corrige ou
répond à chaque constat, et le récap le dit. Le moteur ne connaît aucun
agent : la procédure vit côté agent, en skill et dans les instructions ;
le moteur peut fournir au relecteur le contexte de la revue (le diff, les
sujets du lot, les spécifications citées). Ce qu'elle trouve se mesure au
banc.

## Fait quand

- [ ] la procédure de revue est écrite, côté agent, et les instructions disent quand s'en servir
- [ ] le banc mesure ce qu'elle trouve sur des défauts connus
