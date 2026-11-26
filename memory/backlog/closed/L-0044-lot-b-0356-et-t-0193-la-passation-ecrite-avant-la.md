<!-- socle: couche=backlog zone=publique -->
# L-0044 — Lot — B-0356 et T-0193 : la passation écrite avant la fusion, le seuil de contexte mesuré

> statut : fait · origine : J-2026-11-26-S · lu : backlog@5df1a37f · après : L-0043, T-0193, T-0194 · ref : B-0356, D-0209, D-0210, D-0211, J-2026-11-26-U, J-2026-11-26-W

Les deux sujets de JA-0006 qui changent le skill `socle-batch` et le
guide que chess reçoit (D-0204, D-0206) : la passation écrite dans le
dernier commit de la pull request, avant sa fusion, qui ne laisse aucune
branche de session à supprimer (B-0356, ses tâches après sa question
d'intention), et le seuil de contexte qui fait changer de session, fondé
sur les mesures déjà prises (T-0193, une demande à Théo). Ils touchent
les skills `socle-handoff` et `socle-batch`, le guide et la note de
version : une revue les relit ensemble.

## Revues

### Passe 1 — 2026-11-26

Commits : fc50a2d3..b20b13e6

Relue par l'agent lui-même, sur le dossier complet (le lot touche les copies protégées des skills ; ni contrôle, ni refus, ni hook, moins de 150 lignes de code et de tests).

- Bloquant : en session programmée, la session neuve partait de la branche de travail, que la fusion après la passation supprime désormais
- Ouvre : rien
