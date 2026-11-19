<!-- socle: couche=backlog zone=publique -->
# B-0263 — L'agent voit lui-même qu'un chantier tourne en rond, et en parle à l'humain avec une proposition : un lot garde l'historique de ses revues et s'arrête sur un recul écrit

> statut : fait · origine : J-2026-11-16-G · priorité : haute · après : D-0124 · ref : T-0047, T-0054, T-0055, J-2026-11-19-M · lu : backlog@d9da377d

Théo, le 16 novembre (J-2026-11-16-G) : « c'est la deuxième fois qu'on
tourne en rond avec un sujet infini, et sans intervention de ma part on
se retrouve a avancer dans le vide sans prise de recul. Que peut on faire
pour que le socle évite ça ». La première fois : le hook, le 13 novembre,
trente contournements en deux revues (ADR-0072) ; la seconde : le lot
L-0004, deux sujets, trois passes de revue, huit bloquants, dix sujets
ouverts (ADR-0082). Les deux fois, chaque pas semblait juste selon les
règles, et seul Théo a demandé si l'ensemble convergeait.

L'agent avait proposé des signaux comptés par l'état et montrés à Théo.
Sa réponse, le même jour, mot pour mot (J-2026-11-16-H) :

> Pour ta proposition pour éviter la non convergence va suffit ? Malgré le changement de session ça garde bien la trace des revues ? Et quid de si on ouvre toujours autant de sujets (et pas plus), + cette proposition laisse le fait d'exposer des métriques à l'humain, ce qui est pénible, alors qu'avec la bonne structure on peut faire en sorte que l'agent se rende compte lui meme qu'on ne converge pas  et qu'il puisse en parler à l'humain avec une proposition à ce moment là

Ce qui manque aujourd'hui : l'historique des passes de revue d'un lot
n'est que dans le journal, en prose, et non dans le lot ; aucun moment de
la méthode n'oblige l'agent à se demander si le lot converge ; et un
compte (un lot qui ouvre plus de sujets qu'il n'en ferme) manque le
chantier qui en ouvre autant qu'il en ferme, sans fin.

La piste, à spécifier avant le code et à soumettre à Théo :

1. Le lot garde son historique : chaque passe de revue s'écrit dans le
   sujet du lot (sa date, ses commits, ses bloquants et la nature de
   chacun, les sujets qu'elle ouvre, ceux que le lot ferme). Il survit à un
   changement de session, puisqu'il est dans le lot.
2. Des moments de recul, avant toute passe au-delà de la première et à la
   clôture : l'outil (le dossier de `socle review --since`, `socle
   archive`) met l'historique devant l'agent, avec la question de la
   nature, non du nombre : cette passe trouve-t-elle des bloquants de même
   nature que la précédente (chaque correction crée la suivante) ? les
   sujets que le lot ouvre sont-ils de même nature que ceux qu'il ferme ?
   les lots fermés du même domaine, lus à la formation, l'ont-ils déjà
   rouvert ?
3. L'agent y répond dans le lot, d'un paragraphe de recul : continuer, et
   pourquoi ; ou s'arrêter. Une passe de plus, ou la clôture, sans ce
   paragraphe est refusée, par un contrôle qui a son défaut injecté.
4. S'arrêter, c'est une demande à Théo : ce qui tourne, la règle qui le
   fait tourner, et une proposition qui la borne, comme D-0120 l'a fait
   pour le hook. Théo ne voit aucune métrique ; il voit la demande quand
   l'agent conclut.

## Satisfait quand

- [x] un lot dont les revues tournent en rond s'arrête sur un recul que l'agent écrit lui-même, et Théo reçoit alors une demande avec une proposition, sans lire de métrique
- [x] l'historique des revues d'un lot se lit d'une session neuve, et le recul se fonde sur lui
