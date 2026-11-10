<!-- socle: couche=decisions zone=publique -->
# ADR-0056 — L'installeur rend 0 quand seule l'approbation de l'humain attend

> statut : acceptée · date : 2026-11-10 · source : B-0150@e0e7990a · lu : decisions@6dc3cd52

## Contexte

L'installeur rendait le code de son audit, les contrôles de la CI : 1 dès
qu'un contrôle échoue. Une mise à jour réussie laisse toujours
`protege.fichiers` en échec, jusqu'à ce que l'humain approuve les
fichiers protégés qu'elle a changés : le pilote a vu 1 pour une mise à
jour réussie, qu'un script lirait comme un échec (J-2026-11-10-H@6cded717).

## Décision

L'installeur rend 0 quand l'installation a réussi et que les seuls
contrôles en échec attendent un geste de l'humain que « Et maintenant »
lui dit : `protege.fichiers`, l'approbation des fichiers protégés qu'elle
a changés, et `prive.verrou` quand le dépôt compagnon n'est pas encore en
place, que pose `socle private install`, réservé à l'humain. « Et
maintenant » lit la même liste pour ne pas les dire à corriger. Un autre
contrôle en échec, à corriger ou à passer en adoption, rend 1 ; un refus
d'installer rend 2, comme avant.

## Conséquences

Un script qui lance l'installeur distingue un échec d'une installation
qui attend l'humain ; il lit l'audit pour savoir ce qui attend. Le défaire :
`code_de_sortie` et `attentes_de_l_humain` dans `engine/socle/installer.py`, et
leur test dans `tests/test_initialisation.py`.
