<!-- socle: couche=backlog zone=publique -->
# B-0330 — Un test des notes de version échoue dès que la plus récente ne demande rien

> statut : abandonné · origine : J-2026-11-22-N · ref : J-2026-11-22-M, J-2026-11-22-P · priorité : basse · lu : backlog@b3b601d1

`test_le_texte_dit_quoi_en_faire` (`tests/test_notes_de_version.py`)
prend la plus récente des notes de version et attend que le texte de la
mise à jour finisse par son texte entier. Une note dont « À faire » est
« rien. » ne s'imprime qu'en titre : le test échoue alors, sans que rien
ne soit faux. T-0033 l'a rencontré en écrivant la note 2026-11-22-i,
dont « À faire » dit en vérité quand s'en servir (« rien, sauf
quand … ») ; la prochaine note qui ne demande rien le fera échouer.
Le test est d'un autre module, hors du périmètre de T-0033 ; s'il faut
y changer une assertion, une demande validée la nomme.

## Satisfait quand

- [ ] une note de version la plus récente dont « À faire » est « rien. » ne fait échouer aucun test, et le test garde ce qu'il vérifie d'une note qui demande quelque chose
