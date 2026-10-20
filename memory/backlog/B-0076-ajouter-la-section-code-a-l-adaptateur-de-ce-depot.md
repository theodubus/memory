<!-- socle: couche=backlog zone=publique -->
# B-0076 — Ajouter la section [code] à l'adaptateur de ce dépôt, fichier protégé

> statut : ouvert · origine : J-2026-10-20-Q · lu : backlog@1615e20b · pour : humain

L'adaptateur de ce dépôt (`.socle/adapter.toml`, protégé) n'a pas de
section `[code]` : il a été posé avant qu'elle existe, et le moteur lui
prête celle de l'adaptateur Python maintenu. Ce repli ne sert qu'aux
projets installés avant cette section ; il partira avec le reste du code de
compatibilité (D-0033), une fois la section ajoutée ici.

Geste de Théo : ajouter à `.socle/adapter.toml`, avant `[tests]`, la
section `[code]` de l'adaptateur Python maintenu, telle quelle :

```toml
[code]
paths = ["**/*.py"]
exclude = ["tests/**", "**/test_*.py", "**/*_test.py", "**/conftest.py", "setup.py"]
private = '^\s*(?:async\s+)?def\s+_'
```

puis `python3 .socle/socle approve --text "section [code] de l'adaptateur"`,
et commiter avec.
