<!-- socle: couche=backlog zone=publique -->
# B-0016 — La docstring de memoire.py renvoie à un document de format qui n'existe pas

> statut : fait · origine : fichier:engine/socle/memory.py · lu : backlog@ad031cf1 · ref : J-2026-10-13-Q

Vu en écrivant le module des liens : la docstring du lecteur de la mémoire
dit que le format est décrit dans un document de `docs/` qui n'existe pas ;
c'est `engine/socle/FORMAT.md` qui fait foi. Aucun contrôle ne lit les
chemins cités dans les docstrings du code.
