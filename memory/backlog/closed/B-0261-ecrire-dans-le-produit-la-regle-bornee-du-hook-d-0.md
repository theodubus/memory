<!-- socle: couche=backlog zone=publique -->
# B-0261 — Écrire dans le produit la règle bornée du hook (D-0120) : la décision qui remplace la règle 2 d'ADR-0080, le guide, la consigne du relecteur, et la liste des formes connues que le hook ne juge pas

> statut : fait · origine : J-2026-11-16-G · priorité : haute · ref : D-0120, J-2026-11-16-O · lu : backlog@d9da377d

Théo a validé D-0120@f10e0e80 le 16 novembre (J-2026-11-16-G) : le hook
de l'agent juge les formes du shell qu'un agent écrit dans son travail,
pour tout effet ; pour ce que rien ne rattrape, il refuse aussi ce qu'il
ne sait pas lire ; un trou n'ouvre un sujet que si sa forme est de celles
qu'un agent écrit (vue dans une session d'agent, un skill ou une
documentation courante) ; une autre forme s'inscrit d'une ligne dans la
liste des formes connues que le hook ne juge pas, et dans la revue d'un
lot du hook elle n'est pas un bloquant, même refusée avant le lot par
accident. La règle 1 de D-0112 (le tri de la revue) reste.

À écrire, avec le texte de la règle tel que D-0120 le donne :

- une décision qui remplace ADR-0080 : ADR-0082, écrite le 16 novembre
  (J-2026-11-16-H), ADR-0080 passée `remplacée` ;
- le guide d'un projet équipé (`engine/socle/HELP.md` et sa version
  anglaise), avec la liste des formes connues non jugées : celles que
  ferment sans correction J-2026-11-16-G (les sujets abandonnés et les
  deux derniers constats du lot B-0234) ;
- la consigne du relecteur (`socle review`, et le gabarit du skill
  `socle-review`), pour qu'une forme exotique, même refusée avant le lot
  par accident, ne soit pas classée bloquante ;
- les notes de version, et le prompt de mise à jour de chess.

## Fait quand

- [x] la décision qui remplace la règle 2 d'ADR-0080, le guide (avec la liste des formes connues non jugées) et la consigne du relecteur disent la règle de D-0120, et un test le montre pour la consigne du relecteur
