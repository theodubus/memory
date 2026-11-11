<!-- socle: couche=demandes zone=publique -->
# D-0101 — B-0169 : un commit qui ne touche que des fichiers tiers échappe-t-il à la trace des hooks, y compris sous les déclarations déjà approuvées (A), ou faut-il une clé distincte (B) ?

> date : 2026-11-11 · forme : séance

## Question posée

Déclarer un dossier « tiers » (`[thirdparty] paths`) retire aujourd'hui ses fichiers des contrôles (ADR-0031). Pour que les pull requests d'un autre agent, qui ne travaille que sous ce dossier, passent la CI du projet, le lot B-0169 ajoute : un commit à un parent qui ne touche que des fichiers tiers n'est plus jugé par `hooks.trace` ni par les dispenses de test ; un commit qui touche aussi un fichier du projet reste jugé en entier.

La revue adversariale relève que cela élargit aussi ce qu'exemptent les déclarations déjà approuvées, sur tout projet, et qu'une session de l'agent du projet démarrée sans hooks pourrait pousser des commits sous ce dossier sans que la CI le voie.

- A (recommandation de l'agent) : valider tel quel. Ces commits ne touchent que des fichiers qu'aucun contrôle ne juge déjà.
- B : la dispense demande une clé distincte, à approuver à part sur chaque projet ; les déclarations existantes ne changent pas de sens.

A ou B ?
