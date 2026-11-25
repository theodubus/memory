<!-- socle: couche=backlog zone=publique -->
# B-0346 — La session neuve reprend sur « reprends » seul : la passation écrite dans le dépôt, sans prompt à copier

> statut : ouvert · origine : J-2026-11-24-AF · ref : D-0174, B-0345, D-0177 · lu : backlog@71f347c7

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

Propositions de l'agent (J-2026-11-24-AG), retenues par Théo le 24
novembre (D-0177), pour la spécification :

- **La tête.** La passation est un fichier du dépôt, sans identifiant
  de commit : la garde prend pour tête le dernier commit qui l'a écrit,
  et pour heure la date de ce commit. Si la session qui part pousse
  encore, elle réécrit sa passation dans le même commit, et rien ne se
  périme.
- **Reprise.** La session neuve, sa garde acceptée, retire la
  passation dans son premier commit, poussé aussitôt : une autre
  session ouverte ensuite n'en trouve plus, ou voit la branche bouger
  et s'arrête.
- **Sans passation.** « reprends » fait ce que fait aujourd'hui une
  session neuve : l'état, le chantier actif, le prochain lot ; le
  premier message dit qu'aucune passation n'attendait.

## Satisfait quand

- [ ] une session neuve sur « reprends » seul reprend le travail que la passation dit, sa garde jugée, sans prompt à copier
- [x] la spécification, soumise à Théo, est validée avant le code
