<!-- socle: couche=backlog zone=publique -->
# L-0018 — Lot des allégements de D-0134 : le coût d'un lot suit sa taille

> statut : ouvert · origine : D-0134 · après : L-0017, T-0037, T-0093, T-0094, T-0095, T-0096, T-0097, T-0098, T-0099 · lu : backlog@7b27e264

Formé le 18 novembre pour les cinq allégements que Théo a validés
(D-0134), écrits dans `docs/fabrication/allegements.md` : que le coût
d'un lot suive sa taille, mesuré sur L-0016 (75 % de la fenêtre de cinq
heures pour un correctif de format). Après L-0017, avant L-0015 : il
allège tous les lots qui suivent.

Ce qu'il portera, une tâche ou plus par proposition :
1. le circuit court des petits lots : l'orchestrateur implémente sous un
   seuil mesuré, le relecteur reçoit un dossier court (le diff et les
   critères), sauf un lot qui touche un garde-fou ou un format que
   d'autres parties lisent (les skills `socle-batch` et `socle-review`,
   `socle review`, leurs copies protégées) ;
2. la variante légère pour des valeurs attendues mécaniques, dans le
   skill `socle-request` du produit (le skill `delegate-lot` la dit
   déjà) ;
3. le hook de fin de tour qui ne recopie plus tous les échecs, mais le
   nom des contrôles, la première ligne utile de chaque test et la
   commande qui montre tout ;
4. une décision de séance qui désigne le texte qu'elle approuve, B-0286 ;
5. le coût d'un lot estimé à son annonce : T-0037, tirée de L-0009, puis
   étendue au lot.

Ses tâches, ouvertes après l'intégration de la passation de L-0016
(J-2026-11-18-S) : pour la 1, T-0093 et T-0094 (B-0288) ; pour la 2,
T-0095 (B-0289) ; pour la 3, T-0096 (B-0290) ; pour la 4, T-0097 et
T-0098 (B-0286) ; pour la 5, T-0037 puis T-0099 (B-0291). Huit tâches,
dont cinq ne changent que des gabarits de skills : le circuit court
qu'il porte s'y applique à mesure qu'il le livre.
