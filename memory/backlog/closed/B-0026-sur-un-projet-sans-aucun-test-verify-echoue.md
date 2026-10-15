<!-- socle: couche=backlog zone=publique -->
# B-0026 — Sur un projet sans aucun test, verify échoue

> statut : fait · origine : J-2026-10-11-G · lu : backlog@c462bb86 · ref : J-2026-10-14-H

Vu au banc (s6, premier passage : l'initialisation depuis un cadrage seul)
et reproduit sur un projet installé vide : `socle verify` échoue sur
`verify.tests`, parce que `unittest` rend le code 5 quand il ne trouve
aucun test. Un projet qui commence n'a pas encore de test : l'adaptateur
devrait traiter « aucun test » comme un avertissement, pas comme un échec.
Le juge de s6 ne regardait que les contrôles, pas `verify`.
