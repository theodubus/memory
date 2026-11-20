<!-- socle: couche=decisions zone=publique -->
# ADR-0084 — L'historique des revues d'un lot dans sa section Revues, un recul écrit avant chaque passe au-delà de la première et à la clôture, et l'arrêt sur une demande

> statut : remplacée · date : 2026-11-16 · validation : D-0124@536de605 · source : B-0263@5f67c1f8, T-0047@2bb498d6, J-2026-11-16-T@45c1634d, ADR-0083@512e719c, ADR-0042@c8fe8e02, ADR-0073@1e48220c, ADR-0081@54c62454, D-0120@f10e0e80 · lu : decisions@4cf6bba7 · remplacée-par : ADR-0100

## Contexte

Deux fois, un lot a tourné en rond sans que rien ne fasse demander à
l'agent s'il convergeait : l'historique de ses passes de revue n'était que
dans le journal, en prose (B-0263@5f67c1f8). Théo a validé la
spécification de D-0124@536de605 telle qu'écrite (J-2026-11-16-T@45c1634d) :
l'historique dans l'entrée du lot, un recul écrit avant chaque passe
au-delà de la première et à la clôture, un second regard du relecteur, et
l'arrêt sur une demande. Le lot est une entrée `L-` du backlog
(ADR-0083@512e719c) ; `socle review` produit le dossier de chaque passe
(ADR-0042@c8fe8e02, ADR-0073@1e48220c, ADR-0081@54c62454).

## Décision

La spécification de D-0124@536de605, ses huit points, telle qu'écrite. Ce
qu'elle ne tranchait pas, tranché ici :

1. *La section.* `## Revues` (`## Reviews` en anglais) est la dernière
   section de l'entrée du lot. `socle review` la pose à la fin de l'entrée
   à la première passe, et ajoute chaque passe à la fin de la section.
2. *La forme d'une passe.* Un titre `### Passe N — AAAA-MM-JJ` (`### Pass
   N — …`) et une ligne `Commits : <début>..<tête>`, que l'outil écrit ;
   puis, de l'agent, au retour du relecteur, une ligne `- Bloquant : <la
   cause, en quelques mots>` par bloquant, suivie, à partir de la deuxième
   passe, du regard du relecteur, `· même cause` ou `· cause nouvelle` ;
   une ligne `- Ouvre : <les entrées que la passe ouvre>` ; enfin le
   paragraphe de recul. Les commits s'écrivent en clair, sans `commit:` :
   une fusion par écrasement les retire de la branche par défaut, et
   l'historique doit rester lisible d'un clone neuf.
3. *Le recul.* Le paragraphe de la passe qui commence par « Recul : »
   (« Step back: »), jusqu'à la ligne vide suivante : soixante mots au
   moins, et son dernier mot, ponctuation, accents et apostrophe mis à
   part, est « continuer » (« continue ») ou « s'arrêter » (« stop ») ; ce
   qui rendra la passe suivante différente s'écrit avant. Un recul qui
   s'arrête nomme la demande qu'il pose (`D-NNNN`), qui cite le lot et
   que le lot attend aussi par son `après`.
4. *Le recul de la dernière passe se reconnaît* quand `socle review`
   produit la passe suivante, et à la clôture par `memoire.backlog`. Une
   passe est la même tant que rien n'a changé hors de la mémoire depuis le
   commit de tête qu'elle a relu : `socle review` en redonne le dossier,
   sans l'écrire de nouveau ni exiger son recul. La clôture « fait » d'un
   lot relu applique à sa dernière passe les règles qui refuseraient une
   passe de plus, le recul et les points 5 et 6, sans ce que git donne :
   une seule fonction, `memoire.refus_de_la_suite`, les dit pour les deux.
   Après sa dernière passe, l'agent corrige et clôt : un « continuer »
   après deux passes où une même cause revient, un arrêt qu'aucune réponse
   n'a levé, ou un bloquant sans le regard du relecteur, ne se clôt pas
   « fait ».
5. *Deux passes de suite où une même cause revient* : deux passes
   consécutives dont chacune a au moins un bloquant que le relecteur dit
   de même cause qu'un ancien. Le « continuer » de la seconde est refusé.
   À partir de la deuxième passe, un bloquant sans le regard du relecteur
   laisse la passe ouverte : la suivante est refusée.
6. *L'arrêt.* Seule la réponse de l'humain à la demande du lot le lève
   (D-0124, point 6) : une demande que nomme le recul qui s'arrête le lève
   si elle cite le lot dans son texte, par son identifiant `L-NNNN` ou un
   ancien numéro, et si l'humain y a répondu. Une demande retirée ne le
   lève pas, ni une demande ancienne, même répondue, qui ne cite pas le
   lot ; s'il en nomme plusieurs, une qui remplit les deux conditions
   suffit. `socle review` refuse une passe de plus, et le contrôle la
   clôture « fait », tant qu'aucune ne le lève, ou si le recul n'en nomme
   aucune. Une demande du lot qui attend sa réponse, ou que la mémoire n'a
   pas encore, se dit attendue : le lot avance ailleurs ; d'une autre, le
   refus dit qu'elle ne lève pas l'arrêt. Une demande retirée reste close
   pour l'ordre du backlog (`memoire.demande_close`) : l'arrêt n'en juge
   pas ainsi.
7. *Le lot en cours.* `socle review --batch L-NNNN` le nomme ; sinon,
   c'est le seul lot `en cours` du backlog public. Aucun : le dossier est
   celui d'avant, rien ne s'écrit, et une ligne d'erreur le dit. Plusieurs,
   ou un lot nommé qui n'est pas un lot ouvert : refusé. Un lot qui ne
   change rien hors de la mémoire n'a pas de passe.
8. *Ce que voit l'agent* quand la passe est refusée, sur la sortie
   d'erreur : la raison, la section « Revues » du lot, les entrées du
   backlog ouvertes et closes depuis le début du lot, les lots clos qui
   ont touché les mêmes fichiers (ceux dont un commit d'avant le lot qui
   change ces fichiers cite le lot, son ancien numéro ou ce qu'il attend),
   avec leurs titres, et les trois questions. Le dossier de la première
   passe reste celui d'avant, octet pour octet ; à partir de la deuxième,
   il donne au relecteur les causes des bloquants précédents et lui
   demande son regard sur chaque bloquant nouveau.

## Modèle de menace

Ce que le garde-fou arrête : un agent coopératif, emporté par le lot, qui
enchaîne les passes, ou clôt le lot, sans s'être demandé s'il converge ;
un « continuer » après deux passes où le relecteur a vu une cause revenir,
pour une passe de plus comme pour la clôture ; une passe de plus, ou la
clôture « fait », pendant que la demande d'un arrêt attend Théo ; un arrêt
levé sans sa réponse, par une demande retirée, ou par une demande
ancienne, déjà répondue, d'un autre sujet. Ce qu'il laisse passer : un
recul écrit pour la forme, que le second regard et les soixante mots
bornent sans l'empêcher ; un regard du relecteur mal consigné ; une
demande du lot répondue avant l'arrêt, que le recul nomme : la règle ne
date pas la demande, et la citer pour la forme serait un faux recul ; un
lot arrêté clos `abandonné`, que Théo peut avoir choisi ; une revue faite
hors de `socle review`, ou d'un lot qui n'est pas `en cours` (la ligne
d'erreur le dit) ; un lot qui change du code sans aucune passe, que la
revue exigée par le skill `socle-batch` couvre. Un agent hostile n'est pas
dans le modèle : il écrirait de faux reculs.

## Conséquences

Un lot garde ses passes, lisibles d'une session neuve ; quatre refus de
`socle review` (sans recul, « continuer » après deux causes revenues, un
arrêt dont la demande attend sa réponse, un arrêt qu'aucune demande du lot
répondue ne lève) et quatre de la clôture (sans recul, sans le regard du
relecteur, « continuer » après deux causes revenues, un arrêt dont la
demande attend sa réponse) ont chacun leur défaut injecté et leur témoin
sain. Le format, le guide et les skills `socle-batch` et
`socle-review` le disent, dans les deux langues ; chess le reçoit à sa
mise à jour. Défaire : une décision qui retire les refus et le contrôle ;
les sections « Revues » écrites restent lisibles comme du texte.
