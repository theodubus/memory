# Passation du lot L-0049

T-0206 est fait et commité, mais pas encore relu : la session a rangé
au-delà de 150 000 jetons de contexte (J-2026-11-26-BD). Son commit, en un
correctif : `2026-11-26-L-0049.patch`, qui s'applique par `git am` sur le
commit qui ajoute ce dossier, une fois la passation retirée.

La reprise :

1. appliquer le correctif s'il n'est pas déjà sur la branche ;
2. faire relire le lot de façon adversariale (skill `socle-review`), T-0205
   compris, contre le « Fait quand » de T-0205 et de T-0206. Points à
   éprouver : chaque règle des quatre skills allégés et de la section du
   socle d'`AGENTS.md` se retrouve, intacte, après le déplacement ; chaque
   passage sorti se lit au guide, mot pour mot, dans les deux langues ;
   l'ensemble `PAS_ENCORE` du test des marges ne peut que rétrécir ; les
   trois tests changés sous ADR-0110 et ADR-0111 ne perdent que des phrases
   que le gabarit a quittées ;
3. sur D-0223 (Théo choisit A, J-2026-11-26-BF), poser la demande qui
   relève le plafond des skills de 8 000 à 10 000 octets en nommant sa
   clé et les tests touchés, puis, validée, la faire ;
4. corriger les constats bloquants, retirer ce dossier, puis livrer.
