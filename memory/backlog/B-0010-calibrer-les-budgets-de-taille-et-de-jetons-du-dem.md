<!-- socle: couche=backlog zone=publique -->
# B-0010 — Calibrer les budgets de taille et de jetons du démarrage

> statut : ouvert · origine : fichier:memory/archives/cadrage-2026-10-10.md · priorité : haute

Question ouverte du cadrage. Les valeurs par défaut des garde-fous sont des
hypothèses ; chess donne un point de mesure (F-0005).

Repris par la proposition 1 de D-0093@333ad9d0, validée le 10 novembre : l'état au
démarrage sous 10 Ko (les dix dernières décisions et leur nombre, les
faits par leur titre, le reste lu à la demande), sans attendre le pilote,
dans le jalon B-0154.

Le 12 novembre, la mesure de B-0173 (J-2026-11-12-N) le rend pressant :
l'état injecté au démarrage fait 24 à 28 Ko, et Claude Code ne transmet à
l'agent qu'un aperçu de 2 Ko, avec le chemin du fichier complet, que
l'agent ne relit pas. Le chantier actif et les faits ne lui parviennent
donc pas, ni ici ni sur chess ; la session de ce dépôt l'a vu à chaque
reprise du 12 au soir. La borne de D-0093 doit tenir sous ce que Claude
Code transmet entier, ou l'essentiel dans les premiers 2 Ko. C'est aussi
ce qui permet de continuer un travail dans une session neuve
(J-2026-11-12-O). Théo le passe en priorité haute, juste après B-0173
(D-0107) : « Ok pour augmenter la priorité de B0010 juste apres B0173 ».
