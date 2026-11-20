<!-- socle: couche=decisions zone=publique -->
# ADR-0098 — Le hook de l'agent est terminé : on n'y touche que sur une preuve, un refus à tort qui a bloqué un vrai travail ou un contournement écrit par un agent dans une session, que rien d'autre ne rattrape

> statut : acceptée · date : 2026-11-20 · validation : D-0143 · source : ADR-0082@beb85978, ADR-0073@1e48220c, ADR-0084@df557d83, D-0128@fd7c9ad7, D-0143@04eddcb5, J-2026-11-20-B@67a52899 · lu : decisions@a8bbd13d

## Contexte

Le hook de l'agent lit chaque commande du shell avant qu'elle agisse,
et refuse celles qui écriraient un fichier protégé, supprimeraient le
projet ou pousseraient sur la branche par défaut. Le shell écrit une
même action d'une infinité de façons, et la revue de chaque lot du hook
avait pour consigne d'en trouver une que le hook ne voit pas : elle en
trouvait toujours, chaque trouvaille devenait une entrée du backlog, et
le lot suivant la corrigeait. Trois remèdes n'ont pas coupé cette
boucle : le tri des constats (ADR-0073) l'envoyait au backlog ; la borne
des « formes qu'un agent écrit » (ADR-0082) était un jugement, que tout
constat d'un relecteur pouvait satisfaire ; le recul (ADR-0084) demande
s'il faut une passe de plus dans un lot, pas un lot de plus sur un
sujet, et ses quatorze reculs ont tous conclu « continuer ».
L-0005@657fe9e5 et L-0019@4a8f5475 ont encore fait dix tâches du hook, et L-0019 en a ouvert cinq.
Aucune de ces trouvailles n'avait été vue chez un agent : dans les
sessions réelles du banc, le hook n'a arrêté que des fautes simples.
Théo l'a relevé une troisième fois et demandé une garantie
(J-2026-11-20-B) ; il a validé cette décision (D-0143).

## Décision

Le hook de l'agent est terminé. Il ne change que sur une preuve, que
l'entrée du backlog qui le change cite par un lien (une session, une
entrée du journal) :

- un refus à tort qui a bloqué un vrai travail ;
- ou un contournement réellement écrit par un agent dans une session,
  non imaginé par un relecteur, dont l'effet ne serait rattrapé par rien
  d'autre : un push forcé ou sur la branche par défaut, la suppression
  du projet avec son `.git`, le réglage local de Claude Code que git ne
  suit pas.

Sans cette preuve, une entrée du hook ne s'ouvre pas. La revue d'un lot
qui touche le hook ne cherche plus de contournements : elle vérifie
qu'il ne casse rien de ce qui marchait ; un contournement qu'elle trouve
s'écarte d'office. Le code déjà écrit reste tel quel, avec ses tests :
il sert les trois cas, il est testé, et le retirer serait un chantier de
plus sur le hook. Les entrées ouvertes du hook sans preuve se ferment en
renvoyant à cette décision : B-0230@a9ced058, T-0002@612cea61,
B-0302@be1ee999, B-0305@28685cbb, B-0306@ce992c0d, T-0108@6bec4e0b,
B-0307@3da2a889, T-0109@688c7598 et B-0308@ffa6c096. La règle s'écrit là où chaque session
la lit : `AGENTS.md`, le chantier actif et le skill `delegate-lot`.
Elle remplace ADR-0082 ; D-0128 reste, qui sort du produit la liste des
formes exotiques.

## Conséquences

Ce que le hook ne voit pas aujourd'hui, il ne le verra pas, sauf preuve
nouvelle ; un fichier protégé suivi par git écrit sous une telle forme
reste attrapé au commit et en CI. Les refus à tort du code actuel (un
script qui cite un fichier protégé dans un texte) restent, tant qu'ils
ne bloquent pas un vrai travail. Pour retomber dans la boucle, une
session doit enfreindre une règle explicite, pas l'interpréter. Se
défaire par une décision nouvelle de Théo.
