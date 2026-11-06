<!-- socle: couche=backlog zone=publique -->
# B-0127 — Une demande ne peut pas citer un fichier protégé qu'elle propose d'ajouter : le chemin absent est refusé

> statut : fait · origine : J-2026-11-02-L · ref : J-2026-11-02-L · lu : backlog@9eaa5e2a

Une mise à jour du socle qui pose un fichier protégé nouveau, comme le skill
`socle-review` (B-0124), se fait valider par une demande qui cite le fichier
et son empreinte (B-0115, D-0071). Mais `memoire.references` refusait la
demande : elle citait entre accents graves un chemin encore absent de ce
qui est commité. Relevé en posant la demande du skill dans ce dépôt ; le
pilote l'aurait rencontré à sa prochaine mise à jour.

À faire : dans une demande, un chemin protégé cité n'a pas à exister. La
demande peut proposer de l'ajouter ou de le retirer, et `protege.fichiers`
juge le changement avec son empreinte. Ailleurs, ou pour un chemin qui
n'est pas protégé, le chemin absent reste refusé.
