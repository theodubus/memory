<!-- socle: couche=decisions zone=publique -->
# ADR-0099 — Une forme du shell que le hook ne juge pas ne se liste ni ne se signale plus, dans le produit comme dans l'atelier : ADR-0085 remplacée

> statut : acceptée · date : 2026-11-20 · source : ADR-0085@d249f179, ADR-0098@3081a5ed, D-0128@fd7c9ad7, D-0143@04eddcb5, ADR-0082@beb85978, T-0060@4ff7dafb, T-0061@0842a0be · lu : decisions@1bc25f37

## Contexte

ADR-0085@d249f179 faisait nommer au récap, dans un projet équipé, une
forme du shell que le hook de l'agent ne juge pas, et proposer à
l'humain de la signaler au dépôt public du socle ; seul ce dépôt
écrivait la liste des formes connues, dans le guide. Depuis, Théo a
retiré cette procédure du produit (D-0128@fd7c9ad7, le 17 novembre) :
les projets n'ont pas à juger le hook. T-0061 devait alors garder la
liste dans l'atelier, sous `docs/fabrication`, et écrire la règle
d'ADR-0082@beb85978 dans le skill `delegate-lot`. Puis Théo a déclaré
le hook terminé (D-0143@04eddcb5, ADR-0098@3081a5ed, le 20 novembre) :
il ne change que sur une preuve vue dans une session, et un
contournement qu'un relecteur trouve s'écarte d'office. ADR-0098
remplace ADR-0082, et sa règle est déjà dans le skill `delegate-lot`.

## Décision

Une forme du shell que le hook ne juge pas ne se liste plus, ni dans le
guide du produit, ni dans l'atelier, et ne se signale plus : un
relecteur ne la cherche pas, et une forme trouvée s'écarte sans ligne
ni entrée. La seule voie vers le hook est la preuve d'ADR-0098. La
liste qu'avait le guide reste lisible dans l'historique du dépôt ; le
retrait de la procédure du produit est T-0060, et rien ne la remplace
dans l'atelier. ADR-0085 est remplacée.

## Conséquences

- Le skill `delegate-lot` garde la règle d'ADR-0098 pour la revue d'un
  lot du hook, et un test le garde ; la liste ne va pas dans
  `docs/fabrication`, et T-0061 se clôt sur cette décision.
- Dans un projet équipé, le récap ne nomme plus de forme et « Pour toi »
  ne propose plus de signalement (T-0060, dans le produit).
- Pour défaire : une décision nouvelle de Théo, qui rouvrirait le hook
  au-delà d'ADR-0098.
