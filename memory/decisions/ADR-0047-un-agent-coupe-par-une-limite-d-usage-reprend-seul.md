<!-- socle: couche=decisions zone=publique -->
# ADR-0047 — Un agent coupé par une limite d'usage reprend seul à sa levée : un seul réveil, armé quand la limite approche, porteur du travail en cours

> statut : abandonnée · date : 2026-11-08 · source : B-0132@cc8d5405, J-2026-11-08-H@3d8256b3 · lu : decisions@cece1142

## Contexte

Une limite d'usage, de cinq heures ou de la semaine, coupe l'agent au
milieu de son travail, et il ne reprend qu'au message suivant de
l'humain. Deux check-ins programmés, tombés pendant la limite, n'ont été
lus qu'alors (J-2026-11-08-G@a0ca8d26). Un rappel récurrent ne convient
pas (J-2026-11-08-H@3d8256b3) : il réveille aussi l'agent qu'aucune limite
n'a coupé, ignore les sous-agents coupés, et réveillerait une session
abandonnée ou un projet inactif. Le but est l'autonomie de l'agent, la
nuit comme le jour.

En session cloud de Claude Code, l'agent voit ses limites : chaque appel
enregistre dans les événements de la session (`rate_limit_event`, lus par
l'outil `list_events`) l'utilisation de la fenêtre de cinq heures et de
celle de sept jours, de 0 à 1, et l'heure exacte de leur remise à zéro.
Il peut programmer un message à sa propre session (`send_later`), le
déplacer et le retirer.

## Décision

**1. Un seul réveil, armé quand une coupure est plausible.** À chaque
point d'étape (le début d'un lot, avant de lancer un sous-agent, la fin
d'un tour), l'agent lit son utilisation. Si l'une des deux fenêtres dépasse
80 % et que du travail reste, il arme un réveil de secours : un message à
sa session, programmé cinq minutes après la remise à zéro de cette
fenêtre, à toute heure. Il n'en tient qu'un par session : à l'étape
suivante, il déplace le même. Sous 80 %, ou quand rien ne reste, il n'y en
a pas ; s'il en reste un, l'agent le retire.

**2. Le réveil porte le travail en cours.** Son message dit le lot,
l'étape, et chaque sous-agent lancé avec ce qu'il devait rendre. L'agent
le récrit à chaque point d'étape.

**3. Au réveil, l'agent vérifie d'abord que la session vit encore.** Il ne
fait rien, et ne réarme pas, si une autre session a poussé sur sa branche
depuis son dernier commit, si sa pull request est fusionnée ou fermée sans
travail restant, ou si l'humain lui a dit d'arrêter. Sinon il reprend
l'étape notée, et relance chaque sous-agent dont le résultat n'est pas
arrivé, avec le même message. Il ne réarme que si la limite revient.

**4. La procédure vit dans un skill du socle, `socle-reprise`.** Elle
dépend de l'agent et de ses outils de session cloud : le moteur n'en sait
rien. L'installeur pose le skill dans tout projet, et la politique le
protège, comme les autres skills du socle. Un agent qui n'a pas ces outils
ne fait rien, et son récap ne le dit qu'une fois.

## Conséquences

Un agent coupé reprend seul, au plus tard cinq minutes après la levée de
la limite, jour et nuit. Un agent qu'aucune limite ne menace n'est jamais
réveillé, et une session morte ne l'est jamais non plus : un réveil
n'existe que pendant qu'une session active travaille près d'une limite,
et il ne se réarme pas seul. Une coupure soudaine, sous 80 %, n'est pas
couverte : l'humain relance comme aujourd'hui. Que le réveil d'une
session coupée la reprenne bien est supposé : la première coupure réelle
le mesurera. Se défait en retirant le skill.
