<!-- socle: couche=backlog zone=publique -->
# B-0156 — Le contexte long : une solution automatique, plutôt qu'une session neuve à ouvrir à la main

> statut : fait · ref : J-2026-11-24-Y · origine : J-2026-11-10-N · lu : backlog@877a7268

Théo, le 10 novembre (J-2026-11-10-N) : ouvrir une session neuve à chaque
sujet est une friction majeure en session cloud ; il veut une solution
automatique qui retire le contexte inutile : un compactage agressif, une
suppression de contexte, ou l'agent qui crée et initialise la session
suivante et archive la sienne. La proposition 2 de D-0093@333ad9d0, où le compte
rendu proposait une session neuve, se reformule ainsi.

Mesuré ce jour-là : avec une conversation d'environ 500 000 jetons,
chaque appel coûte autour de 1,4 % de la fenêtre de cinq heures, et un
silence de plus d'une heure fait relire toute la conversation au prix
fort. Pistes à essayer : le compactage que l'humain lance d'une commande,
après lequel le socle réinjecte l'état ; le relais de session par
l'agent, avec les outils de la session cloud ; un sous-agent au contexte
neuf par sujet. À cadrer avec Théo, sur un essai.

Le 10 novembre, Théo retient le compactage, qu'il lance lui-même, et un
sous-agent au contexte neuf par sujet (J-2026-11-10-O) ; le relais de
session reste une piste si cela ne suffit pas. Reste à l'écrire dans les
instructions, et à mesurer le coût d'un sujet ainsi mené.

Premier essai, coupé par la limite (J-2026-11-10-Q) : le compactage d'une
conversation longue coûte lui-même une part de la fenêtre, un appel
compte pour 1 % environ même après, et un sous-agent se lance au premier
plan, un à la fois, pour que la fin du tour ne juge pas un arbre en cours
d'écriture.

Premier sujet mené ainsi, B-0149 (J-2026-11-10-S) : 24 minutes, 53 appels
d'outils, les trois quarts d'une fenêtre de cinq heures et un dixième de
la semaine avec le modèle de la session ; le contexte du sous-agent a
fini plus gros que celui de la conversation principale. Le sous-agent
sort le sujet de la conversation, il n'en baisse pas le coût. Ce que sa
consigne doit dire, appris là : clore le sujet avant de le citer dans une
ADR, puis `socle archive` ; donner à `verify --fast` un délai de cinq
minutes. L'outil lance le sous-agent en arrière-plan quoi qu'on demande :
la conversation principale attend son commit. L'auto-test ne sait pas
jouer un seul cas, ce qui allonge l'essai d'un défaut injecté.

Le 15 novembre (J-2026-11-15-C), un cas de plus, relevé par la revue de
B-0173 : le skill `socle-batch` fait demander le compactage à l'humain à
la fin d'un lot et avant une attente longue ; absent (la nuit), il ne
compacte pas, et à son retour il est trop tard. Rien ne dit alors quoi
faire ; une session neuve coûterait moins que la reprise à froid.

## Satisfait quand

- [x] une session longue se poursuit sans que Théo en ouvre une neuve à la main, même quand il n'est pas là pour compacter, et ce que coûte une tâche ainsi menée est mesuré
