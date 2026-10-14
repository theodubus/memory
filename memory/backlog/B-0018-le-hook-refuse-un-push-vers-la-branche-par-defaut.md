<!-- socle: couche=backlog zone=publique -->
# B-0018 — Le hook refuse un push vers la branche par défaut d'un dépôt local jetable

> statut : ouvert · origine : J-2026-10-10-W · lu : backlog@85e18aaf

Au jalon 6, le hook de l'agent a refusé `git push origin main` vers le
dépôt d'origine d'un projet jetable, un simple dossier local : la
politique (point 4) vise une publication, qu'un dépôt local n'est pas.
Ne refuser que si la destination est distante, ou garder le refus et le
dire dans sa raison ; à arbitrer, le refus large est le plus sûr.

D-0026, réponse de Théo `rien` (J-2026-10-14-V) : le refus d'un push vers un
dossier local reste. Le sujet reste ouvert avec B-0048, qui garde la
réponse exacte et dit quoi noter si le refus devient bloquant.
