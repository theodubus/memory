<!-- socle: couche=backlog zone=publique -->
# B-0263 — Le socle s'arrête quand un chantier tourne en rond : un lot qui ouvre plus de sujets qu'il n'en ferme, ou des revues qui trouvent passe après passe des bloquants de même nature, deviennent une demande à l'humain

> statut : ouvert · origine : J-2026-11-16-G · priorité : haute · lu : backlog@d9da377d

Théo, le 16 novembre (J-2026-11-16-G) : « c'est la deuxième fois qu'on
tourne en rond avec un sujet infini, et sans intervention de ma part on
se retrouve a avancer dans le vide sans prise de recul. Que peut on faire
pour que le socle évite ça ». La première fois : le hook, le 13 novembre,
trente contournements en deux revues (ADR-0072) ; la seconde : le lot
B-0234, deux sujets, trois passes de revue, six bloquants corrigés puis
deux de plus, dix sujets ouverts (D-0120). Les deux fois, chaque pas
semblait juste selon les règles, et seul Théo a demandé si l'ensemble
convergeait.

Ce que le socle ne voit pas : la politique arrête un agent après trois
tentatives d'un contrôle rouge (point 7), pas après trois passes de revue
qui trouvent des bloquants ; rien ne compare ce qu'un lot ouvre à ce qu'il
ferme, ni le solde du backlog d'un domaine sur quelques jours.

La piste, à spécifier avant le code et à soumettre à Théo : des signaux
que l'état calcule, et qui font une ligne de « ce qui revient à
l'humain » et une demande qui résume, au lieu d'une passe de plus :

- un lot qui a ouvert plus de sujets qu'il n'en a fermés ;
- une revue dont la passe suivante trouve encore des bloquants (une
  troisième passe se demande, elle ne se lance pas seule) ;
- le solde du backlog d'un domaine (les sujets d'un même module ou d'un
  même mot du titre) qui grossit sur quelques jours.

La demande dit ce qui tourne, avec ses chiffres, et propose de borner la
règle qui le fait tourner, comme D-0120 l'a fait pour le hook.

## Fait quand

- [ ] la spécification des signaux et de leur seuil est soumise à Théo avant son code
- [ ] un lot qui ouvre plus de sujets qu'il n'en ferme, et une troisième passe de revue avec bloquants, font une ligne de l'état et arrêtent le lot sur une demande, et un test le montre
