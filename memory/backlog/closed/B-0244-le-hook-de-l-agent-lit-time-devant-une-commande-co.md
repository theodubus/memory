<!-- socle: couche=backlog zone=publique -->
# B-0244 — Le hook de l'agent lit time devant une commande composée comme une commande simple : un push forcé y passe (time { … }, time if …, time function f { … })

> statut : abandonné · origine : J-2026-11-15-M · priorité : haute · ref : J-2026-11-16-G · lu : backlog@cc3fa160

Le découpage du hook de l'agent retire `time` comme un préfixe
(`commands.PREFIXES`, dans `_sans_prefixes`), mais après les mots
réservés : écrit devant une commande composée, `time` en fait une commande
simple dont le programme est le mot réservé qui suit, et la première
commande de la condition ou du groupe ne se juge pas. `time { git push
--force origin main; }`, `time if git push --force origin main; then :;
fi` et `time function f { rm -rf ..; }` passent le hook ; bash admet les
trois (`bash -n -c`), et `time -p` de même. Vu en menant B-0232
(J-2026-11-15-M) ; ADR-0080, sa première conséquence, ouvre un sujet pour
un trou par lequel passe un push forcé ou la suppression du projet, quelle
qu'en soit la forme : de priorité haute, comme B-0232.

La piste : lire `time` et `time -p` en tête d'une commande comme un mot
réservé, avant les autres (`reserves`), pour que la commande composée qui
suit s'ouvre comme sans lui.

Abandonné le 16 novembre selon D-0120 (J-2026-11-16-G) : `time` devant une commande composée, qu'aucun agent n'écrit dans son travail, va à la liste des formes connues que le hook ne juge pas (B-0261).

## Fait quand

- [ ] `time { git push --force origin main; }`, `time if git push --force origin main; then :; fi` et `time function f { rm -rf ..; }` sont refusés par le hook, `time ls` passe, et un test le montre
