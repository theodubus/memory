<!-- socle: couche=decisions zone=publique -->
# ADR-0052 — La mise à jour ne rafraîchit une copie d'adaptateur que si le projet ne l'a pas adaptée

> statut : acceptée · date : 2026-11-09 · validation : D-0085@c6c57892 · source : ADR-0051@96428594, J-2026-11-09-H@94a255f0, J-2026-11-09-L@5dc531f1, B-0095@65dbe4c6 · lu : decisions@d2d7770a

## Contexte

ADR-0051 recopie la spécification des adaptateurs multiples que Théo a
validée (D-0083@054ce997). Son point 6 finit par : « La mise à jour rafraîchit
chaque copie d'un adaptateur maintenu, que vous approuvez comme tout
fichier protégé » ; son point 7 dit qu'« un projet à un seul langage ne
change rien ». Le code fusionné ne rafraîchissait que les copies des
autres langages, une lecture que j'avais tranchée seul ; la revue l'a
relevé, et qu'un rafraîchissement défait le resserrement de motifs que
prescrit le point 2 (J-2026-11-09-H@94a255f0, constat 10). Une copie
s'adapte aussi au projet : des commandes en plus, les fichiers que la
mutation couvre, les commandes de Gradle d'un projet Android. D-0085 a posé
la question ; Théo a répondu `valider` (J-2026-11-09-L@5dc531f1).

## Décision

1. *Le texte validé*, qui remplace la dernière phrase du point 6
   d'ADR-0051 ; le reste d'ADR-0051 tient. « La mise à jour rafraîchit
   chaque copie d'un adaptateur maintenu que le projet n'a pas adaptée ;
   une copie adaptée se garde, et la mise à jour dit quand son adaptateur
   maintenu a changé. » La copie principale, `.socle/adapter.toml`, en est :
   le point 7 se lit désormais avec cette exception, sans qu'un projet à un
   seul langage y perde rien, puisque seule une copie non adaptée change.

Son application, que je décide (politique, point 3 : réversible et
mesurable) :

2. *Non adaptée.* Une copie n'est pas adaptée quand son texte est, à
   l'identique, une version de son adaptateur maintenu que le moteur du
   projet a portée : celle du moteur installé, lue avant qu'il ne soit
   remplacé, ou une de celles que l'historique git du projet a eues sous
   `**/socle/adapters/<nom>.toml`. L'historique compte pour la copie
   principale, qu'aucune mise à jour ne rafraîchissait : posée par une
   version plus ancienne, elle peut n'être identique à aucune du moteur
   installé sans que le projet y ait touché. Un premier passage de
   l'installeur, sans moteur installé, ne rafraîchit rien.
3. *Son adaptateur maintenu.* Pour une copie `.socle/adapters/<nom>.toml`,
   celui de son nom. Pour la principale, celui dont elle porte une version ;
   adaptée, celui de son langage (`language`) dont le texte est le plus
   proche du sien, `python` et `python-pytest` partageant Python. Sans
   adaptateur maintenu, une copie est propre au projet, et se garde comme
   avant.
4. *Dire.* Une copie adaptée dont l'adaptateur maintenu a changé depuis le
   moteur installé, ou n'y était pas, se garde avec un avertissement de
   l'installeur (`!!`) qui nomme ce qui a changé
   (`git diff -- <moteur>/socle/adapters/<nom>.toml`) et dit d'en proposer
   le report à l'humain par une demande. Une copie adaptée dont
   l'adaptateur n'a pas changé se garde, sur une ligne.
5. *La CI et le balayage* se génèrent des copies telles qu'elles sont
   après la mise à jour, non des adaptateurs maintenus nommés : une copie
   gardée y garde ses adaptations, ses étapes de CI comprises. Nommer, pour
   le langage de la copie principale, un autre adaptateur maintenu que le
   sien (`python` sur une copie de `python-pytest`) en fait la CI, comme
   avant.

## Conséquences

À la mise à jour de JustCook, sa copie Kotlin se pose, puisqu'il n'en a
pas ; sa copie Python se rafraîchit si elle est une version de son
adaptateur maintenu, et se garde sinon, l'installeur le disant. Aux mises
à jour suivantes, une copie Kotlin adaptée à Android se garde.

Ce qui reste supposé : que l'agent d'un projet donne suite à
l'avertissement d'un adaptateur maintenu qui a changé ; sinon, une copie
adaptée vieillit. Une copie qu'un projet aurait ramenée exprès à une
version ancienne de l'adaptateur maintenu se rafraîchirait, sous
l'approbation de l'humain. La défaire : une demande ; la règle tient dans
`rafraichir_copie` de l'installeur, et ses tests dans
`tests/test_adaptateurs_multiples.py`.
