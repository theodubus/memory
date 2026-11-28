<!-- socle: couche=backlog zone=publique -->
# T-0230 — Le motif des références ne reconnaît un type qu'en début de mot, hors d'un mot en tiret

> statut : ouvert · origine : J-2026-11-28-D · besoin : B-0388 · lu : backlog@68df6bf7

`REF_RE`, dans `engine/socle/memory.py`, ne reconnaît un type de
référence qu'en début de mot : ni après une lettre, un chiffre ou un
tiret. Un test le montre sur le champ d'un refus de l'étage
git-pre-commit, et sur une référence de commit après une espace et
entre accents graves, toujours vérifiée. La note de version le dit, en
français et en anglais.

## Fait quand

- [ ] un test montre que le champ d'un refus de l'étage git-pre-commit, recopié dans une entrée, ne fait refuser aucune référence
- [ ] un test montre qu'une référence de commit qui suit une espace, ou un accent grave, reste vérifiée
