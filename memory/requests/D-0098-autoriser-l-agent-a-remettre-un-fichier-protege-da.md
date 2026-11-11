<!-- socle: couche=demandes zone=publique -->
# D-0098 — Autoriser l'agent à remettre un fichier protégé dans l'état du dernier commit quand il a été modifié par erreur

> date : 2026-11-11 · forme : séance

## Question posée

B-0165 : quand un fichier protégé du projet (politique, hooks, CI, verrou
du moteur) est modifié par erreur dans l'arbre de travail, le hook refuse
à l'agent de le remettre en état, ce qu'il réserve à l'humain. En session
cloud, l'humain n'a pas la main sur le conteneur : la session reste
bloquée, comme le 9 novembre, quand un relecteur avait lancé l'installeur
par erreur. L'agent a demandé à Théo, dans la conversation, s'il
l'autorisait à remettre un fichier protégé dans l'état du dernier commit ;
le risque dit : effacer une modification que Théo aurait faite lui-même
dans le conteneur sans la commiter, ce qui n'arrive pas en session cloud.
C'est un assouplissement, que la politique lui réserve.
