<!-- socle: couche=demandes zone=publique -->
# D-0056 — Publier le moteur du socle dans un dépôt public de distribution, dès maintenant

> date : 2026-10-31 · lu : decisions@4007cd0e

## Décision demandée

Choisir si le moteur du socle se publie dès maintenant dans un dépôt
public de distribution, sous quel nom, sous quelle licence, et qui le
publie.

## Contexte

Installer ou mettre à jour le socle dans un projet, en session cloud,
oblige à ajouter ce dépôt-ci, privé, à la session du projet : elle passe à
deux dépôts et, si son processus redémarre, repart hors de la racine du
projet, sans les hooks de l'agent. C'est arrivé à l'installation, puis à
la mise à jour du pilote, qui a laissé un brouillon dans un conteneur.
Un dépôt public se clone sans être ajouté à la session : la session du
projet reste à un seul dépôt, reprise ou non, et l'installation tient en
une commande. Le dépôt de distribution était prévu à la première version
mûre (B-0083@a1035592) ; Théo le veut maintenant s'il simplifie
(D-0055@67df13c6). Il ne contiendrait que le produit : le moteur, un
README de distribution qui dit l'installation, et une licence ; ce
dépôt-ci reste privé, avec l'atelier et sa mémoire. Le produit ne renvoie
nulle part à ce dépôt.

## Éléments cités

- B-0083@a1035592 — le sujet du dépôt de distribution, et ses questions : qui publie, le nom, les liens.
- D-0055@67df13c6 — la décision de Théo en séance : avancer B-0083 dès maintenant, s'il simplifie.

## Où regarder

- [le sujet B-0083](https://github.com/theodubus/memory/blob/ef1a76149342eab95f64c651b5e593135a95f2e1/memory/backlog/B-0083-un-depot-de-distribution-separe-a-la-premiere-vers.md) : ce qui était prévu, et les questions laissées ouvertes.
- [le moteur, ce qui serait publié](https://github.com/theodubus/memory/tree/ef1a76149342eab95f64c651b5e593135a95f2e1/engine/socle) : le seul contenu du dépôt public, avec un README et une licence.
- [l'installation dans le README actuel](https://github.com/theodubus/memory/blob/ef1a76149342eab95f64c651b5e593135a95f2e1/README.md#installation) : le clone partiel d'un dépôt privé, qui deviendrait un clone simple.

## Options

- **Option 1, un dépôt public publié à chaque fusion** : le dépôt `theodubus/socle`, public, sous licence MIT ; un workflow de ce dépôt-ci y copie le moteur, son README et sa licence à chaque fusion sur `main`, avec un jeton qui n'écrit que là. Les gestes de Théo : créer le dépôt vide, créer le jeton, l'ajouter en secret ici. Effort : une heure pour l'agent, dix minutes pour Théo. Risque : le code devient lisible par tous, et une publication ne se reprend pas tout à fait (une copie peut rester) ; le jeton est borné à ce seul dépôt. Peu réversible.
- **Option 2, la même sous licence Apache-2.0** : elle ajoute une clause de brevets et l'obligation de signaler les changements. Même effort et même risque. Peu réversible.
- **Option 3, publier à la main** : pas de jeton ; Théo pousse lui-même chaque version, avec une commande que l'agent prépare. Effort : quelques minutes à chaque version. Risque : le dépôt public prend du retard sur le moteur. Peu réversible.

## Conséquences

- Si Théo valide : l'agent écrit le workflow, le README de distribution et la licence, change l'installation dans le README, le guide et les prompts, et pose les trois gestes de Théo au backlog ; la session d'un projet n'ajoute plus aucun dépôt pour installer ou mettre à jour.
- S'il choisit l'option 2 ou 3 : la même chose, avec la licence Apache-2.0, ou sans workflow ni jeton.
- S'il refuse : rien n'est publié ; l'installation et la mise à jour gardent la procédure en deux sessions.
- Sans réponse : rien n'est publié, et la procédure en deux sessions reste.

## Recommandation

L'option 1 : elle supprime la cause des trois incidents sans geste à refaire à chaque version, et MIT est la licence la plus simple pour un outil personnel ouvert.

Vérifié : le produit ne contient aucun lien vers ce dépôt ; l'installation et la mise à jour ne lisent que le moteur.

Supposé : qu'une session cloud clone un dépôt public sans l'ajouter, le proxy git le servant d'ordinaire ; à vérifier sur la première installation.

## Réponses possibles

- `valider` — l'option 1 : `theodubus/socle`, public, licence MIT, publié par un workflow à chaque fusion.
- `apache` — l'option 2 : la même, sous licence Apache-2.0.
- `a-la-main` — l'option 3 : Théo publie lui-même chaque version.
- `refuser` — rien n'est publié pour l'instant.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
