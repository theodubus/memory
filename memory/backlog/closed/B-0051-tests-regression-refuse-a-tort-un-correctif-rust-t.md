<!-- socle: couche=backlog zone=publique -->
# B-0051 — tests.regression refuse à tort un correctif Rust testé dans son module

> statut : fait · origine : J-2026-10-12-Q · lu : backlog@104e7a14 · ref : J-2026-10-13-A

Mesuré à R6, tâche 4 : l'agent corrige un défaut de `chess` et écrit son
test de régression dans le module, comme le projet le fait partout ; la
CI du socle refuse le correctif (« aucun fichier de tests/*.rs ajouté ou
modifié »), alors que le hook avant push l'avait laissé passer (B-0024).
L'adaptateur Rust n'accepte qu'un test d'intégration, parce qu'un test du
module voyage avec le code et ne se pose pas seul sur le commit d'avant.
Pistes : rejouer sur le parent le seul diff du module de tests ; dire la
règle à l'agent dès le commit d'un `fix:`.
