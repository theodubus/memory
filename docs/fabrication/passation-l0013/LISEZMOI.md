# Passation du lot L-0013, le 16 novembre au soir

La session du 16 novembre (J-2026-11-16-V à J-2026-11-16-Y) s'arrête au
seuil de la fenêtre de cinq heures (60 %), selon la consigne de Théo :
la passation se fait avant la limite. Tout est poussé, sauf les vingt
tests que D-0125 nomme, rangés ici, compressés comme dans la passation
d'avant, pour qu'aucun contrôle ne lise le correctif comme un texte du
dépôt. Ce dossier se retire dans le commit qui les intègre.

## Ce qu'il contient

- `tests-attendus.diff.gz` : les vingt tests de D-0125, dans six fichiers
  de `tests/` ; `gunzip -c` puis `git apply`. Avec eux, la suite entière
  passe ; sans eux, la CI de la branche échoue sur eux.

## Où en est le lot

- T-0046 (B-0265) : relu (passe 1), ses trois bloquants corrigés, poussé.
- T-0047 (B-0263) : relu (passe 2), ses deux bloquants corrigés, poussé.
  Les deux passes et leurs reculs sont dans la section « Revues » de
  L-0013 : la passe suivante, celle de T-0048, s'y écrit en passe 3.
- T-0048 (B-0270) : à faire ; sa revue, puis la clôture du lot.
- D-0125 : poussée, en attente de Théo ; ses empreintes sont celles des
  gabarits au commit de la correction de T-0047.

## La reprise, dans l'ordre

1. Si Théo a répondu à D-0125 : consigner sa réponse (skill
   `socle-request`), appliquer le correctif, et, s'il a validé les copies,
   les poser par l'installeur relancé dans le mode du verrou, puis remettre
   en état ce qu'il change d'autre (J-2026-11-15-F). Les copies validées
   sont les gabarits du commit que citent les liens de D-0125 : à poser
   avant que T-0048 change de nouveau le gabarit de `socle-review`. Le
   commit des tests, des copies et de la réponse part dans un même push.
2. T-0048, selon le skill `delegate-lot`, puis sa revue (passe 3, avec son
   recul), puis la clôture de L-0013, la pull request, la CI, la fusion.
3. Sans réponse de Théo, T-0048 se fait quand même ; les copies de
   D-0125, si Théo les valide après, se posent depuis le commit cité.
