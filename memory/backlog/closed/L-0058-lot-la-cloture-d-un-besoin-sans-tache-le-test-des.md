<!-- socle: couche=backlog zone=publique -->
# L-0058 — Lot — la clôture d'un besoin sans tâche, le test des 8 000 octets retiré, le prompt de chess remis à sa version

> statut : fait · origine : J-2026-11-28-B · après : L-0057, T-0227, T-0228, T-0229 · lu : backlog@2b83126f · ref : ce commit

Le lot de JA-0006 que Théo fait mener le 28 novembre avant de mettre le
socle en pause quelques jours (D-0244). Ses tâches touchent les mêmes
fichiers ou tests : la clôture d'un besoin dans `memoire.formes` et
l'état (`engine/socle/checks_memory.py`, `engine/socle/memory.py`,
`engine/socle/selftest.py`, `engine/socle/FORMAT.md`, la note de
version), le test des 8 000 octets de `tests/test_skills.py` que D-0242
retire, et le prompt de mise à jour de chess avec la constante du test
qui la rejoue, que ce changement du moteur permet d'avancer. Il change un
contrôle : revue adversariale.

## Revues

### Passe 1 — 2026-11-28

Commits : 543aead8..1fa6e291

- Bloquant : le catalogue anglais sans les défauts et le témoin nouveaux de l'auto-test, la suite rouge (corrigé par 363021ba)
- Bloquant : FORMAT.md disait encore refusé le besoin fait sans tâche faite, dans le paragraphe des contrôles
- Ouvre : rien
