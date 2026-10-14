<!-- socle: couche=decisions zone=publique -->
# ADR-0017 — Une valeur attendue ne change que sur une spécification écrite par l'humain

> statut : acceptée · date : 2026-10-11 · source : J-2026-10-11-J@61ef7a99 · lu : decisions@d500d913

## Contexte

Le point 2 de la politique veut qu'un test supprimé ou une valeur attendue
changée soit justifié par une demande validée, ou par une spécification
changée qui nomme le test. Les spécifications sont par défaut les ADR, que
le point 3 laisse l'agent écrire seul. Au banc (s9, seconde version), un
agent sur trois a écrit une ADR qui nommait le test rouge, puis changé sa
valeur attendue : `tests.attendus` l'a accepté. L'agent s'autorisait
lui-même ; les deux autres ont posé une demande.

## Décision

Option B, choisie par Théo : une spécification ne justifie un changement
de test que si l'humain l'a écrite. Elle doit être commitée, et aucun
commit d'agent de la plage ne doit l'avoir touchée (les marqueurs de la
politique, `[agents] markers`, disent ce qu'est un commit d'agent). Une
spécification en cours d'écriture est celle de l'agent qui travaille. Une
demande validée qui nomme le test suffit toujours.

## Conséquences

Un agent devant un test rouge dont la valeur attendue est périmée pose une
demande ; l'humain répond d'un mot. Un humain qui change lui-même une
spécification et le test d'un même geste doit commiter la spécification
d'abord. Le refus dit, quand une spécification de l'agent nomme le test,
qu'elle ne suffit pas et ce qu'il faut faire. Défaut injecté et témoin sain
dans l'auto-test.

Pour défaire : retirer la condition `_ecrite_par_l_humain` dans
`moteur/socle/controles_tests.py` ; le test de `tests/test_attendus.py`
qui l'exige échouera.
