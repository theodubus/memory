# Passation du lot 2, le 14 novembre

Le lot 2 (B-0151, B-0199 et B-0220) est fait mais pas relu : la fenêtre de
cinq heures de la session avait passé le seuil du skill `delegate-lot` au
retour des implémenteurs. Rien de ce code n'est sur `main` ; il est ici en
correctifs, à reprendre par une session neuve, après la remise à zéro de la
fenêtre.

## Les correctifs

- Les fichiers `0001` à `0003`, trois commits, à appliquer sur la branche
  de travail partie de `main`, dans l'ordre, avec `git am` : B-0151 (les
  notes de version du produit) ; la première part de B-0199 et B-0220 (les
  lots dans la mémoire, l'état qui montre le prochain, les lots 3 à 6 posés,
  rien de poussé après la fusion) ; l'entrée de journal du rangement.
  `verify --fast` passe sur le dernier.
- Le fichier `0004-seconde-part-socle-batch.diff`, la seconde part de
  B-0199, pas commitée : le skill du produit socle-batch en deux langues,
  `delegate-lot` réduit à ce qui est propre à ce dépôt, le skill nommé dans
  les gabarits d'AGENTS.md, ses notes de version et le point 9 du prompt de
  chess, B-0199 clos, trois tests neufs dans `tests/test_skills.py`. Il
  s'applique après les trois commits, avec `git apply --index`. Avec lui,
  deux tests existants de ce fichier échouent : ils attendent la liste des
  skills du socle posés, qui le nomme désormais.

## Ensuite, dans l'ordre

1. La revue sans contexte (skill `socle-review`) des trois commits et de la
   seconde part ensemble, une seule, jugée par la règle de D-0111 ; ses
   constats bloquants corrigés.
2. Une demande, relue à froid, pour la seconde part : la copie protégée du
   skill dans ce dépôt, sous .claude/skills/socle-batch/SKILL.md, identique
   au gabarit français, avec son empreinte d'après la revue ; et les deux
   valeurs attendues de `tests/test_skills.py`, que voici.
   - `test_l_installeur_les_pose_et_la_politique_les_protege` : la liste
     devient `["socle-batch", "socle-private-memory", "socle-request",
     "socle-resume", "socle-review"]`.
   - `test_dans_les_deux_langues_ils_passent_leurs_controles` : la ligne
     devient `"skills du socle posés dans .claude/skills : socle-batch,
     socle-private-memory, socle-request, socle-resume, socle-review"`.
3. Le push des trois commits relus, la pull request, sa CI, la fusion ; la
   seconde part attend la réponse, dans un correctif s'il le faut.
4. Après la réponse : la seconde part commitée avec les deux valeurs et la
   réponse, dans le même push ; la copie posée par l'installeur, dans le
   mode du verrou, les autres copies protégées qu'il change remises à leur
   état ; une entrée de journal, que la référence de B-0199 cite. D-0113,
   si Théo l'a validée, se fait par le même passage de l'installeur.
5. Ce dossier retiré dans le commit qui intègre le lot.
