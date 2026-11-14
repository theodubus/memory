<!-- socle: couche=decisions zone=publique -->
# ADR-0077 — La fin de tour dit en une ligne les fichiers protégés qu'une mise à jour a posés, reconnus par le verrou du moteur

> statut : acceptée · date : 2026-11-14 · source : B-0196@e7e000e8, ADR-0056@a5d4f150, ADR-0065@88e1a34b, ADR-0061@514e0797 · lu : decisions@b1d7ba83

## Contexte

Entre l'installation d'une mise à jour et le push de sa demande, la fin
de tour refusait l'arbre par une erreur de `protege.fichiers` pour
chaque fichier protégé changé, chacune avec sa commande de remise en état
(ADR-0065@88e1a34b) : 26 lignes sur chess, relues à chaque tentative,
pour une seule cause, la demande pas encore posée (B-0196@e7e000e8). La
commande de remise y est même un mauvais conseil : suivie, elle défait la
mise à jour. Il faut reconnaître, fichier par fichier, ce qu'une mise à
jour a posé, sans couvrir ce qu'un agent changerait pendant qu'elle a
lieu.

## Décision

1. **Le signe d'une mise à jour** : en mode projet, le verrou du moteur a
   changé dans l'arbre depuis la base, et l'empreinte qu'il porte est
   celle du moteur de l'arbre et celle du moteur qu'un passage de
   l'installeur a copié, qu'il écrit sous `copied`. Lancé depuis le
   projet, l'installeur garde le moteur tel quel et récrit le verrou avec
   son empreinte, même s'il a changé : il ne récrit `copied` que si le
   moteur est encore celui qu'un passage précédent a copié (la revue du
   lot l'a trouvé : un module reformaté par l'agent, puis l'installeur
   relancé depuis le projet, passait dans la ligne commune). Un fichier du
   moteur changé après la copie rompt l'égalité, et plus rien n'est
   regroupé (`moteur.empreinte` échoue alors aussi, tant que le verrou
   n'est pas récrit). La version ne dit rien : elle n'a pas changé d'une
   publication à l'autre.
2. **Ce que la mise à jour a posé** : le verrou ; le moteur et son
   lanceur, que l'empreinte couvre, un fichier supprimé du dossier du
   moteur compris, puisque l'installeur le remplace en bloc ; et les
   autres fichiers protégés que l'installeur consigne au verrou, sous
   `[installed]`, avec leur empreinte, tant qu'ils l'ont encore.
   L'installeur n'y consigne qu'un fichier que son passage a changé et
   qui était, avant lui, tel que la base ou un passage précédent l'avait
   laissé : un fichier que l'agent a changé avant de le lancer n'y entre
   pas, même s'il le fusionne ensuite (les réglages de Claude Code, les
   propriétaires du code). Un passage suivant garde les entrées qui
   valent encore.
3. **Où se regroupe l'affichage** : le contrôle garde une erreur par
   fichier, que `socle check` liste et dont `socle approve` tire les
   chemins ; celle d'un fichier posé par la mise à jour ne dit plus de le
   remettre, et porte une ligne commune (« une mise à jour du socle
   attend sa demande : la poser », le nombre de fichiers, la commande qui
   les liste avec leurs empreintes, et le renvoi aux étapes « Et
   maintenant » de l'installeur). Le rapport ne l'imprime à leur place
   que si on le lui demande (`Rapport.texte(regrouper=True)`), ce que
   seule la fin de tour fait. Un fichier qui n'en vient pas garde sa
   ligne et sa commande de remise.
4. **L'arbre de travail seul** : le hook avant commit juge l'index, et la
   CI des commits, où l'empreinte du moteur ne se recalcule pas ; ils ne
   regroupent rien. Le hook avant commit ne voit ces erreurs que sur un
   commit des fichiers de la mise à jour avant que sa demande ne parte,
   une fois par essai, sans les relances de la fin de tour.

## Conséquences

La fin de tour coûte une ligne à l'agent qui a lancé la mise à jour, et
le dirige vers la demande au lieu de la remise. Un fichier dont l'agent
forgerait l'origine en écrivant le verrou, ce que son hook refuse,
entrerait dans la ligne commune : il reste une erreur, et l'humain le lit
dans la demande et la pull request. Le verrou d'un projet mis à jour
porte quelques lignes de plus ; une mise à jour faite par un installeur
d'avant ne les écrit pas, et rien ne s'y regroupe.
Se défait en retirant `poses_par_la_mise_a_jour` de
`engine/socle/checks_ratchet.py`, `_consigner_installes` de
`engine/socle/installer.py` et l'option `regrouper` du rapport.
