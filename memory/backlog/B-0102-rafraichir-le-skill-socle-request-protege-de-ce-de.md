<!-- socle: couche=backlog zone=publique -->
# B-0102 — Rafraîchir le skill socle-request et le réglage de Claude Code, protégés, de ce dépôt depuis leurs gabarits

> statut : en cours · origine : J-2026-10-30-Q · lu : backlog@aa365018

Le retrait de BMAD (J-2026-10-30-Q) change le gabarit du skill des
demandes : une décision en séance approuve « une spécification », non
plus « une spec de BMAD ». La copie de ce dépôt, sous
`.claude/skills/socle-request/`, est protégée (B-0085) : seul Théo la
rafraîchit. Geste de Théo, depuis la racine du dépôt, sur une branche à
jour de `main` une fois le retrait fusionné :

Le 31 oct., B-0105 change le même skill (une décision qui demande du
contexte s'écrit en demande, jamais dans le widget de questions de
l'agent) et le gabarit du réglage de Claude Code, protégé lui aussi, dont
le hook de l'agent doit voir ce widget pour le refuser ; la copie de ce
dépôt garde aussi un délai de démarrage de 30 secondes, quand le gabarit
en donne 300 (ADR-0035). Le geste, une fois B-0105 sur `main` :

```sh
cp engine/socle/templates/skills/socle-request/SKILL.md .claude/skills/socle-request/SKILL.md
cp engine/socle/templates/settings.json .claude/settings.json
python3 .socle/socle approve --files .claude/skills/socle-request/SKILL.md .claude/settings.json --text "B-0102 : le skill des demandes et le réglage de Claude Code rafraîchis depuis leurs gabarits"
git add -A && git commit -m "B-0102 : le skill des demandes et le réglage de Claude Code rafraîchis depuis leurs gabarits"
```

Sans ce geste, l'agent de ce dépôt lit encore BMAD dans ce skill, et son
hook ne voit pas le widget de questions ; les contrôles n'en dépendent
pas.

Le 31 oct., Théo demande de le faire « si c'est nécessaire/mieux » : c'est
mieux. Il n'a pas de terminal ; l'installeur, relancé sur ce dépôt comme
pour une mise à jour en session cloud, réécrit cinq fichiers protégés en
retard, et D-0060 les cite avec leurs empreintes, à valider dans la
conversation (J-2026-10-31-T). Le geste ci-dessus n'est plus le sien.
