<!-- socle: couche=backlog zone=publique -->
# B-0085 — Protéger les skills du socle dans la politique de ce dépôt, fichier protégé

> statut : fait · origine : J-2026-10-22-H · ref : J-2026-10-29-A · pour : humain · lu : backlog@c942935a

La politique d'un projet neuf protège les skills du socle
(`.claude/skills/socle-*/**`, ADR-0034) ; celle de ce dépôt, posée avant,
ne les nomme pas, et seul Théo la modifie. Geste de Théo, depuis la racine
du dépôt, sur la branche à jour :

```sh
python3 - <<'PY'
from pathlib import Path
p = Path(".socle/policy.toml"); t = p.read_text(encoding="utf-8")
a = '  ".claude/settings.json",\n'
assert t.count(a) == 1 and "claude/skills" not in t
p.write_text(t.replace(a, a + '  ".claude/skills/socle-*/**",\n'), encoding="utf-8")
PY
python3 .socle/socle approve --files .socle/policy.toml --text "B-0085 : les skills du socle protégés"
git add -A && git commit -m "B-0085 : les skills du socle protégés dans la politique"
```

Ensuite, une mise à jour de leurs gabarits passe dans ce dépôt par son
approbation, comme les hooks.
