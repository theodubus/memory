<!-- socle: couche=decisions zone=publique -->
# ADR-0008 — Une lecture se prouve par l'empreinte de la version lue

> statut : acceptée · date : 2026-10-10 · source : J-2026-10-10-N@29b0a201 · lu : decisions@f991d721

## Contexte

Les consignes d'`AGENTS.md` demandent de lire une entrée avant de s'appuyer
dessus, et l'index des décisions avant d'en prendre une. Aucun contrôle ne
pouvait le vérifier. Théo a proposé de l'exiger par des identifiants de
version ou des empreintes que l'agent devrait citer.

## Décision

- Chaque entrée de mémoire a une empreinte : les huit premiers caractères du
  SHA-256 de son texte. Chaque index aussi : `decisions@…` pour toutes les
  décisions, `backlog@…` pour le backlog ouvert. `socle show <ID>` et
  `socle show --index …` les impriment avec le texte ; l'état injecté au
  démarrage donne l'index des décisions et son empreinte.
- Citer `ID@empreinte` dit « j'ai lu cette version-là ». Une citation ajoutée
  doit correspondre à la version actuelle : sinon la lecture est périmée, ou
  inventée. Le hook d'écriture la refuse sans révéler la bonne empreinte, et
  `memoire.lectures` la refuse au commit et en CI.
- Obligatoire : une décision nouvelle porte `lu : decisions@…` et cite avec
  empreinte chaque entrée sur laquelle elle s'appuie ; une demande nouvelle
  cite avec empreinte chaque entrée qu'elle nomme ; un sujet de backlog
  nouveau porte `lu : backlog@…`. `socle new` affiche l'index concerné et
  pose l'empreinte dans le squelette.

## Conséquences

- Ce que ça prouve : que le texte de cette version est passé par les outils
  de l'agent, et qu'il n'a pas changé depuis. Ce que ça ne prouve pas : qu'il
  a été compris, ni qu'il a été lu en entier. Un agent décidé à tricher peut
  calculer une empreinte sans lire ; la règle vise l'oubli, pas la fraude.
- Une citation ancienne n'est pas revérifiée quand l'entrée change ensuite :
  elle témoigne de ce qui a été lu à l'époque.
- Réversible : un contrôle et une obligation à retirer.
