<!-- socle: couche=backlog zone=publique -->
# B-0148 — « Et maintenant » ne dit pas l'ordre des commits d'une mise à jour en session cloud, que le hook avant commit impose

> statut : ouvert · origine : J-2026-11-10-H · lu : backlog@e41bab5c

À la mise à jour du pilote en session cloud (J-2026-11-10-H), le hook
avant commit a refusé deux fois : le journal citait la copie de
l'adaptateur `kotlin`, pas encore commitée, et le chantier actif
une entrée du journal que le commit ne contenait pas. Ce qui a marché :
commiter et pousser la demande seule, puis commiter les fichiers
protégés avec le journal et le chantier actif qui les citent. L'étape 2
de « Et maintenant » propose un seul commit de tout, alors que l'étape 1
dit que la demande poussée laisse ensuite commiter les fichiers protégés.

## Fait quand

- [ ] « Et maintenant », en session cloud, dit l'ordre des commits d'une mise à jour, et un test le montre
