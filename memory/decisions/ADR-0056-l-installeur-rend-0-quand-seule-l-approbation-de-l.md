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
lui dit : aujourd'hui, `protege.fichiers`. Un autre contrôle en échec, à
corriger ou à passer en adoption, rend 1, comme une erreur de
l'installeur. L'audit et « Et maintenant » ne changent pas.

## Conséquences

Un script qui lance l'installeur distingue un échec d'une installation
qui attend l'humain ; il lit l'audit pour savoir ce qui attend. Le défaire :
`code_de_sortie` et `ATTENTE_HUMAINE` dans `engine/socle/installer.py`, et
leur test dans `tests/test_initialisation.py`.
