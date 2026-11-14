<!-- socle: couche=decisions zone=publique -->
# ADR-0079 — Un lot se garde au backlog comme un sujet de forme lot, qui attend ses sujets ; sa conduite est le skill socle-batch

> statut : acceptée · date : 2026-11-14 · source : B-0199@528031a5, B-0220@0df68693, J-2026-11-14-M@567221ed, ADR-0037@10b3bfbe, ADR-0034@abef67cd, ADR-0033@44523582, ADR-0027@d32b4ef9 · lu : decisions@9ecc00fd

## Contexte

Ce dépôt mène ses lots par une procédure à lui, le skill `delegate-lot`,
que l'installeur ne pose pas ; Théo veut que ce qui est utile entre dans
le produit (J-2026-11-13-F@8a674408), et qu'on apprenne au socle à réunir les
sujets qui se traitent facilement ensemble (J-2026-11-14-M@567221ed).
Les lots ne vivaient que dans la prose du chantier actif, que rien ne
relie aux sujets ni ne montre l'état : une session neuve ne les retrouve
que si le chantier actif les a gardés. B-0199@528031a5 demande le skill
du produit, la mémoire qui relie un lot à ses sujets et l'état qui
montre le prochain ; B-0220@0df68693, l'étape d'après la fusion, qui
poussait une branche vide de tout travail et recréait la branche
distante supprimée.

## Décision

1. **Un lot est un sujet du backlog** marqué `forme : lot` (`form:
   batch` en anglais), qui attend ses sujets par `après`, et le lot
   d'avant s'il y en a un, comme un jalon (ADR-0037@10b3bfbe) : aucune
   notion de plus, aucun fichier de plus. Son corps dit ce qui réunit ses
   sujets ; ce qui n'est pas un sujet (une règle qu'une demande autorise)
   s'y nomme dans le texte. Le lot n'est pas un sujet à prendre : il
   n'est jamais « prêt ».
2. **L'état montre le prochain lot**, à côté du prochain jalon : ouvert,
   qu'aucun lot ouvert ne précède de proche en proche, celui qui est en
   cours d'abord, puis par identifiant ; et l'avancement de chacun de
   ses sujets (clos, en cours, bloqué, prêt, ou qui attend) et de ses
   demandes (répondue ou sans réponse). Le rappel de fin de tour le
   redonne. Le rang des sujets prêts ne change pas : un lot ne passe pas
   devant une priorité que l'humain a donnée.
3. **Un lot se clôt quand ses sujets le sont** : `memoire.ordre` refuse
   déjà un sujet fait avant ce qu'il attend ; aucun contrôle nouveau.
4. **Former un lot** : réunir les sujets prêts qui touchent les mêmes
   fichiers, le même garde-fou ou les mêmes tests, pour qu'une seule
   revue les juge ensemble. La règle s'écrit dans le format et dans le
   skill ; le moteur n'aide pas à la former : les fichiers qu'un sujet
   touchera ne se lisent que dans sa prose, et une aide qui devinerait
   se tromperait sans qu'un test le voie.
5. **La conduite d'un lot est le skill `socle-batch`**, posé et protégé
   comme les autres skills du socle, dans les deux langues : son nom en
   anglais au préfixe du socle (ADR-0027@d32b4ef9, ADR-0034@abef67cd),
   `batch` traduisant `lot` comme dans le vocabulaire de la mémoire. Il
   ne dit que des règles générales, sans rien de l'atelier
   (ADR-0033@44523582) : annoncer et former le lot ; un sous-agent par
   sujet, deux à la fois au plus ; la revue sans contexte avant tout push
   (`socle-review`) ; l'intégration et la renumérotation des collisions ;
   l'attente de la CI sur le commit de tête ; la fusion telle que les
   instructions du projet la donnent ; une session par lot ; les seuils
   des fenêtres de cinq heures et de la semaine ; le changement de
   session avec le prompt de la suivante, un commit pas encore relu
   sauvé en correctif avant de passer la main. Un agent sans sous-agents
   mène le lot seul, dans le même ordre.
6. **Après la fusion, rien ne se pousse sans travail neuf** (B-0220) : le
   chantier actif et le journal s'écrivent avant la fusion, dans le
   dernier commit de la pull request, ou partent avec le travail suivant ;
   la branche locale repart de la branche par défaut et ne se pousse
   qu'avec le premier commit du lot suivant.

## Conséquences

Un lot survit à la fin d'une session : l'état le donne à la suivante.
`delegate-lot` ne garde que ce qui est propre à ce dépôt et renvoie au
gabarit du produit. La copie protégée du skill dans ce dépôt, et les
deux tests qui comptent les skills du socle, ne changent qu'avec une
demande validée (politique, points 1 et 2). Un sujet peut appartenir à
deux lots, et un lot sans `après` passe : ni l'un ni l'autre n'est
refusé. Pour défaire : retirer `est_lot` et la ligne du prochain lot de
`engine/socle/memory.py`, et le dossier du skill de
`engine/socle/templates/skills/` ; un sujet `forme : lot` se lit alors
comme un sujet ordinaire qui attend ses sujets.
