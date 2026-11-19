<!-- socle: couche=backlog zone=publique -->
# L-0005 — Lot du hook, ce qu'il laisse passer : uv run et poetry run, la substitution entre guillemets, le push forcé par une variable, l'ancien numéro repris

> statut : en cours · origine : J-2026-11-15-J · après : L-0015, T-0005, T-0007, T-0006, T-0083, T-0086 · lu : backlog@19378efe · ancien : B-0235

Trois écritures que le hook de l'agent juge mal, deux qu'il laisse
passer, une qu'il refuse à tort : les mêmes fichiers que le lot d'avant
(le découpage et le jugement des commandes, `tests/test_garde.py`), sous
la règle 2 de D-0112 (ADR-0080) qui dit lesquelles se corrigent.

Le 16 novembre, Théo y fait entrer les quatre sujets du hook gardés sous D-0120 (J-2026-11-16-I) : `find … | xargs rm` (B-0246, voisin de B-0230), `uv run` et `poetry run` (B-0248), le push forcé passé par une variable ou une fonction d'aide (B-0254), la substitution entre guillemets (B-0260). S'il ne tient pas en une session, il se coupe en deux lots du hook.

Le 16 novembre, selon la règle qui réunit dans un lot les sujets qui touchent les mêmes fichiers ou le même garde-fou, appliquée à tout le backlog ouvert (J-2026-11-16-J) : une action externe validée par une demande que le hook refuse encore (B-0048), dans le même jugement des actions irréversibles que B-0254.

L-0014 et L-0015 passent avant lui le 16 novembre (J-2026-11-16-AB) : T-0049
refait les lots du jalon, celui-ci compris, et L-0015 corrige la revue
qui les juge ; L-0012 reste avant eux, comme Théo l'a placé.

Le 18 novembre, T-0049 découpe B-0230 et B-0048 (J-2026-11-18-J) : T-0070 juge le chemin passé en argument au script d'un `python -c`, à côté de T-0002 ; T-0008 soumet à Théo l'action externe validée, que T-0071 fait passer au hook après sa réponse.

Le 19 novembre, coupé en deux sur son coût estimé (J-2026-11-19-Q) : il
garde ce que le hook laisse passer, ses quatre sujets de priorité haute
(T-0005, T-0007, T-0006, T-0083) et l'action externe validée (T-0086,
T-0008, T-0071) ; le découpage des commandes (`engine/socle/commands.py`)
et le jugement des actions irréversibles et des références
(`engine/socle/hooks.py`). Les écritures qu'il juge mal, dont il portait
le titre, vont à L-0019.

T-0086 faite, T-0008 et T-0071 en sortent (J-2026-11-19-R) : T-0008 est
bloquée jusqu'à un refus nouveau d'une action validée qui bloque le
travail, la condition de D-0026 ; T-0071 la suit.
