<!-- socle: couche=backlog zone=publique -->
# B-0106 — Approuver depuis une session cloud les fichiers protégés qu'une mise à jour du socle change : socle approve exige un terminal

> statut : ouvert · origine : J-2026-10-31-G · lu : backlog@ed7e2136

Mettre à jour le socle d'un projet change ses fichiers protégés : le
moteur sous `.socle/`, ses hooks, le réglage de Claude Code, les skills du
socle, la CI. L'installeur dit alors à l'humain de lancer `socle approve`,
qui les approuve d'un coup ; mais cette commande refuse de tourner sous un
agent, et en session cloud l'humain n'a pas de terminal. Le pilote, mené
depuis un téléphone, le rencontrera à sa première mise à jour.

Ce qui marche aujourd'hui : une demande qui cite chaque fichier protégé
changé avec son empreinte (`socle check` les donne), que l'humain valide
dans la conversation et que l'agent relaie ; elle peut compter des dizaines
de lignes. Piste : `socle approve --relayed --by <nom> --quote-file
<fichier>`, comme `socle answer`, `socle decision` et `socle reviewed`,
l'humain ayant donné son accord dans la conversation ; c'est relâcher un
refus du hook, à décider par Théo. Et l'étape que l'installeur affiche
devrait dire le chemin cloud.
