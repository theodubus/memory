<!-- socle: couche=backlog zone=publique -->
# B-0329 — L'installeur dit vrai, à la mise à jour, de l'écart de politique et de l'adoption sans contrôle en échec

> statut : ouvert · origine : J-2026-11-22-J · lu : backlog@930d5f98

La revue à froid de L-0021 (J-2026-11-22-J), deux constats pour le
backlog sur ce que B-0195 a livré.

1. La ligne qui dit l'écart de politique déjà connu (T-0076) le dit
   « montré à la mise à jour précédente ». L'installeur compare la
   politique d'aujourd'hui au gabarit de la copie remplacée, et ne sait
   pas ce qui a été montré : une ligne que l'humain a écrite après la
   mise à jour précédente, le gabarit inchangé, y tient aussi, et la
   phrase est fausse. Le fond est juste : aucune ligne ne vient du
   gabarit de cette version.
2. `_adopter` n'écrit la table `[adoption]` que s'il a des contrôles en
   échec : un projet adopté sans aucun n'en a pas, et ses mises à jour
   le traitent comme jamais adopté ; la ligne de T-0026 ne revient
   plus.

## Satisfait quand

- [ ] la ligne de l'écart de politique déjà connu dit ce que l'installeur sait, que ses lignes ne viennent pas du gabarit de cette version (T-0156)
- [ ] un projet adopté sans contrôle en échec se dit, à chaque mise à jour, sans rien à inscrire (T-0157)
