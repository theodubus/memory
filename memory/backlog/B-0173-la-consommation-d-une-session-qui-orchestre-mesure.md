<!-- socle: couche=backlog zone=publique -->
# B-0173 — La consommation d'une session qui orchestre : mesurer ce qui pèse, puis écrire les règles qui la bornent

> statut : ouvert · origine : J-2026-11-11-R · priorité : haute · lu : backlog@e69f45bc

Le 11 novembre, une session qui orchestre des sous-agents a vidé deux
fenêtres de cinq heures, la seconde en moins d'une demi-heure, et pris
plus de trente points de la semaine (J-2026-11-11-P, J-2026-11-11-R). Théo
demande si un sujet doit porter la consommation : « Sous agents, modèles,
gestion du contexte lu, compactage/demande de compactage ou autre ? Ou
c'est uniquement lié a fable et disparaîtra quand je ferais tout de
nouveau avec opus ».

Le modèle ne change que le prix de chaque lecture. Ce qui pèse tient à la
façon de travailler, et reste avec un autre modèle :

- la conversation principale se relit à chaque appel ; elle grossit
  jusqu'au compactage (B-0156) ;
- après une pause longue, une limite par exemple, tout se relit au prix
  fort : la conversation, et chaque sous-agent qu'on reprend ;
- chaque sous-agent a son contexte ; en lancer plusieurs à la fois
  multiplie la dépense, et le reprendre après sa revue le fait relire ;
- ce que le socle injecte : l'état à chaque démarrage, compactage et
  reprise (B-0010), les messages des hooks, le dossier de revue.

Rien de cela n'est mesuré : la session ne voit que le pourcentage de ses
fenêtres. À mesurer d'abord, sur une journée d'orchestration ; puis écrire
dans la méthode ce qui la borne : quand compacter ou le demander, combien
de sous-agents à la fois, quand reprendre un sous-agent plutôt qu'en
lancer un neuf, quel modèle pour quel travail, que faire à l'approche
d'une limite.

Le 12 novembre, Théo en fait une priorité (J-2026-11-12-L) : « a chaque
fois que tu relis apres limite on se mange 50% de la limite de session
d'un coup / Traiter ce problème est classé prioritaire ? ». Mesuré sur
cette session : à chaque reprise après une limite, la conversation longue
et ses sous-agents se relisent au prix fort, et la moitié de la fenêtre de
cinq heures part avant tout travail. Pistes à peser d'abord : compacter à
la fin de chaque lot et avant une attente longue ; intégrer soi-même les
petits lots plutôt que de reprendre un sous-agent ; un réveil qui ouvre
une session neuve, lue depuis la mémoire, au lieu de reprendre la longue.
Le sujet n'attend plus chess, qui est installé.

Un premier chiffre, le 12 novembre au soir (J-2026-11-12-M) : à la reprise
après la limite, un seul appel, la relecture à froid de la conversation
longue, prend 39 points de la fenêtre de cinq heures et 6 de la semaine ;
le compactage qui suit, 12 points.

## Fait quand

- [ ] une mesure dit, sur une journée d'orchestration, ce que pèsent la conversation principale, les sous-agents et les reprises après une pause
- [ ] ce que le socle injecte à chaque démarrage, compactage et reprise est mesuré, et borné si c'est lui qui pèse (B-0010)
- [ ] la méthode de délégation dit quand compacter, combien de sous-agents à la fois, quand en reprendre un, quel modèle pour quoi, et que faire à l'approche d'une limite
