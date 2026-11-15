# Passation du lot 5 (B-0223), la revue

Le lot a été commencé le 15 novembre (J-2026-11-15-F, J-2026-11-15-H) et
rangé pour une session neuve quand la fenêtre de cinq heures a passé
60 %. Ce dossier se retire quand le lot s'intègre.

## Ce qu'il contient

`0001-B-0213-le-dossier-de-la-revue-mesure-le-lot-depuis-l.patch` : le
commit de B-0213, fait par un implémenteur dans sa copie isolée, sur
`5167550`, ni relu ni poussé. Il apporte une décision nouvelle, qui
complète ADR-0075 (toute base se mesure depuis son ancêtre commun avec
HEAD ; une référence qui ne mesure pas le lot est refusée, code 2 ; la
barre ne prend que les sujets dont le lot change le statut ou le « Fait
quand »), le code, treize tests (douze échouent sur le parent), la
documentation, les notes de version, son entrée de journal, la lettre
qui précède celle de J-2026-11-15-H, et B-0213 clos et rangé.
`sujets_du_lot` garde sa forme, `(servis, ouverts)` ; ni `sujets_fermes`,
ni `CONSIGNE_CLASSES`, ni les trois tests de D-0116 n'y sont touchés.

## Reprendre

1. Appliquer le correctif sur la branche de travail : `git am -3`. Deux
   conflits attendus : son entrée de journal se place avant
   J-2026-11-15-H, déjà poussée ; `memory/active.md` garde le texte de la
   branche.
2. Lancer B-0214 dans une copie isolée, après l'intégration du correctif.
   Ses critères comprennent la règle 1 de D-0112 (la consigne du
   relecteur, le skill de revue et les instructions des projets), D-0116
   et D-0117. Le correctif a déjà récrit la ligne de `review.py` dans
   `docs/fabrication/architecture.md` (une part du premier critère).
3. D-0116 est validée, mais sa réponse ne se commite qu'avec les trois
   tests qu'elle nomme, dans le même push (ADR-0076). La consigner de
   nouveau dans ce commit, avec le texte exact de Théo et sa lecture :
   `socle answer D-0116 valider --relayed --by Théo`, citation
   « Valider D0016 », texte « « D0016 » lu comme D-0116, la seule demande
   en attente : D-0016 est une demande d'octobre, déjà répondue. »
4. La revue du lot entier (B-0213 et B-0214), le relecteur sur Opus
   (D-0117) ; puis l'intégration, la CI, la fusion et le prompt de mise à
   jour de chess, selon le skill `delegate-lot`.
