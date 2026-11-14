<!-- socle: couche=backlog zone=publique -->
# B-0219 — Les suites de la revue de B-0202 et B-0175 : le délai partagé du démarrage sans test ni décision, la tentative repayée à chaque démarrage, deux fetch sans délai, le modèle de menace de B-0175 trop large

> statut : ouvert · origine : J-2026-11-14-J · priorité : basse · lu : backlog@669c8d5c

La revue de B-0202 et B-0175 (J-2026-11-14-J), quatre constats non
bloquants, de même nature : les délais et le coût de ce que le moteur
lance vers l'origine.

- `session_start` (`engine/socle/hooks.py`) donne un seul délai de 270
  secondes à l'historique puis aux outils : les outils n'ont plus que le
  reste, jusqu'à 150 secondes seulement. Aucune décision ne le dit, et
  aucun test ne montre que les outils reçoivent bien le même délai.
- Un échec de `completer_historique` ne se marque pas : un fetch qui pend
  coûte jusqu'à 120 secondes à chaque démarrage du même conteneur
  (reprise, compactage).
- `recuperer_pull_requests` (`engine/socle/utils.py`) lance désormais
  deux fetch, sans délai ni `GIT_TERMINAL_PROMPT=0` : une origine qui pend
  ou demande des identifiants coûte deux fois, au pre-commit, au Stop et
  dans `socle check`. Un seul fetch des deux motifs est impossible quand
  une même tête existe des deux côtés.
- Le modèle de menace de B-0175 dit qu'un clone ne reçoit pas un commit
  qu'aucun ref n'atteint : vrai pour un clone `--no-local` ou `file://`,
  faux pour un `git clone <chemin>` ordinaire, qui copie toute la base
  d'objets ; le défaut injecté `commit-sans-ref` ne couvre que le premier.

Écartés le 14 novembre, sur la décision de Théo (D-0111, J-2026-11-14-L),
comme cas exotiques : les deux fetch sans délai (une origine qui pend ou
demande des identifiants) et la phrase du modèle de menace de B-0175 sur
le clone local ordinaire.

## Fait quand

- [ ] le partage du délai du démarrage est décidé par une ADR et montré par un test
- [ ] un échec de l'historique ne coûte pas son délai entier à chaque démarrage du même conteneur, et un test le montre
