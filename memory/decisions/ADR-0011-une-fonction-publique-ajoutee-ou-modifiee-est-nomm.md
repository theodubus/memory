<!-- socle: couche=decisions zone=publique -->
# ADR-0011 — Une fonction publique ajoutée ou modifiée est nommée par un test

> statut : acceptée · date : 2026-10-10 · source : J-2026-10-10-S@cfa1fec9 · lu : decisions@2eb4b19f

## Contexte

Théo veut qu'un code nouveau arrive avec ses tests (B-0014@3172471c). Le
cadrage n'exige un test que pour un correctif, et compte sur la mutation
pour voir le code qu'aucun test ne vérifie ; or la mutation est hebdomadaire,
et absente pour Python. Il faut un signal à chaque fin de tour et à chaque
CI, bon marché, que le moteur puisse calculer sans connaître le langage.

## Décision

- **Le contrôle `tests.code-teste`** : une fonction publique dont une ligne
  a changé depuis la base, ou qui est nouvelle, doit être nommée par au
  moins un test. Nommée au sens littéral : son nom figure dans un fichier de
  test qui n'est pas du code, ou dans le corps d'une fonction de test d'un
  fichier qui en est (les tests unitaires de Rust vivent dans les sources).
  Une fonction imbriquée compte pour celle qui la contient.
- **Privée, elle est exemptée** : elle se teste par les fonctions publiques
  qui l'appellent. L'adaptateur dit ce qui est du code et ce qui rend une
  fonction privée (section `[code]`) ; un projet dont l'adaptateur n'a pas
  cette section hérite de celle de l'adaptateur maintenu du même langage, et
  à défaut toute fonction compte comme publique.
- **Une dispense nomme les fonctions et dit pourquoi** : trailer de commit
  `Dispense-test: f, g — <raison>`. Une dispense sans raison est refusée.
- Le contrôle tourne à la fin du tour et en CI, pas au commit : le hook avant
  commit ne voit pas le message, donc pas la dispense.
- Pour le code existant qu'on découvre sans test, la règle est écrite dans
  les instructions et non vérifiée : le test tout de suite s'il est dans le
  périmètre, sinon un sujet au backlog.

## Conséquences

Le contrôle voit qu'un test nomme une fonction, pas qu'il la vérifie : la
qualité des assertions reste l'affaire de `tests.creux` et de la mutation.
Une fonction appelée seulement par un aiguillage (une commande de la ligne de
commande, un contrôle enregistré, un hook) n'est nommée par aucun test qui
l'exerce de bout en bout : elle demande un test qui l'appelle directement,
ou une dispense qui le dit. Un nom très commun (`main`, `run`) se trouve
facilement dans un test : le contrôle le croit nommé.

Pour défaire : retirer le contrôle du registre ; la section `[code]` des
adaptateurs ne sert à rien d'autre.
