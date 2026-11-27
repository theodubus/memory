<!-- socle: couche=backlog zone=publique -->
# L-0049 — Lot — la place des textes du socle à leur plafond : les consignes à 24 000 octets, les justifications des skills et d'AGENTS.md vers le guide (T-0205, T-0206)

> statut : en cours · origine : J-2026-11-26-AZ · lu : backlog@34d28079 · après : L-0048, T-0205, T-0206

Les deux tâches de B-0354 (D-0218, JA-0006) : donner aux textes du
socle arrivés à leur plafond la place des règles suivantes. T-0205
relève le budget de `memory/directives.md` à 24 000 octets sur D-0220
validée (`.socle/guardrails.toml`, les deux gabarits des garde-fous,
`tests/test_consignes.py`, la spécification des consignes). T-0206 sort
vers le guide (`engine/socle/HELP.md` et sa version anglaise) les
justifications des skills du produit et de la section du socle
d'`AGENTS.md`, déplacées mot pour mot. Toutes deux changent ce que
reçoit un projet : une note de version française et anglaise chacune,
et leur point au prompt de la prochaine mise à jour de chess. T-0206
change plus de 150 lignes de textes du produit : revue adversariale.

## Revues

### Passe 1 — 2026-11-27

Commits : 7d8d9681..95f30786

- Bloquant : l'adresse où l'humain retrouve les réveils (claude.ai/code/routines) sortie du skill socle-resume, contre T-0127
- Bloquant : la note 2026-11-26-l sans point au prompt de mise à jour de chess
- Ouvre : rien
