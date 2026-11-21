<!-- socle: couche=backlog zone=publique -->
# T-0121 — À une mise à jour, l'installeur imprime en entier les notes de version qui demandent une action, et des autres le titre et le fichier

> statut : ouvert · origine : J-2026-11-21-D · besoin : B-0324 · lu : backlog@d8734f07

Un commit : `texte_des_notes` (`engine/socle/installer.py`) n'imprime en
entier, à une mise à jour, que les notes de version dont « À faire »
n'est pas « rien » ; des autres, leur titre et le fichier où les lire,
`engine/socle/CHANGES.md`, en français et en anglais ; sa note de
version, et ses cas dans la suite du dépôt. Théo la place avant la mise
à jour de chess (D-0152), dans le lot de l'installeur qui suit L-0008 :
L-0021.

## Fait quand

- [ ] à une mise à jour, une note dont « À faire » demande une action s'imprime en entier, et un test le montre
- [ ] une note dont « À faire » est « rien » ne s'imprime que par son titre et le fichier où la lire, en français comme en anglais, et un test le montre
