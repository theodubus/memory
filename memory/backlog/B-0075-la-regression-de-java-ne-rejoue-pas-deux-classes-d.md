<!-- socle: couche=backlog zone=publique -->
# B-0075 — La régression de Java ne rejoue pas deux classes de test à la fois

> statut : ouvert · origine : J-2026-10-20-N · lu : backlog@89d725be

Lu dans le code en écrivant l'adaptateur C#, non mesuré : le moteur joint
les arguments de test par une espace (`{test_args}`), et l'adaptateur Java
rejoue par `-Dtest={test_args}`. Un correctif qui ajoute deux classes de
test donne `-Dtest=ATest BTest` : Maven lit `BTest` comme une phase, et
échoue sur le parent comme sur le correctif ; `tests.regression` refuse
alors à tort (« son test de régression échoue sur le correctif lui-même »).
Le mesurer au banc des adaptateurs avec deux fichiers de régression, puis
joindre par une virgule, comme le fait l'adaptateur C# avec un `|` dans son
filtre. Vérifier au passage PHPUnit, qui reçoit plusieurs fichiers.
