<!-- socle: couche=backlog zone=publique -->
# B-0389 — La passation programmée part sans vérifier que le lot tient dans la fenêtre, et la clôture d'un lot n'inscrit pas son coût

> statut : ouvert · origine : J-2026-11-28-D · lu : backlog@68df6bf7

Le constat 1 du relevé d'après de chess
(`docs/fabrication/chess/cout-et-frictions-2026-11-28.md`). Le skill
`socle-handoff` dit qu'une session ne part que si le coût estimé de son
lot tient dans ce qui reste de la fenêtre de cinq heures, la marge du
rangement comprise. Chez chess, une session a programmé la suivante « la
minute qui suit », sans estimation écrite ; celle-ci a démarré à 68 % de
la fenêtre et fini son lot ordinaire à 89 %, au seuil du rangement, et
le tri de la réserve a été reporté. Ni `socle handoff write --scheduled`
ni `socle handoff check` ne lisent l'utilisation. Le skill `socle-batch`
fait noter au journal le coût de chaque sous-agent, du relecteur, des
demandes et du rangement, pas celui du lot entier : aucun coût de lot
n'avait été mesuré chez chess.

Le moteur ne lit pas l'utilisation des fenêtres, que seuls les outils de
la plateforme donnent : l'agent la lui passerait. Deux voies, dont le
choix revient à Théo, par sa question d'intention avant la conception :
une passation programmée qui exige l'utilisation des deux fenêtres et le
coût estimé du lot, et recule elle-même son heure à la remise à zéro ;
ou la seule règle des skills, précisée.

## Satisfait quand

- [ ] une session programmée ne part que quand le coût estimé de son lot tient dans ce qui reste de chaque fenêtre, la marge du rangement comprise, et la passation dit sur quels chiffres
- [ ] la clôture d'un lot inscrit au journal l'utilisation de chaque fenêtre à son annonce et à sa clôture
