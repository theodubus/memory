<!-- socle: couche=backlog zone=publique -->
# B-0025 — tests.code-teste prend pour du code une fonction écrite dans une chaîne

> statut : fait · origine : J-2026-10-11-F · lu : backlog@a44391d3 · ref : J-2026-10-14-H

Le banc garde le code de ses projets d'essai dans des chaînes Python ; une
ligne `def echelle(x):` en début de ligne, dans une chaîne, est lue comme
une fonction publique ajoutée, qu'aucun test ne nomme. Dispensée pour
l'instant par un trailer ; le lecteur de fonctions devrait sauter les
chaînes multilignes.
