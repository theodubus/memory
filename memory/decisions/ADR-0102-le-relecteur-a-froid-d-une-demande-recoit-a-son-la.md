<!-- socle: couche=decisions zone=publique -->
# ADR-0102 — Le relecteur à froid d'une demande reçoit à son lancement le modèle le plus capable jusqu'à Opus, comme celui d'un lot, et non celui de la session

> statut : acceptée · date : 2026-11-20 · source : B-0243@db88be3c, T-0074@0dfd5dfa, D-0117@0e7cde01, D-0119@c39e11d7, B-0197@8440dcbc, ADR-0046@1017e7f0, J-2026-11-19-F@fb7cf3dd, J-2026-11-19-P@c8038dde, J-2026-11-20-P@82233e21 · lu : decisions@103da660

## Contexte

Le skill `socle-request` fait relire une demande à froid, avant de la
pousser (ADR-0046@1017e7f0), par un sous-agent « du modèle de la
session ». La règle du modèle du skill `socle-batch` peut faire ce modèle
moins coûteux pour la conversation qui orchestre ; or ce relecteur joue
l'humain qui décide sur ce seul texte. D-0117@0e7cde01 donne au relecteur
d'un lot le modèle le plus capable disponible jusqu'à Opus, découplé de
celui de la session, et Fable seulement si l'humain le demande ; elle ne
vise pas la relecture d'une demande (B-0243@db88be3c, T-0074@0dfd5dfa).

Ce que coûte cette relecture, mesuré au journal sur les quatre
dernières : sur Opus, 83 000 jetons et une minute et demie pour
D-0137@8a882c42 (J-2026-11-19-F@fb7cf3dd), 79 000 et une minute et quart pour
D-0138@f8ca9924 (J-2026-11-19-P@c8038dde), 77 823 pour D-0147@ffd624cc
(J-2026-11-20-P@82233e21), 83 817 pour D-0148@e43922c7 ; environ 3 points de la
fenêtre de cinq heures. B-0197@8440dcbc en relevait 131 786 sur un autre
projet, le 13 novembre. Un
relecteur de lot en coûte de 263 000 à 344 000, et de 12 à 23 points. Et
chacune de ces quatre relectures a fait corriger de 19 à 23 points de la
demande sur 21 à 26.

## Décision

1. **Le relecteur à froid d'une demande reçoit explicitement à son
   lancement (`model`) le modèle le plus capable disponible jusqu'à
   Opus**, quel que soit celui de la session, sur la dernière version de
   sa famille : un alias qui en désigne une plus ancienne, il hérite de
   la session, sans `model`. Fable, s'il est disponible, seulement si
   l'humain le demande, comme pour le relecteur d'un lot (D-0117,
   D-0119@c39e11d7).
2. **Le récap nomme le modèle qui l'a servi**, avec ce qu'il a relevé :
   `Relecture à froid (<modèle>) : <n> points, <k> corrigés`.
3. Le skill du produit nomme le modèle par sa famille, jamais par un
   identifiant daté ni par un modèle de ce dépôt.

Pourquoi pas celui de la session : ce relecteur est le dernier regard
avant celui de l'humain, sur une décision qui lui revient ; un modèle
moindre y perd ce que les mesures montrent qu'il trouve, pour une
économie de l'ordre de 3 points d'une fenêtre, que la règle de
`socle-batch` (jamais un moindre modèle pour tenir une limite) refuse
déjà.

## Conséquences

Le gabarit du skill `socle-request`, en français et en anglais, le dit à
l'étape de la relecture à froid ; sa copie protégée de ce dépôt suit par
T-0072@f84a75da. B-0243 garde son premier critère, le lot implémenté sur Fable
(D-0119). Le défaire : rendre au relecteur le modèle de la session, en
retirant la phrase du skill.
