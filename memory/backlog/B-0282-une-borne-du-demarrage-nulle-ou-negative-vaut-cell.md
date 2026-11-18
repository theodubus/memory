<!-- socle: couche=backlog zone=publique -->
# B-0282 — Une borne du démarrage nulle ou négative vaut celle du gabarit, que le cliquet laisse écrire librement : [startup] max_bytes = 0 relève en silence une borne plus basse

> statut : ouvert · origine : J-2026-11-18-B · lu : backlog@ead98240

Vu en écrivant le seuil des étapes rapides (T-0045, J-2026-11-18-B), pas
corrigé : un défaut voisin. `Projet.borne_demarrage` rend la borne du
gabarit (9 500 octets) pour une valeur de `[startup] max_bytes` nulle,
négative ou qui n'est pas un entier ; le cliquet des garde-fous, sens
« bas », juge l'écrire plus bas comme un durcissement, libre. Un projet
dont la borne vaut 8 000 qui écrit 0 la relève donc à 9 500 sans
demande. Déduit de la lecture du code, non reproduit. L'effet est borné
par la valeur du gabarit, que Claude Code remet entière ; le seuil
`[verify] fast_max_seconds` évite le même trou en prenant une valeur nulle
ou négative pour la plus stricte.

## Satisfait quand

- [ ] aucune valeur de `[startup] max_bytes` que le cliquet laisse écrire sans demande ne relève la borne effective, et un test le montre
