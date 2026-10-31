<!-- socle: couche=backlog zone=publique -->
# B-0115 — Une mise à jour en session cloud ne peut pas finir son tour : ses fichiers protégés attendent la validation de l'humain

> statut : fait · origine : J-2026-10-31-T · lu : backlog@db1569b5 · ref : J-2026-10-31-T

Trouvé en rafraîchissant les fichiers protégés de ce dépôt (B-0102) par
la voie de la mise à jour en session cloud (B-0107) : l'installeur change
les fichiers protégés, l'agent pose une demande qui cite chacun avec son
empreinte, et l'humain la valide dans la conversation, au tour suivant.
Mais `protege.fichiers` échouait sur l'arbre en attendant : le hook de
fin de tour refusait de conclure, et le tour ne finissait qu'après trois
refus, par une escalade. Les valeurs attendues des tests avaient déjà ce
répit (B-0033), pas les fichiers protégés.

Correctif : à la fin du tour seulement, une demande en attente, poussée
telle quelle, qui cite le fichier et son empreinte nouvelle, laisse le
fichier dans l'arbre ; le commit et la CI attendent toujours la réponse.
Un test et un témoin de l'auto-test l'établissent ; l'étape de mise à jour
de l'installeur le dit.
