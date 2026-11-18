<!-- socle: couche=backlog zone=publique -->
# B-0241 — Le dossier de la revue d'une branche qui a fusionné la branche par défaut en cours de lot montre son code et ses sujets

> statut : ouvert · origine : J-2026-11-15-K · lu : backlog@90ff4f28

La revue du lot 5 (J-2026-11-15-K), constat pour le backlog 1. Une
branche de travail déjà poussée qui fusionne la branche par défaut en
cours de lot, par exemple pour renuméroter un identifiant que celle-ci a
pris aussi (skill `socle-batch`, « Intégrer »), puis relit le lot avant
son push : le dossier de `python3 .socle/socle review` part de l'ancêtre
commun de HEAD et de la branche distante, d'avant la fusion. Le code de
la branche par défaut entre dans le diff, et un sujet qu'elle seule a
clos dans la barre (`engine/socle/review.py`, `base_par_defaut`). Le
cas existait avant le lot 5 ; ADR-0081 ne couvre que la base qui avance
sans la branche. Ni l'un ni l'autre ancêtre commun ne précède l'autre :
la mesure doit retirer ce que la fusion a apporté.

## Satisfait quand

- [ ] le relecteur d'un lot dont la branche a fusionné la branche par défaut ne voit que le lot : ni le code ni les entrées que la fusion a apportés
