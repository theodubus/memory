<!-- socle: couche=backlog zone=publique -->
# L-0018 — Lot des allégements de D-0134 : le coût d'un lot suit sa taille

> statut : fait · origine : D-0134 · après : L-0017, T-0037, T-0093, T-0094, T-0095, T-0096, T-0097, T-0098, T-0099, T-0102 · lu : backlog@7b27e264 · ref : J-2026-11-19-E

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
T-0098 (B-0286) ; pour la 5, T-0037 puis T-0099 (B-0291). Le 19 novembre,
T-0102 s'y ajoute à la demande de Théo (J-2026-11-19-A). Neuf tâches,
dont six ne changent que des skills : le circuit court
qu'il porte s'y applique à mesure qu'il le livre.

## Revues

### Passe 1 — 2026-11-19

Commits : 13524e2..f2dc001

- Bloquant : avec pytest, le journal capturé des tests prenait le plafond des lignes d'échec avant le bilan
- Bloquant : le dossier donnait le fichier approuvé tel que le lot l'avait changé, non la version approuvée
- Bloquant : le gabarit socle-batch resserré avait perdu trois règles
- Ouvre : B-0294, B-0295, B-0296, B-0297, T-0103

Recul : les trois bloquants n'ont pas de passe précédente à laquelle se
comparer ; deux viennent du code du sous-agent (une borne prise par le
début de la sortie, un fichier lu dans l'arbre au lieu du début du lot),
le troisième du resserrement que l'orchestrateur a fait sous le plafond
de 8 000 octets, où « sans règle perdue » n'était pas vérifié règle par
règle. Les entrées ouvertes sont de même nature que celles que le lot
ferme (la consommation, l'essentiel des échecs, le dossier de la revue) :
ce sont leurs suites, non des dérives. Les lots clos qui ont touché ces
fichiers, L-0016 et L-0014 sur `review.py` et les skills, ont ouvert des
entrées du même genre, des précisions de format. Les corrections tiennent
en quelques lignes, chacune avec son test : pas de seconde passe ;
continuer.
