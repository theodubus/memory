<!-- socle: couche=backlog zone=publique -->
# B-0388 — memoire.references lit une référence de commit au milieu d'un mot : le champ étage et contrôle du journal des hooks, recopié, est refusé comme un SHA

> statut : ouvert · origine : J-2026-11-28-D · lu : backlog@68df6bf7

Le constat 5 du relevé d'après de chess
(`docs/fabrication/chess/cout-et-frictions-2026-11-28.md`). Le journal
des hooks écrit son quatrième champ « étage:contrôle » ; recopié dans une
entrée de la mémoire pour l'étage git-pre-commit, `memoire.references` y
lit une référence de commit, dont la cible est le nom du contrôle, et le
refuse : « n'est pas un SHA ». Le relevé demande pourtant de classer les
refus par ce champ.

Vérifié ici le 28 novembre : `REF_RE`, dans `engine/socle/memory.py`, n'a
aucune borne à gauche ; tout mot qui finit par le nom d'un type de
référence, suivi d'un deux-points, en ouvre une, entre accents graves
aussi. Seul l'étage git-pre-commit le fait parmi ceux du journal.

## Satisfait quand

- [ ] le champ d'un refus du journal des hooks, recopié dans une entrée de la mémoire, n'est pas lu comme une référence
- [ ] une référence en début de mot, après une espace, une parenthèse ou un accent grave, reste lue et vérifiée
