# Le prompt de la mise à jour du socle sur chess

À coller dans une session de chess, qui tourne sur un autre compte et ne lit
pas ce dépôt. Il met à jour le socle installé le 28 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-28.md`) vers la version
publiée, et dit à l'agent de chess ce qui change pour lui, comme Théo l'a
demandé.

Récrit le 28 novembre pour la mise à jour suivante (T-0229) : celle du
28 novembre a suivi la version de L-0057, et chess a reçu toutes les
notes jusqu'à `2026-11-27-l`. Les points d'ici ne couvrent que les notes
d'après elle, dans `engine/socle/CHANGES.md`. Chaque point dit la règle
d'aujourd'hui et finit par les identifiants des notes qu'il couvre ; d'une
note qu'une plus récente remplace, il ne garde que la règle qui reste.
Chaque point vaut dans une session cloud de chess, où le proxy refuse la
suppression d'une branche. Le prompt reste cumulatif : d'ici la mise à
jour, chaque lot qui change ce que chess reçoit ajoute sa note au point de
son thème (J-2026-11-13-L). Il ne fait pas écrire un même texte dans deux
entrées, ni vérifier sur un clone fabriqué ce qu'un test joue déjà
(J-2026-11-28-A).

````text
Mets à jour le socle de ce dépôt depuis son dépôt public, sans ajouter ce dépôt à la session. Lis d'abord ce qui change, puis fais la mise à jour.

## Ce qui change depuis ta version

Ta version date du 28 novembre. L'installeur t'imprimera les notes de version que ta copie n'a pas, en entier celles qui te demandent quelque chose, puis le seul titre des autres. Ce qui suit les regroupe par thème et dit ce qu'elles changent pour chess ; chaque point finit par les identifiants des notes qu'il couvre. Le détail d'une note se lit dans .socle/engine/socle/CHANGES.md.

### La mémoire et le backlog

1. Clore un besoin qui n'a jamais eu de tâche. socle close B-NNNN clôt désormais « fait », en un geste, un besoin qui n'a jamais eu de tâche, une attente levée ou un besoin pour moi, sur sa section « Satisfait quand », qui a au moins une case et les a toutes cochées (ta gêne 1 du 28 novembre, B-0084). Un besoin qui a eu des tâches garde la règle d'avant : closes, l'une au moins faite ; toutes abandonnées, il s'abandonne. socle state ne dit plus « à fermer » qu'un besoin que socle close accepterait. Une attente que rien ne lève encore se met au statut bloqué, qui la sort des besoins à découper, B-0083 par exemple tant que son critère n'est pas constaté. Si une clôture te coûte encore plus d'un geste, rapporte-moi lesquels, et le refus mot pour mot. (2026-11-28-a)

## La mise à jour

1. Si le clone est superficiel (git rev-parse --is-shallow-repository répond true), complète son historique : git fetch --unshallow.
2. Clone le socle à jour, après avoir supprimé un /tmp/socle resté d'avant :
   git clone --depth 1 https://github.com/theodubus/socle /tmp/socle
3. Sur une branche de travail neuve depuis main, à la racine du dépôt :
   PYTHONPATH=/tmp/socle python3 -m socle install --target .
   Ne redonne ni l'adaptateur ni --owner : ceux de chess sont en place, et ils sont gardés.
4. Lis les notes de version que l'installeur imprime en entier, et fais ce que chacune demande. Puis lis le reste de ce qu'il dit, et vérifie :
   - sa ligne sur CODEOWNERS ;
   - python3 .socle/socle state : sa taille (python3 .socle/socle state | wc -c, sous 9 500), et s'il finit par une ligne « !! coupé » ;
   - rien de changé dans ta politique ni dans ton adaptateur ; ta liste [adoption.tolerated] inchangée.
5. Suis les étapes « Et maintenant » de l'installeur, dans son ordre : la demande qui cite chaque fichier protégé changé avec son empreinte, poussée seule, puis les fichiers commités et poussés, pour que je les lise dans la pull request avant de répondre.
6. La porte, avant de me demander de fusionner : python3 .socle/socle verify --fast --redo, python3 .socle/socle ci et tools/verify.sh --rapide passent. Donne-moi les durées.
7. Ouvre la pull request, et dis-moi ce qui me revient. Ne la fusionne pas : je la fusionne après avoir lu ton compte rendu.

Rends-moi compte, court : les identifiants des notes de version qu'il t'a données en entier, et ce que tu en as fait ; sa ligne sur CODEOWNERS, mot pour mot ; la taille de l'état avant et après, et s'il est coupé ; les fichiers protégés changés ; chaque refus du hook pendant la mise à jour, avec sa commande ; les lignes « CI » et « branche » de l'état après le push, et si l'état me donne une action ; tout ce qui t'a gêné.
````
