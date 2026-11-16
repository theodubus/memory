<!-- socle: couche=backlog zone=publique -->
# B-0165 — L'agent ne peut pas remettre un fichier protégé à son état commité, même après l'avoir changé par erreur

> statut : fait · origine : J-2026-11-11-F · lu : backlog@77cbfa34 · pour : humain · ref : J-2026-11-11-O

Sur un projet en mode projet, la commande de l'incident de B-0141
(`install --target . --adapter kotlin --owner @essai`) passe le hook de
l'agent : le mode demandé est celui du verrou (ADR-0062). Elle réécrit
l'adaptateur, CODEOWNERS et les hooks ; le contrôle des fichiers
protégés arrête le commit, mais le hook refuse à l'agent la remise de ces
fichiers à leur état commité, qu'il réserve à l'humain. La piste,
permettre cette remise à l'agent, assouplit un garde-fou, au risque
d'effacer un changement que l'humain n'a pas encore commité : c'est à
l'humain de dire s'il la veut, et sous quelle condition (par exemple,
seulement les fichiers que l'agent a lui-même changés dans le tour).

## Satisfait quand

- [x] l'humain a tranché la piste, et, s'il la veut, l'agent remet un fichier protégé qu'il a changé par erreur à son état commité sans pouvoir effacer un changement de l'humain, et un test le montre

Ce qui est tenu (ADR-0065) : un fichier que cite, lui ou son dossier, une
demande en attente, ou validée sans que ce qu'elle approuve soit commité,
est épargné, et un test le montre. Ce qui ne l'est pas, accepté par
D-0098 : une modification de l'humain dans l'arbre de travail, ni commitée
ni soumise par une demande, peut être effacée par la remise.
