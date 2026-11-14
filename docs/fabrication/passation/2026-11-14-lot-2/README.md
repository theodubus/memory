# Passation du lot 2, le 14 novembre

Le lot 2 (B-0151, B-0199 et B-0220) est relu et intégré, sauf sa seconde
part, qui attend la demande D-0114 : la copie protégée d'un skill nouveau
et deux valeurs attendues d'un test. Elle est ici en correctif, avec ses
deux bloquants de la revue corrigés (J-2026-11-14-X).

## Les fichiers

- `0004-seconde-part-socle-batch.diff`, la seconde part de B-0199, pas
  commitée : le skill du produit `socle-batch` en deux langues,
  `delegate-lot` réduit à ce qui est propre à ce dépôt, le skill nommé
  dans les gabarits d'AGENTS.md, ses notes de version et le point 9 du
  prompt de chess, B-0199 clos, trois tests neufs dans
  `tests/test_skills.py`. Il s'applique sur la branche de travail avec
  `git apply --index`. Avec lui, deux tests existants de ce fichier
  échouent : ils attendent la liste des skills du socle posés, qui le
  nomme désormais.
- `socle-batch-SKILL.md`, le gabarit français du skill tel que le
  correctif le pose, pour le lire rendu : la copie protégée que D-0114
  autorise lui sera identique.

## Après la réponse à D-0114

1. Le correctif appliqué ; les deux valeurs attendues de
   `tests/test_skills.py` changées comme D-0114 le dit ; la copie posée
   par l'installeur, dans le mode du verrou (`install --target . --mode
   amont`), les autres copies protégées qu'il change remises à leur état
   du dernier commit (D-0098).
2. Une entrée de journal, que la référence de B-0199 cite à la place de
   J-2026-11-14-U, qui le disait ouvert.
3. Ce dossier retiré, et le tout commité avec la réponse, dans le même
   push ; la revue est faite, la pull request suit.

Sur un refus, la seconde part se reprend selon la raison donnée.
