<!-- socle: couche=backlog zone=publique -->
# JA-0005 — Jalon — le produit corrigé et stabilisé avant la mise à jour de chess

> statut : ouvert · origine : J-2026-11-14-M · après : B-0213, B-0214, B-0232, B-0228, B-0261, B-0251, B-0153, B-0267, B-0268, B-0265, B-0263, B-0270, B-0257, B-0258, B-0229, B-0230, B-0231, B-0246, B-0248, B-0254, B-0260, B-0227, B-0226, B-0233, B-0217, B-0242, B-0243, B-0140, B-0185, B-0167, B-0176, B-0200, B-0203, B-0241, B-0262, B-0193, B-0225, B-0195, B-0144, B-0152, B-0183, B-0186, B-0201, B-0197, B-0210, B-0219, B-0249, B-0194, B-0156, B-0198, B-0259, B-0252, B-0133, B-0273, B-0274, B-0276, B-0277, B-0278, B-0279, B-0280, B-0147, B-0275, B-0292, B-0301, B-0303, B-0311, B-0317, B-0320, B-0321, B-0322, B-0324, B-0327, B-0328, B-0331, B-0334, B-0335, B-0341, B-0342, B-0343, B-0348, B-0349, B-0344, B-0345, B-0347, B-0350 · lu : backlog@f69fc579 · ancien : B-0224

Ce qui reste de la liste que Théo a fixée le 13 novembre, à finir avant
les nouvelles fonctions (J-2026-11-13-I). Né le 14 novembre sous la
forme d'un lot qui réunissait vingt-deux sujets sans fichiers communs,
il devient un jalon le 15 novembre, sur la décision de Théo (D-0118) :
ses sujets se répartissent en sept lots, chacun ce qu'une seule revue
juge en une session, dans l'ordre qu'il donnait, le hook d'abord. Les
sujets de priorité basse (B-0217, B-0219, B-0195, B-0172, B-0198,
B-0203) se prennent dans leur lot quand c'est commode. Après lui, la
mise à jour de chess, avec son prompt complété.

Le 21 novembre, Théo retient les suggestions de la revue de cap 2
(D-0151, J-2026-11-21-B) : JA-0005 finit sans attendre chess, et « je
veux tous les besoins/taches de correction/stabilisation du produit
avant chess, puis le reste apres ». Le jalon reçoit les trente besoins de
correction et de stabilisation qui n'étaient dans aucun jalon (B-0147,
B-0271 à B-0322), et cède à JA-0006 le balayage de mutation de chess
(B-0172), qui se mesure à la mise à jour. Hors de lui restent les
fonctions nouvelles (B-0055, B-0109, B-0158, B-0174, B-0188, JA-0004),
ce qui attend l'usage réel du pilote (B-0104, B-0012, B-0095, B-0179) et
l'essai de la revue de cap (B-0310). Ses besoins sans tâche se découpent
à la formation de leur lot.

Le 21 novembre, le tri T-0120 relève que trois besoins de correction du
produit ouverts le jour même lui manquent (J-2026-11-21-M) : B-0326, les
identifiants de l'atelier dans les messages du moteur, et B-0327 et
B-0328, ouverts par la revue de L-0008 (J-2026-11-21-L). Ils le
rejoignent, selon D-0151.

Le 21 novembre, sur le tri T-0120, Théo répond « 1 a / 2 c / 3 a »
(D-0153, J-2026-11-21-O) : B-0048 en sort, comme B-0179, avec ce qui
attend un événement, gardé en tête au backlog (D-0026) ; B-0192 passe à
JA-0006, où la mise à jour de chess peut en montrer le besoin ; B-0095,
que nommait la liste de ce qui attend le pilote, est abandonné.

Le 21 novembre, sur la décision de Théo (D-0154, J-2026-11-21-P), ses
lots se forment tous d'un coup, et non plus à leur annonce
(J-2026-11-21-Q) : après L-0021, L-0009 et L-0010, dans l'ordre qu'il
garde (D-0155), viennent L-0023, la seconde moitié de L-0010, puis les
lots nouveaux, de L-0024 à L-0033.

Le 22 novembre, Théo clôt les trois besoins que la formation des lots
laissait sans tâche (D-0156, J-2026-11-22-A) : le risque de B-0320 est
accepté, B-0321 et B-0322 sont abandonnés sous ADR-0098. Chaque besoin
ouvert de JA-0005 a désormais ses tâches dans un lot.

## Fait quand

- [ ] ses besoins sont clos, et aucun besoin ouvert de correction ou de stabilisation du produit n'est hors de lui

Le 23 novembre, la revue de cap 3 relève cinq tâches du jalon hors de tout lot, nées des revues de L-0021 et de L-0009 (J-2026-11-23-D) ; sur D-0158 (J-2026-11-23-E), T-0158 rejoint L-0023, et L-0034, le dernier lot du jalon, prend T-0156, T-0157, T-0159 et T-0160. B-0334 (la ligne « CI » de l'état après la fusion) et B-0335 (la règle de ce placement) y entrent, leurs tâches dans L-0024 et L-0026.

Le 24 novembre, sur D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`) : 25 de ses besoins s'abandonnent et le quittent ; B-0274 est satisfait ; il garde treize besoins ouverts, en quatre lots, L-0035, L-0010, L-0024 et L-0032.

Le 24 novembre, sur la revue de cap 5 (J-2026-11-24-AU), Théo y range les corrections du produit restées hors de tout jalon, B-0344, B-0345 et B-0347 (D-0180), et B-0350, l'attente de la CI du gabarit de `socle-batch` (D-0181) ; le lot de corrections devient le prochain lot, avant L-0032 (J-2026-11-24-AV).
