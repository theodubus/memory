<!-- socle: couche=backlog zone=publique -->
# B-0102 — Rafraîchir le skill socle-request protégé de ce dépôt depuis son gabarit

> statut : ouvert · origine : J-2026-10-30-Q · pour : humain · lu : backlog@aa365018

Le retrait de BMAD (J-2026-10-30-Q) change le gabarit du skill des
demandes : une décision en séance approuve « une spécification », non
plus « une spec de BMAD ». La copie de ce dépôt, sous
`.claude/skills/socle-request/`, est protégée (B-0085) : seul Théo la
rafraîchit. Geste de Théo, depuis la racine du dépôt, sur une branche à
jour de `main` une fois le retrait fusionné :

```sh
cp engine/socle/templates/skills/socle-request/SKILL.md .claude/skills/socle-request/SKILL.md
python3 .socle/socle approve --files .claude/skills/socle-request/SKILL.md --text "B-0102 : le skill des demandes rafraîchi depuis son gabarit"
git add -A && git commit -m "B-0102 : le skill des demandes rafraîchi depuis son gabarit"
```

Seules trois lignes changent ; sans ce geste, l'agent de ce dépôt lit
encore BMAD dans ce skill, sans effet sur les contrôles.
