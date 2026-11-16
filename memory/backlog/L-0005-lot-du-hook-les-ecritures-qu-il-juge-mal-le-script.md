<!-- socle: couche=backlog zone=publique -->
# L-0005 — Lot du hook, les écritures qu'il juge mal : le script d'un heredoc, la liste qu'un find ou un grep donne à xargs, la conjonction des filtres d'un find

> statut : ouvert · origine : J-2026-11-15-J · après : L-0012, T-0001, T-0002, T-0003, T-0004, T-0005, T-0006, T-0007, T-0008 · lu : backlog@19378efe · ancien : B-0235

Trois écritures que le hook de l'agent juge mal, deux qu'il laisse
passer, une qu'il refuse à tort : les mêmes fichiers que le lot d'avant
(le découpage et le jugement des commandes, `tests/test_garde.py`), sous
la règle 2 de D-0112 (ADR-0080) qui dit lesquelles se corrigent.

Le 16 novembre, Théo y fait entrer les quatre sujets du hook gardés sous D-0120 (J-2026-11-16-I) : `find … | xargs rm` (B-0246, voisin de B-0230), `uv run` et `poetry run` (B-0248), le push forcé passé par une variable ou une fonction d'aide (B-0254), la substitution entre guillemets (B-0260). S'il ne tient pas en une session, il se coupe en deux lots du hook.

Le 16 novembre, selon la règle qui réunit dans un lot les sujets qui touchent les mêmes fichiers ou le même garde-fou, appliquée à tout le backlog ouvert (J-2026-11-16-J) : une action externe validée par une demande que le hook refuse encore (B-0048), dans le même jugement des actions irréversibles que B-0254.
