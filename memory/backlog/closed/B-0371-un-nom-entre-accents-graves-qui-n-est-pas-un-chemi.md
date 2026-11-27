<!-- socle: couche=backlog zone=publique -->
# B-0371 — Un nom entre accents graves qui n'est pas un chemin du dépôt fait refuser la fin du tour sans son chemin complet, et le message qui corrige doit redire tout le récap

> statut : fait · origine : J-2026-11-27-U · ref : D-0235, T-0210, J-2026-11-27-X, J-2026-11-27-Z · lu : backlog@4d53be09

Le premier poste des refus chez chess : 20 sur 56, du 12 au 26
novembre (`docs/fabrication/chess/cout-et-frictions-2026-11-26.md`, §3.1), chacun un tour et un message de plus ; Théo
s'en est plaint (« Pourquoi tu répètes 2 fois le récap de fin ? »).
Confirmé dans le code (`docs/fabrication/chess/relecture-cout-et-frictions-2026-11-27.md`) : `links.problemes` répond « aucun
chemin de ce nom dans le dépôt » sans chercher le fichier suivi que
désigne un nom nu ; la fin de tour (`engine/socle/hooks.py`) juge le
récap sur le seul dernier message, que le message qui corrige doit donc
redonner entier.

Retenu par Théo le 27 novembre (D-0235, point 1). Le hook de l'agent
s'ouvre sur cette preuve (ADR-0098).

## Modèle de menace

Le refus arrête un lien mort dans le dernier message : un nom entre
accents graves qui n'est pas un chemin du dépôt, dont l'interface de
l'humain fait un lien. Il laisse passer désormais un message sans récap
qui suit, dans le même tour, un message refusé pour ses seuls liens qui
portait le récap : l'humain l'a lu une fois. Il n'arrête toujours pas un
chemin juste vers le mauvais fichier.

## Satisfait quand

- [x] le refus d'un nom nu qui désigne un seul fichier suivi donne son chemin complet ; sinon, il dit de l'écrire sans accents graves
- [x] un message qui ne fait que corriger les liens d'un récap refusé pour eux seuls passe sans redire le récap
- [x] la section installée dit la règle des liens en une phrase positive
