<!-- socle: couche=backlog zone=publique -->
# L-0020 — Lot du push et de la fusion par l'agent : la plage d'un push dont la branche distante a disparu, la fusion en option de la politique, ce qu'on vérifie après elle, les garanties hors du hook

> statut : fait · origine : J-2026-11-20-AE · ref : J-2026-11-20-AS · après : L-0007, T-0018, T-0020, T-0064, T-0112, T-0023 · lu : backlog@3ed0ebd8

La moitié de L-0007 qui touche au push et à la fusion, coupée à son
annonce au-delà du seuil de neuf tâches (ADR-0101, J-2026-11-20-AE) : la
plage que le hook git avant push juge quand la branche distante a
disparu sans fusion (T-0018, B-0167), la fusion de sa pull request par
l'agent en option de la politique que l'humain active (T-0020, B-0200),
ce que le skill `socle-batch` fait vérifier après elle (T-0064, B-0279),
la remise des copies protégées de ce dépôt sur le gabarit changé, sous
une demande validée (T-0112, B-0218), et le relevé des couches hors du
hook qui rattrapent un push forcé ou la suppression du projet (T-0023,
B-0262).

T-0020 fait refuser la fusion par le hook de l'agent sans l'option :
relire ADR-0098 avant de l'ouvrir ; la liste `[irreversible] tools` de
la politique règle déjà ce refus.

## Revues

### Passe 1 — 2026-11-20

Commits : 792a2d86..eb5a8e6c

- Bloquant : la note 2026-11-20-p contredisait ADR-0104 après une fusion par écrasement
- Bloquant : le relevé de T-0023 tenait pour entière la garantie du hook de fin de tour du cloud
- Bloquant : le gabarit français de socle-batch avait perdu « du dépôt »
- Ouvre : B-0321, B-0322
