<!-- socle: couche=backlog zone=publique -->
# B-0190 — La clé d'un test creux dit sa classe, celle d'une copie son paragraphe

> statut : ouvert · origine : J-2026-11-12-F · priorité : haute · lu : backlog@d439d914

La seconde revue de la règle de l'adoption (B-0189, constat 3) a montré
deux clés trop pauvres : celle d'un test sans assertion ne dit pas la
classe du test, celle d'un paragraphe recopié ne dit pas quel paragraphe.
Deux constats différents peuvent alors avoir la même clé, et un neuf
prendre la place d'un ancien corrigé. Les préciser change deux valeurs
attendues de `test_les_controles_d_adoption_citent_leur_objet`
(`tests/test_adoption.py`) : Théo l'a autorisé (D-0104). À faire avant la
fusion de la pull request en cours et avant la mise à jour de chess, tant
qu'aucune liste n'est écrite sous l'ancienne forme.

## Fait quand

- [ ] la clé d'un constat de `tests.creux` porte le nom du test avec sa classe quand il en a une ; un test nouveau, qui échoue avant, montre que deux tests de même nom dans deux classes ont deux clés
- [ ] la clé d'un constat de `docs.copie` porte les huit premiers mots du paragraphe recopié ; un test nouveau, qui échoue avant, montre que deux paragraphes recopiés entre les deux mêmes fichiers ont deux clés
- [ ] la valeur attendue du test nommé plus haut est mise à jour, et elle seule
