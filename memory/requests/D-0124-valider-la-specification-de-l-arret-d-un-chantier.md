<!-- socle: couche=demandes zone=publique -->
# D-0124 — Valider la spécification de l'arrêt d'un chantier qui tourne en rond : l'historique des revues dans le lot, un recul écrit avant chaque passe et à la clôture (B-0263)

> date : 2026-11-16

## Décision demandée

Valider la spécification ci-dessous, écrite ici en entier : comment
l'agent voit lui-même qu'un lot tourne en rond, et vous en parle avec une
proposition, sans vous montrer de chiffres. Répondez dans la conversation
par l'un des mots de la fin ; une condition que vous y ajoutez sera
recopiée mot pour mot, et appliquée.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA comme Claude Code : il
garde la mémoire du projet (le backlog, le travail à faire, en fait
partie), vérifie ce que l'agent produit, et vous pose en « demandes »,
comme celle-ci, les décisions qui vous reviennent. Chess, votre jeu
d'échecs, est le projet pilote qui l'utilise.

**Le chantier.** L'agent mène le travail par lots : quelques entrées du
backlog menées ensemble, puis relues par un relecteur sans contexte, un
autre agent qui n'a pas la conversation et cherche à les prendre en
défaut ; chaque relecture est une passe de revue, et ses bloquants, les
constats à corriger avant de livrer. Deux fois, un lot a tourné en rond.
Le 13 novembre, sur le hook de l'agent (le programme qui lit chaque
commande de l'agent avant qu'elle tourne et refuse celles qui feraient un
dégât), deux revues ont trouvé trente commandes qui passaient à tort. Le
15, un lot de deux entrées a demandé trois passes, corrigé huit bloquants
et ouvert dix entrées nouvelles au backlog. Chaque pas semblait juste, et
seul vous avez demandé si l'ensemble convergeait.

**La question.** Le 16 novembre, l'agent proposait de compter des signaux
et de vous les montrer. Vous avez répondu : garde-t-on la trace des revues
d'une session à l'autre ? que faire si l'on ouvre autant d'entrées qu'on
en ferme ? montrer des chiffres à l'humain est pénible ; avec la bonne
structure, l'agent doit voir lui-même qu'on ne converge pas, et vous en
parler avec une proposition. Voici cette structure, avant le code.

**Les mots.** Le moteur : le programme du socle. Un contrôle : une règle
qu'il vérifie quand l'agent finit de répondre, à chaque commit et dans la
CI, les vérifications que GitHub lance à chaque envoi. Un défaut injecté :
une faute que l'auto-test du socle s'inflige pour prouver que le contrôle
l'attrape, avec un témoin sain, le même cas sans la faute, qui doit
passer. Un skill : une procédure écrite pour l'agent. Le dossier de
revue : le texte que produit la commande `socle review`, seul message que
reçoit le relecteur. Une entrée close : faite ou abandonnée. La décision
que j'écris ensuite est une ADR, la trace d'une décision de conception,
distincte de cette demande.

**La spécification.**

1. *L'historique, dans le lot.* L'entrée du lot reçoit une section
   « Revues ». Chaque fois que `socle review` produit le dossier d'un lot
   en cours, il y ajoute la passe, sa date et ses commits ; l'agent y
   écrit, au retour du relecteur, la cause de chaque bloquant, en quelques
   mots (« la correction change la lecture des commandes »), et les
   entrées que la passe ouvre. L'historique est versionné avec le lot :
   une session neuve le lit tel quel.
2. *Le recul, avant chaque passe au-delà de la première.* `socle review`
   refuse de produire le dossier tant que la passe précédente n'a pas son
   recul, et montre à l'agent l'historique et trois questions de nature,
   non de nombre : les bloquants de cette passe ont-ils la même cause que
   ceux de la précédente ? les entrées que le lot ouvre sont-elles de même
   nature que celles qu'il ferme ? les lots clos qui ont touché les mêmes
   fichiers ont-ils déjà ouvert ce genre d'entrées ? Il y joint ce que
   git donne : les entrées ouvertes et closes depuis le début du lot, et
   ces lots clos, avec leurs titres. Un lot qui ouvre autant qu'il ferme,
   mais toujours la même sorte d'entrées, se voit ainsi.
3. *Le recul, à la clôture.* Un lot relu ne se clôt `fait` que si sa
   dernière passe a aussi son recul ; un contrôle le vérifie. Un lot qui ne
   change ni code, ni spécification, ni test n'a pas de revue, ni de
   recul.
4. *Le paragraphe.* Il commence par « Recul : », répond aux trois
   questions en soixante mots au moins, et finit par « continuer », avec
   ce qui rendra la passe suivante différente, ou par « s'arrêter ».
5. *Un second regard.* À partir de la deuxième passe, le dossier donne au
   relecteur les causes des bloquants précédents ; il dit, pour chaque
   bloquant nouveau, s'il a la même cause qu'un ancien. L'agent le
   consigne. Après deux passes de suite où le relecteur voit une même
   cause revenir, `socle review` refuse « continuer » : le lot s'arrête.
6. *S'arrêter.* C'est une demande pour vous : ce qui tourne, en clair, la
   règle qui le fait tourner, et une proposition qui la borne, comme celle
   du 16 novembre pour le hook (il ne juge plus que les commandes qu'un
   agent écrit vraiment ; une forme rare s'inscrit dans une liste, sans
   ouvrir d'entrée ni bloquer un lot). Le lot attend votre réponse, et
   `socle review` refuse une passe de plus jusque-là ; l'agent avance
   ailleurs. Vous ne voyez aucun chiffre : vous voyez la demande.
7. *Les textes.* Le format du backlog, les skills qui mènent un lot et sa
   revue, et le guide d'un projet qui utilise le socle, en français et en
   anglais ; chess les reçoit à sa mise à jour, sans geste de votre part.
8. *Les preuves.* Des tests, et trois défauts injectés : une deuxième
   passe sans recul, un « continuer » après deux causes revenues, refusés
   par `socle review` ; un lot clos sans recul, refusé par le contrôle. Un
   test lit l'historique d'un lot depuis un clone neuf.

**L'ordre.** Après la structure du backlog, soumise à part et en attente :
le lot y devient une entrée de forme lot. Cette spécification ne dépend
que de ce qu'un lot soit une entrée du backlog, vrai dans les deux cas.
Une session.

## Éléments cités

- B-0263@0f02de1d — l'entrée du backlog qui porte ce chantier, avec votre message du 16 novembre mot pour mot.
- B-0234@97238e0d — le lot du 15 novembre qui a tourné en rond : deux entrées, trois passes, huit bloquants.
- D-0120@f10e0e80 — votre décision du 16 novembre qui borne le hook, l'exemple d'une proposition qui arrête une boucle.
- D-0123@61a56e15 — la demande qui soumet la structure du backlog, en attente de votre réponse.

## Où regarder

- [B-0263](https://github.com/theodubus/memory/blob/ea73156977df2099381d4ea87a3552d9efc100c5/memory/backlog/B-0263-le-socle-s-arrete-quand-un-chantier-tourne-en-rond.md) :
  votre question et la piste d'origine, celle de l'agent ; vérifier que la
  spécification répond à vos trois points : la trace d'une session à
  l'autre, le lot qui ouvre autant qu'il ferme, aucune métrique montrée.

## Options

- **La spécification telle quelle** : l'outil écrit la passe, refuse la
  suivante sans recul, et arrête le lot quand le relecteur voit une cause
  revenir. Effort : une session. Risque : un recul écrit pour la forme ;
  le second regard le borne. Réversible : une règle du moteur, qui se
  retire par une décision.
- **Le recul dans les skills seulement**, sans refus ni contrôle. Moins de
  code, mais c'est l'état des deux fois où le lot a tourné : rien ne
  forçait le recul.

## Conséquences

Si vous validez : j'écris la décision, puis le code, relu par un relecteur
sans contexte avant la livraison. Si vous refusez : je corrige ce que
votre réponse dit, et vous soumets une spécification nouvelle. Sans
réponse : rien ne s'écrit de ce chantier ; les autres entrées du lot en
cours avancent.

## Recommandation

Valider. Vérifié : aujourd'hui, l'historique des passes n'est que dans le
journal, en prose, et rien n'oblige l'agent à se demander si le lot
converge ; `socle review` produit déjà le dossier de chaque passe, le
point naturel du refus. Supposé : que trois questions de nature et le
second regard suffisent à faire voir une boucle ; le premier lot qui
s'arrête le dira.

## Réponses possibles

- `valider` — la spécification telle quelle ; l'agent écrit la décision, puis le code.
- `skills-seuls` — le recul écrit dans les skills, sans refus ni contrôle.
- `refuser` — l'agent corrige ce que la réponse dit, et soumet une spécification nouvelle.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
