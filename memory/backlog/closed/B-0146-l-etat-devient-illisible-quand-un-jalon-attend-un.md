<!-- socle: couche=backlog zone=publique -->
# B-0146 — L'état devient illisible quand un jalon attend un sujet qui attend une demande sans réponse

> statut : fait · origine : J-2026-11-10-H · lu : backlog@13100dad · ref : J-2026-11-10-I

Sur le pilote, `socle state` affiche « mémoire : illisible (KeyError:
'D-0036') » et ne montre plus ni le backlog ni les sujets prêts : un
jalon attend un sujet, qui attend une demande sans réponse
(J-2026-11-10-H). `memoire.ordre` cherche le prochain jalon parmi les
jalons ouverts qu'aucun jalon attendu ne précède, et lit comme un sujet
chaque attendu, demandes comprises. `socle check` passe : le contrôle de
l'ordre ne lit les attendus qu'après les avoir triés.

## Fait quand

- [x] l'état calcule l'ordre d'un backlog où un jalon attend un sujet qui attend une demande sans réponse, et un test le montre
