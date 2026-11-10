<!-- socle: couche=backlog zone=publique -->
# B-0150 — L'installeur rend 1 quand l'installation réussit et que l'audit attend des validations

> statut : fait · origine : J-2026-11-10-H · lu : backlog@95c74b2b · ref : J-2026-11-10-I

L'installeur rend 1 quand l'installation réussit mais que son audit
attend des validations (J-2026-11-10-H) : un script le lirait comme un
échec. Piste du pilote : un code distinct, ou 0 avec l'audit en
avertissement.

## Fait quand

- [x] le code de sortie de l'installeur distingue un échec d'une installation réussie qui attend l'humain, et un test le montre
