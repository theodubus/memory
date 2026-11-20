<!-- socle: couche=decisions zone=publique -->
# ADR-0082 — Le hook de l'agent borné aux formes qu'un agent écrit, pour tout effet : une forme exotique va à une liste, sans sujet ni bloquant

> statut : remplacée · date : 2026-11-16 · source : ADR-0072@1a8b5c2d, ADR-0080@bfb13155, B-0234@97238e0d, B-0261@a03979df, B-0262@2acccd9a, D-0112@c8501606, D-0120@f10e0e80, J-2026-11-16-E@5c27e17f, J-2026-11-16-G@18a77f23 · lu : decisions@1b9b7e67 · remplacée-par : ADR-0098

## Contexte

ADR-0080@bfb13155 écrivait la règle 2 de D-0112 : le hook de l'agent
juge, « quelle qu'en soit la forme », ce que rien ne rattrape ensuite.
Dans un langage aux formes infinies, ce critère, qui porte sur l'effet et
non sur la vraisemblance, ouvre un sujet par forme : onze sujets du hook
de priorité haute en deux jours, aucun venu d'une commande qu'un agent a
écrite dans son travail. Et la revue comptait comme une régression, donc
un bloquant, une forme que l'ancienne lecture refusait par accident : le
lot B-0234 a demandé trois passes et huit bloquants, dont sept de cette
sorte ; le huitième contredisait le critère d'un de ses sujets.
Théo a demandé si l'on retombait dans un interpréteur du shell qui ne
converge pas (J-2026-11-16-E), et validé D-0120@f10e0e80 le 16 novembre
(J-2026-11-16-G).

## Décision

Le texte de la règle, tel que Théo l'a validé :

> Le hook de l'agent arrête les erreurs d'un agent coopératif avant
> qu'elles agissent. Il juge les formes du shell qu'un agent écrit dans
> son travail, pour tout effet ; pour ce que rien ne rattrape ensuite
> (supprimer le projet ou un dossier qui le contient, une action externe
> irréversible, une fuite de la mémoire privée, la part de la mémoire qui
> ne se publie pas), il refuse aussi ce qu'il ne sait pas lire. Un trou
> ouvre un sujet si sa forme est de celles qu'un agent écrit dans son
> travail : vue dans une session d'agent, un skill ou une documentation
> courante. Une autre forme s'inscrit d'une ligne dans la liste des formes
> connues que le hook ne juge pas, sans sujet ; dans la revue d'un lot du
> hook, elle n'est pas un bloquant, même refusée avant le lot par
> accident.

Elle remplace ADR-0080 ; la règle 1 de D-0112 (le tri des constats de la
revue) reste. Le relecteur propose le classement d'une forme, l'agent le
vérifie. Le hook refuse toujours ce qu'il sait ne pas savoir lire
(ADR-0072@1a8b5c2d, point 6).

## Conséquences

- La liste des formes connues non jugées est, jusqu'à ce que B-0261
  l'écrive dans le guide d'un projet équipé, celle de J-2026-11-16-G ;
  B-0261 écrit aussi la règle dans le guide et dans la consigne du
  relecteur, que chess reçoit à sa mise à jour.
- Les sujets du hook ouverts pour une forme exotique sont abandonnés à
  la liste, et ceux qui gardent une part qu'un agent écrit sont réduits à
  elle (J-2026-11-16-G).
- La garantie de ce que rien ne rattrape, que le hook ne donne plus pour
  une forme exotique, s'étudie dans des couches qui ne lisent pas le
  shell (B-0262).
- Pour défaire : c'est une décision de Théo ; une demande nouvelle, qui
  la remplace.
