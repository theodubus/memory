# Passation du lot 3, suite, le 14 novembre

Le lot 3 (B-0221, le hook) a été repris d'une première passation, intégré,
relu une première fois et corrigé ; il reste à faire relire sa correction,
à corriger un dernier bloquant, puis à le livrer. La fenêtre de cinq heures
de la session qui l'a repris a passé 60 %, le seuil au-delà duquel le skill
`socle-batch` ne lance plus de sous-agent : une session neuve le finit.
Rien de ce code n'est sur la branche par défaut ; il est ici en neuf
correctifs, partis de c79f96b. Les identifiants qu'ils créent (une ADR,
des entrées de journal, trois sujets) n'existent qu'une fois appliqués :
ce texte les décrit sans les nommer.

## Les correctifs

1. à 5. La règle 2 de D-0112 (une ADR nouvelle), B-0208, B-0205, B-0204 et
   B-0207, de la première passation, leurs identifiants déjà renumérotés
   (les entrées de journal du 14 novembre de AB à AF, les notes de version
   `2026-11-14-f` à `-j`).
6. B-0206 fini, et un sujet ouvert : le script python qu'un heredoc donne.
7. La revue sans contexte : cinq bloquants, et un sujet ouvert : `xargs` et
   `python -c` jugés par les seuls chemins qu'ils citent.
8. La correction des bloquants : un analyseur des expressions de `find`,
   le corps d'une fonction, les boucles qui reviennent à leur dossier, et
   un opérateur écrit entre guillemets ou échappé lu comme un mot ; les
   notes de version corrigées en place.
9. Ce qui reste, et un sujet ouvert : la conjonction de filtres d'un
   `find`, jugée filtre par filtre.

Chaque correctif a son entrée de journal, qui dit le détail. Ils ne
touchent ni ce dossier ni le chantier actif : ils s'appliquent sans
conflit sur la branche par défaut qui a reçu cette passation (vérifié sur
une copie). Si elle a reçu autre chose depuis, une entrée de journal, une
note de version ou un sujet peuvent se heurter : renuméroter
(`python3 .socle/socle renumber <ID>`).

## Ce qu'il reste à faire, selon le skill delegate-lot

1. Sur la branche de la session, partie de la branche par défaut :
   `git am docs/fabrication/passation/2026-11-14-lot-3-suite/*.patch`.
2. Le bloquant restant, que dit l'entrée de journal du neuvième
   correctif : `for d in .socle memory; do cd $d; echo x > policy.toml;
   done` passe le hook ; la variable d'un `for` à plusieurs valeurs, cible
   d'un `cd`, doit devenir inconnue ou se juger valeur par valeur (le
   modèle de menace de B-0204). Un test qui échoue sur le commit parent ;
   `for d in */; do cd "$d"; ls; cd ..; done` doit continuer de passer.
3. La seconde revue, sur la correction seule : `python3 .socle/socle
   review --since <SHA du septième correctif appliqué>`. Ses constats
   classés par la règle de D-0111 ; ses bloquants corrigés.
4. La clôture du lot, dans le dernier commit : B-0221 passé `fait` et
   rangé (`python3 .socle/socle archive`), le chantier actif réécrit, une
   entrée de journal, et le point du hook ajouté au prompt de mise à jour
   de chess (`docs/fabrication/chess/prompt-mise-a-jour.md`,
   J-2026-11-13-L), dont le brouillon est `prompt-chess-point-10.txt`,
   écrit avant la correction des bloquants : à compléter de ce qu'elle
   change (l'expression d'un `find`, le corps d'une fonction) ; ce
   dossier retiré dans ce même travail.
5. `python3 .socle/socle verify --fast` (onze minutes), le push, la pull
   request, la CI verte, la fusion par l'agent (D-0092), puis la
   distribution vérifiée.
