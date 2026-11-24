<!-- socle: couche=decisions zone=publique -->
# ADR-0108 — La revue trie ses constats par le but : les bloquants corrigés dans le lot, un autre au backlog seulement s'il est important et vu en usage réel ou d'effet irréversible, sinon écarté, et il revient s'il est vu

> statut : acceptée · date : 2026-11-24 · source : D-0165@d8aaca8b, D-0167@4a24a192, ADR-0073@1e48220c, D-0112@c8501606, B-0342@088e016b, J-2026-11-24-A@69c38dd7, T-0173@12e8e5b3, D-0168@f095a79d · lu : decisions@338a5d9b

## Contexte

ADR-0073@1e48220c, puis la règle 1 de D-0112@c8501606, envoient au
backlog tout constat de revue qui ne bloque pas, s'il peut se produire
dans l'usage normal du projet ou si rien ne rattrape son effet ; seul
s'écarte l'exotique rattrapé. Un relecteur qui cherche à prendre le lot
en défaut en trouve toujours : du 14 au 23 novembre, les revues de ce
dépôt ont ouvert 111 entrées, et le jalon ne converge plus
(J-2026-11-24-A, B-0342@088e016b). Le 24 novembre, Théo décide que le
temps ne va pas à un cas limite rare qui n'est qu'une légère gêne que
l'agent gère lui-même (D-0165@d8aaca8b), puis valide les critères de tri
(D-0167@4a24a192, `docs/fabrication/but-et-tri.md`), dont seule la part
générale entre dans le produit : les bloquants corrigés dans le lot ; un
autre constat seulement s'il est important et vu en usage réel ; écarté,
il revient s'il est vu.

## Décision

**Les bloquants** ne changent pas : un critère coché ou une décision
citée contredits, une régression, une perte de données, un contournement
dans le modèle de menace ; ils se corrigent dans le lot.

**Un autre constat va au backlog seulement** s'il est important et a été
vu en usage réel (une session, une CI, un message de l'humain le
montre), ou si son effet serait irréversible (une perte de données, un
push sur la branche par défaut, une suppression).

**Tout autre s'écarte**, quel qu'il soit, dont un cas que le relecteur
imagine sans l'avoir vu, une légère gêne que l'agent règle lui-même (ce
que rattrape un contrôle, la CI ou une erreur qu'il voit aussitôt), un
contournement hors du modèle de menace, et un constat infondé. En cas de doute, il s'écarte ; il revient s'il est vu en
usage réel. Le récap dit pourquoi chacun est écarté.

Ce tri remplace la classe « Pour le backlog » d'ADR-0073 et la règle 1
de D-0112 ; le reste d'ADR-0073 (les sujets du lot dans le dossier, le
modèle de menace, la seconde revue) tient. Il s'écrit d'une seule
manière dans la consigne du relecteur (`engine/socle/review.py`), le
gabarit du skill `socle-review`, celui d'`AGENTS.md` et le guide, en
français et en anglais. Dans ce dépôt, `docs/fabrication/but-et-tri.md`
le précise par ses trois tests et ses exclusions (le skill
`delegate-lot`).

## Conséquences

Une revue rend moins d'entrées au backlog ; ce qu'elle écarte n'est pas
perdu, il revient s'il se voit. Un projet installé le reçoit à sa mise à
jour, avec une note de version ; la copie protégée du skill
`socle-review` de ce dépôt suit sur une demande. Les entrées ouvertes de
ce dépôt nées d'une revue sont retriées par T-0173 (D-0168). Se défait en
revenant au texte d'avant de la consigne, du skill, du gabarit et du
guide.
