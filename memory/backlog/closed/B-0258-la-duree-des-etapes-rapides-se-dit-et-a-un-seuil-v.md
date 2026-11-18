<!-- socle: couche=backlog zone=publique -->
# B-0258 — La durée des étapes rapides se dit, et a un seuil : verify --fast n'imprime aucune durée, et rien ne signale qu'elle a passé de 143 s à près de douze minutes

> statut : fait · origine : J-2026-11-16-E · ref : J-2026-11-18-B · priorité : haute · lu : backlog@6e1a17c2

Un sujet du produit, d'une analyse en lecture seule du 15 novembre sur
d1d296e, que Théo a fait inscrire (J-2026-11-16-E) ; il n'en fixe ni la
priorité ni le lot. Son constat, commun avec B-0257, y est écrit avec la
nature de chaque point (mesuré, écrit, déduit, vérifié) : `verify --fast
--redo` mesuré une fois à 11 min 49 s sur un seul cœur, quand
`docs/fabrication/recul.md` écrit 143 s le 13 octobre, sur une autre
machine ; vérifié, `verify --fast` n'imprime aucune durée.

Quoi : `verify --fast` dit la durée de chaque étape et leur total. Au-delà
d'un seuil des garde-fous, un avertissement, pas un échec, nomme l'étape
la plus longue.

Pourquoi : entre les deux relevés, la durée est passée de 143 s à près de
douze minutes sans que rien ne le signale. Les tailles ont un budget, les
durées n'en ont pas.

Conception à trancher, la spécification avant le code : où s'écrit le
seuil ; sa valeur par défaut (les cinq minutes viennent du cache d'un
agent, que le moteur ne connaît pas) ; ce que le cliquet en dit.

Théo le passe en priorité haute le 16 novembre, au lot L-0012, juste après L-0011 (J-2026-11-16-I) : une vérification plus courte rend chaque lot suivant moins cher.

La spécification se soumet à Théo dans la demande D-0130, récrite après
la passe 1 de la revue du lot (J-2026-11-17-J).

## Modèle de menace

Le seuil `[verify] fast_max_seconds` est un garde-fou qui avertit, sans
jamais échouer.

Il arrête : une dérive silencieuse du total des étapes rapides au-delà du
seuil, vue au premier `verify --fast` qui les lance toutes sur la machine
où il tourne ; elle reste dite, tant que le dernier passage complet
dépasse le seuil, à chaque vérification servie par la marque des étapes
déjà passées et dans `socle state`, que le démarrage de chaque session
injecte. Le relèvement du seuil par l'agent : le cliquet des garde-fous
connaît la clé, la relever exige une demande validée, la baisser est
libre ; un défaut injecté le prouve.

Il laisse passer : une dérive sous le seuil ; la durée d'une machine plus
rapide, qui masque celle d'une plus lente, et la CI, sans seuil ; une
étape retirée des étapes rapides, ce qui change l'adaptateur, protégé, et
passe donc par l'humain ; un test mis de côté sous `SOCLE_RAPIDE`, que la
CI joue toujours ; une étape bloquée, qui finit en erreur de délai, pas
en durée ; la fin de tour et le push, qui ne relancent pas des étapes
déjà passées sur le même contenu, et n'ajoutent donc rien.

## Satisfait quand

- [x] le « Fait quand » de T-0045 est tenu
