<!-- socle: couche=backlog zone=publique -->
# B-0088 — Une session qui installe le socle est dite sans hooks par l'état

> statut : fait · origine : J-2026-10-29-F · ref : J-2026-10-29-F · lu : backlog@b8f4fad9

La détection de B-0079 exige un SessionStart pour la session. Une session
qui installe le socle n'en a pas : le hook n'existait pas à son démarrage,
mais ses hooks tirent dès l'appel d'outil suivant (F-0003). L'état la
disait donc sans hooks, et l'agent, suivant ses instructions, ne devait
plus rien pousser. Relevé en préparant l'installation du pilote dans une
session cloud.
