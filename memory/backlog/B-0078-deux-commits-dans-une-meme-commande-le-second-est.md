<!-- socle: couche=backlog zone=publique -->
# B-0078 — Deux commits dans une même commande : le second est refusé comme si les hooks n'étaient pas chargés

> statut : ouvert · origine : J-2026-10-20-R · lu : backlog@1615e20b

Mesuré le 20 oct. : deux `git commit` enchaînés dans une même commande de
l'agent ; le premier passe, le second est refusé par `hooks.filtre`, « ses
hooks ne sont pas chargés », avec le conseil de relancer la session. Or le
filtre de l'agent avait tiré juste avant la commande : il ne tire qu'une
fois par commande, et le compte depuis le commit précédent est nul pour le
second. Le refus est juste dans son effet (un commit par commande), mais
son message égare : il fait croire à des hooks déchargés. Le dire tel quel
quand le filtre a tiré dans la session, ou compter depuis le début de la
commande plutôt que depuis le commit précédent.
