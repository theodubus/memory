<!-- socle: couche=demandes zone=publique -->
# D-0071 — B-0106 : commiter sous une demande en attente les fichiers protégés qu'une mise à jour change, ou garder le chemin actuel ?

> date : 2026-11-02

## Décision demandée

Quand une mise à jour du socle change des fichiers protégés, l'agent
peut-il les commiter et les pousser dès que la demande qui les cite est
poussée, la CI restant rouge jusqu'à votre réponse, au lieu de les garder
non commités dans son conteneur ?

## Contexte

Une mise à jour du socle change des fichiers protégés : le moteur, ses
hooks, le réglage de Claude Code, les skills du socle, la CI. Aucun ne se
commite sans votre approbation. Dans un terminal, vous lancez
`socle approve`. En session cloud, vous n'avez pas de terminal : l'agent
pose une demande qui cite chaque fichier changé avec son empreinte, vous la
validez dans la conversation, et il commite alors les fichiers. Ce chemin
marche : le pilote l'a suivi le 2 novembre, pour vingt fichiers.

Mais pendant l'attente, deux choses gênent. D'abord, les vingt fichiers
restent non commités, dans le conteneur de l'agent : vous validez des
empreintes sans pouvoir lire les fichiers, que GitHub ne montre pas.
Ensuite, la session cloud rappelle à l'agent, à chaque fin de tour, qu'il a
des changements non commités ; l'agent du pilote a répondu trois fois la
même chose. Ce rappel vient de la session cloud, pas du socle.

L'idée de départ de B-0106, une commande `socle approve` que l'agent
relaierait comme une réponse, ne change rien à l'attente : la demande joue
déjà ce rôle. La question est donc où attendent les fichiers.

## Éléments cités

- B-0106@b347b4da — le sujet : approuver depuis une session cloud les
  fichiers protégés qu'une mise à jour change, avec le retour du pilote du
  2 novembre.
- B-0115@dd1e5c4c — le correctif qui laisse finir le tour d'une session
  cloud dont les fichiers protégés attendent une demande poussée qui les
  cite, le commit et la CI attendant la réponse.
- D-0060@d5635b2c — la demande par laquelle vous avez validé, le 1er
  novembre, les cinq fichiers protégés que l'installeur avait rafraîchis
  dans ce dépôt : le chemin actuel, suivi ici.

## Où regarder

- [B-0106](https://github.com/theodubus/memory/blob/92f22a9b7db5c7a43fdf0209e21406ef22b4706a/memory/backlog/B-0106-approuver-depuis-une-session-cloud-les-fichiers-pr.md) :
  le sujet, et à sa fin ce que la mise à jour du pilote a montré.
- [D-0060](https://github.com/theodubus/memory/blob/92f22a9b7db5c7a43fdf0209e21406ef22b4706a/memory/requests/D-0060-valider-le-rafraichissement-des-cinq-fichiers-prot.md) :
  une demande du chemin actuel. Vérifier que vous n'y aviez que des
  empreintes à valider, sans le contenu des fichiers.

## Options

- **Commiter sous la demande en attente** (recommandée). Une fois la
  demande poussée, les hooks de l'agent et de git acceptent de commiter et
  de pousser les fichiers protégés qu'elle cite, avec ces empreintes. La CI
  les refuse toujours, rouge jusqu'à votre réponse ; votre validation,
  relayée et poussée, la remet au vert. Les fichiers sont dans la pull
  request, que vous lisez sur GitHub avant de valider ; rien n'attend dans
  le conteneur. Pour qu'une pull request rouge ne puisse pas se fusionner
  par mégarde, cela ne vaut que si la branche par défaut exige la CI du
  socle avant toute fusion, comme l'installation le conseille ; sinon, le
  chemin actuel reste. Effort : moyen (les hooks, l'auto-test, le guide).
  Risque : la défense locale ne retient plus un changement protégé qu'une
  demande en attente cite ; la CI et la fusion qui l'exige le retiennent
  encore. Réversible.
- **Garder le chemin actuel.** Les fichiers attendent non commités dans le
  conteneur, jusqu'à votre réponse. Effort nul. Risque : vous validez sans
  voir les fichiers, et la session cloud rappelle à chaque tour les
  changements non commités. Réversible.

## Conséquences

Si vous validez, l'agent écrit le changement des hooks, son défaut injecté
et son témoin, et le guide ; il vous le livre dans la prochaine pull
request. Si vous refusez, B-0106 se clôt, abandonné, et le chemin actuel
reste celui du guide. Sans réponse, rien ne change : le chemin actuel
marche, et l'agent travaille sur autre chose.

## Recommandation

Commiter sous la demande en attente. Vérifié : le chemin actuel marche
(le pilote, le 2 novembre ; ce dépôt, avec D-0060), et la CI refuse un
fichier protégé qu'aucune demande validée ne cite. Supposé : que vous
préfériez lire les fichiers sur GitHub plutôt que valider des empreintes,
et que les rappels de la session cloud gênent plus que la défense locale
ne protège, la CI et la fusion qui l'exige restant en place.

## Réponses possibles

- `valider` — l'agent commitera les fichiers protégés d'une mise à jour sous la demande en attente qui les cite, quand la branche par défaut exige la CI du socle ; la CI reste rouge jusqu'à votre réponse.
- `refuser` — le chemin actuel reste ; B-0106 se clôt, abandonné.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
