<!-- socle: couche=backlog zone=publique -->
# B-0180 — Le mode adoption désarme le contrôle entier : une erreur nouvelle passe en avertissement comme les anciennes

> statut : fait · origine : J-2026-11-12-A · priorité : haute · lu : backlog@849cf3e7 · ref : J-2026-11-12-D

À l'installation sur chess (`docs/fabrication/chess/installation-2026-11-12.md`, point 1) : un contrôle nommé dans
`[adoption] warn_only` voit toutes ses erreurs passer en avertissement,
les nouvelles comme celles d'avant l'installation
(`engine/socle/context.py`). Sur chess, `tests.creux` et
`memoire.references` n'arrêtent donc plus rien tant que quatre constats
anciens ne sont pas résorbés : une référence inventée demain passerait. Ni
l'installeur ni l'état ne le disent. L'adoption promet des contrôles qui
« ne peuvent que durcir » : elle doit tolérer les constats présents à
l'installation, pas ceux qui viennent après.

## Satisfait quand

- [x] sous l'adoption, un constat né après l'installation fait échouer son contrôle ; ceux d'avant restent en avertissement, et leur liste ne peut que se réduire
- [x] un projet déjà installé en adoption reçoit cette règle à sa mise à jour, sans que ses constats anciens deviennent des erreurs
- [x] l'état dit, par contrôle, combien de constats l'adoption tolère encore
