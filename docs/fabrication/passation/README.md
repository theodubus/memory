# Passation du lot du 13 novembre 2026 : B-0010 et B-0171

La session du 13 novembre a été coupée par la limite de cinq heures, la
semaine à 90 % (J-2026-11-13-E). Deux commits de sous-agents, pas encore
relus jusqu'au bout, n'existaient que dans son conteneur : ils sont ici en
correctifs, sur le commit 5d5906a, pour qu'une session neuve, sur un autre
compte, les reprenne.

- `docs/fabrication/passation/2026-11-13-B-0010.patch` — B-0010, la sortie
  du démarrage bornée, avec sa décision. Relu sans contexte :
  six constats, dont deux de fond, dans
  `docs/fabrication/passation/2026-11-13-constats-B-0010.txt`.
- `docs/fabrication/passation/2026-11-13-B-0171.patch` — B-0171, le hook
  qui développe un chemin écrit comme le shell. Sa revue a été coupée par
  la limite : à refaire.

## Reprendre

1. `git am -3` de chaque correctif, B-0010 d'abord. Le journal se heurte :
   garder toutes les entrées, dans l'ordre des dates.
2. Renuméroter ce que les correctifs prennent en double avec la branche
   (`socle renumber` refuse une collision née d'un rebase, B-0176 : à la
   main, mentions comprises). Pour B-0010 : son entrée de journal du 13 (D)
   prend la première lettre libre, son sujet B-0195 le premier numéro
   libre ; sa décision garde son numéro. Pour B-0171 : son entrée (D), sa
   décision (le numéro suivant celle de B-0010), ses sujets B-0195 et
   B-0196 de même.
3. B-0010 : corriger les six constats (un sous-agent neuf, la consigne et
   les constats), puis une seconde revue, la correction étant lourde.
   La piste de l'orchestrateur pour les constats 1 et 2 : une part de la
   borne par partie de la sortie (l'état dérivé plafonné, chaque ligne
   bornée, ses listes plafonnées ; le chantier actif entier ; les titres
   des faits et des décisions raccourcis, chaque liste coupée dans sa
   propre part), et la ligne de coupe qui dit ce qu'il faut réduire.
4. B-0171 : la revue sans contexte, puis ses corrections.
5. Supprimer ce dossier dans le commit qui intègre le dernier correctif.
