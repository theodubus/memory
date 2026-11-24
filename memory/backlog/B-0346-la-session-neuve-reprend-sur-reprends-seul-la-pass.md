<!-- socle: couche=backlog zone=publique -->
# B-0346 — La session neuve reprend sur « reprends » seul : la passation écrite dans le dépôt, sans prompt à copier

> statut : ouvert · origine : J-2026-11-24-AF · ref : D-0174, B-0345 · lu : backlog@71f347c7

Le 24 novembre, Théo : « en vrai je me demande si le prompt est utile
tout court a donner à l'utilisateur, c'est typiquement un truc qui
pourrait faire partie de la passassion et que l'utilisateur puisse dire
uniquement "reprends" dans une nouvelle session non ? »
(J-2026-11-24-AF).

Aujourd'hui, en mode « prompt à copier », l'humain colle dans une
session neuve un prompt de neuf lignes, dont la garde (`socle handoff
check` et ses trois arguments) et le lot. La piste : la session qui
part écrit sa passation dans le dépôt (sa garde, le lot, ce qui
attend) ; la session neuve la lit au démarrage, lance la garde, et
l'humain n'a qu'à écrire « reprends », d'un compte comme d'un autre ;
la tâche programmée de la session programmée pourrait de même ne dire
que « reprends ». À trancher d'abord : la tête que la garde nomme quand
la passation est elle-même un commit, qui marque la passation reprise,
ce que fait « reprends » sans passation en attente, et ce que dit
l'état. Elle change la spécification validée par D-0174 : spécification
et demande avant le code, après des questions de cadrage à Théo si son
intention ne suffit pas.

## Satisfait quand

- [ ] une session neuve sur « reprends » seul reprend le travail que la passation dit, sa garde jugée, sans prompt à copier
- [ ] la spécification, soumise à Théo, est validée avant le code
