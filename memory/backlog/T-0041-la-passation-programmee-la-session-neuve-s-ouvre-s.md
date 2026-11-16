<!-- socle: couche=backlog zone=publique -->
# T-0041 — La passation programmée : la session neuve s'ouvre seule à la remise à zéro de la fenêtre, au lieu d'un prompt à copier

> statut : ouvert · origine : J-2026-11-16-E · besoin : B-0259 · lu : backlog@9966bbbd

La tâche de B-0259, que la migration du backlog en quatre formes a posée dans le lot L-0010 : elle reprend ses critères, à récrire en livrable qu'un test vérifie.

## Fait quand

- [ ] l'essai de B est fait et son relevé écrit, chaque inconnue levée ou dite non levée ; A n'est essayée que si B échoue
- [ ] Théo a confirmé la variante sur ce relevé
- [ ] la spécification de la passation programmée et du commutateur est soumise à Théo avant son code, pour la seule variante retenue
- [ ] en mode « session programmée », le rangement programme la session neuve au lieu de donner le prompt, et un test le montre pour ce qui se teste sans la plateforme
- [ ] changer de mode annule ce qui est programmé, et la garde contre le travail en double est écrite dans le prompt de passation
