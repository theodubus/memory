# Le prompt de la mise à jour du socle sur chess

À coller dans une session de chess, qui tourne sur un autre compte et ne lit
pas ce dépôt. Il met à jour le socle installé le 26 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-26.md`) vers la version
publiée, et dit à l'agent de chess ce qui change pour lui, comme Théo l'a
demandé.

Récrit le 26 novembre pour la mise à jour suivante (L-0046) : celle du
26 novembre a suivi la version précédente de ce prompt, ses 37 points par
thème pour les notes d'après le 13 novembre (T-0186, commit `f24ebfec`),
et chess a reçu toutes les notes jusqu'à `2026-11-26-c`. Les points
d'ici ne couvrent que les notes d'après elle, dans
`engine/socle/CHANGES.md`. Chaque point dit la règle d'aujourd'hui et
finit par les identifiants des notes qu'il couvre ; d'une note qu'une plus
récente remplace, il ne garde que la règle qui reste. Chaque point vaut
dans une session cloud de chess, où le proxy refuse la suppression d'une
branche. Le prompt reste cumulatif : d'ici la mise à jour, chaque lot qui
change ce que chess reçoit ajoute sa note au point de son thème
(J-2026-11-13-L).

````text
Mets à jour le socle de ce dépôt depuis son dépôt public, sans ajouter ce dépôt à la session. Lis d'abord ce qui change, puis fais la mise à jour.

## Ce qui change depuis ta version

Ta version date du 26 novembre. L'installeur t'imprimera les notes de version que ta copie n'a pas, en entier celles qui te demandent quelque chose, puis le seul titre des autres. Ce qui suit les regroupe par thème et dit ce qu'elles changent pour chess ; chaque point finit par les identifiants des notes qu'il couvre. Le détail d'une note se lit dans .socle/engine/socle/CHANGES.md.

### La mise à jour et l'installeur

1. Le propriétaire du CODEOWNERS. Relancé sans --owner, l'installeur lit désormais le propriétaire sur la ligne de ton CODEOWNERS qui protège la politique (/.socle/), complète le fichier avec les lignes que son gabarit a en plus, et le dit (« CODEOWNERS : <propriétaire> … ») : la ligne « !! aucun propriétaire (--owner) » de ta gêne 2 ne doit plus paraître. Ne redonne pas --owner. Si elle paraît encore, rapporte-la mot pour mot. (2026-11-26-d)

2. Les notes d'une copie qui n'en avait pas. Quand la copie remplacée n'avait pas de notes de version, l'installeur n'imprime plus en entier que celles d'après le jour de son dernier commit, les autres par leur seul titre, sous une ligne qui les compte (ta gêne 7). Ta copie a désormais ses notes : ce cas ne te concerne plus, et tu ne reçois que les notes nouvelles. (2026-11-26-g)

### Les contrôles et la fin de tour

3. Un correctif de la mémoire. Un commit dont le sujet suit le motif d'un correctif (« Correction : … ») et qui ne change que des fichiers de la mémoire n'est plus refusé par tests.regression : il s'avertit, « correctif qui ne touche que la mémoire : non jugé » (ta gêne 4). Un correctif qui touche aussi du code reste jugé comme avant. (2026-11-26-e)

4. Une commande citée dans « Pour toi ». La fin de tour ne prend plus le nom d'une commande du socle, prune-branches par exemple, cité entre accents graves sur une ligne qui dit supprimer une branche, pour une branche à chercher à l'origine (ta gêne 5). (2026-11-26-f)

## La mise à jour

1. Si le clone est superficiel (git rev-parse --is-shallow-repository répond true), complète son historique : git fetch --unshallow.
2. Clone le socle à jour, après avoir supprimé un /tmp/socle resté d'avant :
   git clone --depth 1 https://github.com/theodubus/socle /tmp/socle
3. Sur une branche de travail neuve depuis main, à la racine du dépôt :
   PYTHONPATH=/tmp/socle python3 -m socle install --target .
   Ne redonne ni l'adaptateur ni --owner : ceux de chess sont en place, et ils sont gardés.
4. Lis les notes de version que l'installeur imprime en entier, et fais ce que chacune demande. Puis lis le reste de ce qu'il dit, et vérifie :
   - sa ligne sur CODEOWNERS (point 1) ;
   - python3 .socle/socle state : sa taille (python3 .socle/socle state | wc -c, sous 9 500), et s'il finit par une ligne « !! coupé » ;
   - rien de changé dans ta politique ni dans ton adaptateur ; ta liste [adoption.tolerated] inchangée.
5. Suis les étapes « Et maintenant » de l'installeur, dans son ordre : la demande qui cite chaque fichier protégé changé avec son empreinte, poussée seule, puis les fichiers commités et poussés, pour que je les lise dans la pull request avant de répondre. Donne-moi son lien, et attends ma réponse.
6. La porte, avant de me demander de fusionner : python3 .socle/socle verify --fast --redo, python3 .socle/socle ci et tools/verify.sh --rapide passent. Donne-moi les durées.
7. Ouvre la pull request, et dis-moi ce qui me revient. Ne la fusionne pas : je la fusionne après avoir lu ton compte rendu.

Rends-moi compte, court : les identifiants des notes de version qu'il t'a données en entier, et ce que tu en as fait ; sa ligne sur CODEOWNERS, mot pour mot ; la taille de l'état avant et après, et s'il est coupé ; les fichiers protégés changés ; chaque refus du hook pendant la mise à jour, avec sa commande ; les lignes « CI » et « branche » de l'état après le push, et si l'état me donne une action ; tout ce qui t'a gêné.
````
