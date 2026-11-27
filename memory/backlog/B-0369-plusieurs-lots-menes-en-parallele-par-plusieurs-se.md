<!-- socle: couche=backlog zone=publique -->
# B-0369 — Plusieurs lots menés en parallèle, par plusieurs sessions d'un humain à plusieurs comptes ou par plusieurs humains, sans collision d'identifiants ni conflit de mémoire

> statut : ouvert · origine : J-2026-11-26-BC · ref : D-0222 · priorité : basse · lu : backlog@0a5e410f · réserve : une nouveauté, après JA-0006 et chess (D-0222) · trié : L-0056

Théo, le 26 novembre, qui a plusieurs comptes : un lot est long, et il
demande s'il serait compliqué, ou une mauvaise idée, de mener des lots en
parallèle, pour lui comme pour des humains qui travaillent à plusieurs
sur un projet. Aujourd'hui le socle suppose un seul fil :

- `socle new` numérote sur la branche : deux sessions prennent les mêmes
  identifiants (vu le 26 novembre entre l'orchestrateur et un sous-agent,
  deux `J-2026-11-26-BB`), et une entrée poussée ne se renumérote plus ;
- la mémoire tient dans des fichiers uniques : le journal du jour, ajouté
  par sa fin, le chantier actif, réécrit, les notes de version par leur
  tête, et ici le prompt de chess : deux branches s'y heurtent à chaque
  fusion ;
- une seule pull request ouverte, et la garde de la passation, servent à
  empêcher le travail en double : rien ne dit à une autre session quel
  lot est pris, son statut `en cours` ne vivant que sur sa branche ;
- les lots de l'atelier touchent souvent les mêmes fichiers du moteur.

La conception n'est pas tranchée : sa question d'intention se pose quand
le besoin s'ouvre, après JA-0006 (C-0024@68f54ebf : les nouveautés après
les corrections).

## Satisfait quand

- [ ] deux sessions, de deux comptes ou de deux humains, mènent chacune un lot du même projet en même temps, et leurs deux pull requests se fusionnent l'une après l'autre sans conflit dans la mémoire ni identifiant pris deux fois
- [ ] une session qui forme un lot voit les lots qu'une autre a pris, et n'en prend aucun
