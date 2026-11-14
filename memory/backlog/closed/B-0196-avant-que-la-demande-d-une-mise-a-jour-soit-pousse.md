<!-- socle: couche=backlog zone=publique -->
# B-0196 — Avant que la demande d'une mise à jour soit poussée, la fin de tour refuse l'arbre par une ligne en échec pour chaque fichier protégé changé

> statut : fait · origine : J-2026-11-13-D · priorité : haute · lu : backlog@8f4711b1 · ref : J-2026-11-14-P

Relevé à la mise à jour du socle sur chess, le 13 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-13.md`, gêne 3).

Entre l'installation et le push de la demande qui couvre les fichiers
protégés changés, la fin de tour refuse l'arbre : 26 lignes en échec,
une par fichier, chacune avec sa commande de remise en état, environ
17 Ko de contexte relu ensuite à chaque appel. La cause est une, la
demande pas encore posée : une ligne qui le dit (« une mise à jour attend
sa demande : la poser ») suffirait, la liste restant lisible à la demande.
Une fois la demande poussée, ce n'est plus qu'un avertissement.

Le 13 novembre, Théo retient la priorité haute proposée (D-0108@96eeead5) :
le sujet fait partie de ceux à finir avant de revenir aux nouvelles
fonctions.

## Modèle de menace

Le garde-fou reste `protege.fichiers`, sans rien relâcher : son erreur
par fichier reste au rapport, `socle check` la liste, `socle approve`
l'approuve, le commit et la CI refusent jusqu'à la validation qui cite
chaque fichier et son empreinte. Seul change ce que la fin de tour
affiche et, pour un fichier qu'une mise à jour a posé, le message de son
erreur, qui ne dit plus de le remettre en état.

Ce qu'il arrête : la fin de tour qui redit à l'agent, à chaque tentative,
une ligne et une commande de remise par fichier qu'une mise à jour du
socle a posé, quand la cause est une, la demande pas encore posée ; et
l'agent qui, suivant ces commandes, défairait la mise à jour.

Ce qui garde sa ligne et sa commande de remise : un fichier protégé
changé hors d'une mise à jour ; pendant une mise à jour, un fichier
qu'elle n'a pas posé tel qu'il est, changé avant le passage de
l'installeur (même si celui-ci le fusionne ensuite, comme les réglages de
Claude Code) ou après ; tout fichier, si le moteur de l'arbre n'est plus
celui que le verrou décrit.

Ce qu'il laisse passer : rien de plus au commit ni à la CI. À la fin du
tour, un fichier dont l'agent forgerait l'origine en écrivant le verrou
du moteur, ce que son hook refuse, entrerait dans la ligne commune au lieu
d'avoir la sienne ; il reste une erreur que `socle check` nomme, et que
l'humain lit dans la demande et la pull request. Hors de l'arbre de
travail (le hook avant commit, qui juge l'index ; la CI), rien ne change.

## Fait quand

- [x] après une mise à jour dont la demande n'est pas posée, la fin de tour le dit en une ligne au lieu d'une ligne par fichier, et un test le montre
