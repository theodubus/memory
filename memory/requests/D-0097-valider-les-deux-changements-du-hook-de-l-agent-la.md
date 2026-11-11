<!-- socle: couche=demandes zone=publique -->
# D-0097 — Valider les deux changements du hook de l'agent : la fin de tour ne relance plus un échec inchangé, l'installeur hors mode est refusé

> date : 2026-11-11 · forme : séance

## Question posée

Deux sujets du lot livré avant chess changent le hook de l'agent, le
programme du socle qui juge ses commandes et vérifie son travail en fin de
tour ; le projet veut l'accord de Théo pour y toucher. L'agent les lui a
expliqués dans la conversation et recommandait de valider les deux.

1. Fin de tour (ADR-0061) : quand un contrôle est rouge, le hook renvoie
   l'agent corriger, jusqu'à trois fois. Il cesse désormais dès que
   l'échec est le même et que l'arbre n'a pas changé ; l'échec reste
   affiché à l'humain, et le commit, le push et la CI refusent toujours.
2. Installeur (ADR-0062) : le hook refuse l'installeur visé sur un projet
   équipé dans un autre mode que le sien, ou sur une cible qu'il ne sait
   pas lire ; la mise à jour normale passe toujours.
