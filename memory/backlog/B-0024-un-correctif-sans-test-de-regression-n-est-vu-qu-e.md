<!-- socle: couche=backlog zone=publique -->
# B-0024 — Un correctif sans test de régression n'est vu qu'en CI

> statut : ouvert · origine : J-2026-10-11-F · lu : backlog@9939ea82

Au banc (s9, première version), deux agents ont commité un correctif
(`fix:`) sans test de régression : ni la fin de tour ni le hook avant
commit ne l'ont vu, seule la CI le refuse (`tests.regression` rejoue les
tests sur le parent, trop lent pour un hook). Au moins avertir en fin de
tour qu'un commit `fix:` de la plage n'apporte aucun test nouveau.
