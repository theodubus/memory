<!-- socle: couche=backlog zone=publique -->
# B-0091 — Un fichier modifié dans la seconde de son dernier ajout passait pour inchangé, et verify ne se relançait pas

> statut : fait · origine : J-2026-10-29-M · ref : J-2026-10-29-M · lu : backlog@bc911780

Les étapes rapides ne se relancent pas sur un contenu déjà vérifié
(B-0086) ; ce contenu se lit en écrivant l'arbre de travail dans une copie
de l'index. La copie prenait la date du moment. Or git ne relit un fichier
dont la taille et la date n'ont pas changé que si son entrée est datée de
la même seconde que l'index : une copie plus récente lui retirait cette
précaution. Un fichier modifié dans la seconde de son dernier `git add`, à
taille égale, passait pour inchangé : `verify --fast` sautait ses étapes
sur un arbre qui avait changé. Reproduit cinq fois sur cinq ; c'était
l'échec intermittent de `verify` resté sans cause (le test
`test_un_arbre_change_se_reverifie`, dans la suite complète seulement).

La copie garde la date de l'index (`shutil.copy2`).
