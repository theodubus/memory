<!-- socle: couche=backlog zone=publique -->
# T-0099 — Le skill socle-batch estime le coût d'un lot à son annonce, depuis les coûts mesurés, et le découpe, le réduit ou attend la remise à zéro s'il ne tient pas dans ce qui reste

> statut : ouvert · origine : D-0134 · après : T-0037 · besoin : B-0291 · lu : backlog@7ec4d25a

Un commit, après T-0037 : le gabarit du skill `socle-batch`, en
français et en anglais, fait estimer à l'annonce d'un lot son coût, par
les coûts mesurés d'un sous-agent qui implémente, d'un relecteur et
d'une demande, et, s'il ne tient pas dans ce qui reste de la fenêtre, le
découper, commencer par un lot plus petit ou attendre la remise à zéro.
Une note de version ; la copie protégée suit par une demande.

## Fait quand

- [ ] le gabarit de `socle-batch` et son anglais font estimer le coût d'un lot à son annonce, et dire ce qui se fait s'il ne tient pas, et un test le lit
