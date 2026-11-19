# Passation du lot L-0019

Sept commits du 19 novembre, faits dans la session ouverte à 19 h 27 UTC,
qui suivent cee8d33, la tête poussée de la branche
`ccr-f176849a-qbyj74`, où D-0140 est posée. La fenêtre de cinq heures
est à 68 % : ce qui reste du lot, environ 60 points, ne tient pas avant
sa remise à zéro (l'entrée de journal du commit 6). Les six premiers
passent `verify --fast`. Rien n'en est poussé : la série n'est pas
relue, et le commit 7 porte la réponse de Théo à D-0140, qui ne part
qu'avec le changement qu'elle autorise. Ce dossier se retire au commit
qui l'intègre.

1. T-0001, par le sous-agent du lot : le corps d'un heredoc donné à
   python se juge comme le script d'un `python -c` (le découpage garde
   le corps de chaque heredoc, `Commande.entree`, et une ADR le dit) ;
   note de version 2026-11-19-p ; B-0229 satisfait.
2. T-0070 : les arguments qui suivent le script d'un `python -c` se
   jugent comme les chemins qu'il cite, quand le script lit ses
   arguments (`LIT_SES_ARGUMENTS`, sans ADR : son entrée de journal le
   dit) ; note 2026-11-19-q.
3. T-0004 : `find … | xargs rm` se juge comme un `find` qui supprime
   depuis ses départs (chaque commande d'un pipeline connaît celle qui
   la précède, `Commande.amont`, et une ADR le dit) ; note 2026-11-19-r ;
   B-0246 satisfait. T-0002 arrêtée sur un test qui la contredit (dans
   la même entrée de journal).
4. T-0003 : la garde d'une action d'un `find` est une disjonction de
   conjonctions, et le motif d'un `-path` ne vise que ce qui est sous
   ses départs (une ADR, écrite par `cp` après un refus du hook que la
   session n'a pas su reproduire : l'entrée de journal du commit 6) ;
   note 2026-11-19-s ; B-0231 satisfait.
5. T-0106 arrêtée avant son code, sur un test et un défaut injecté qui
   la contredisent.
6. La passation : son entrée de journal, un besoin nouveau sur les
   réveils qu'une session archivée laisse (skill `socle-resume`), la
   troisième case de T-0106 (la substitution d'une commande qui change
   de branche ou de dépôt reste refusée, comme D-0140 le dit à Théo),
   l'état du lot.
7. La réponse de Théo, mot pour mot : D-0140 `valider`, consignée par
   `socle answer --relayed` ; les propositions 1 et 2 sur les valeurs
   attendues des tests retenues en décision de séance ; trois besoins
   nouveaux (ces deux propositions, et la fausse alerte « hooks git non
   branchés » d'un `core.hooksPath` absolu) et la tâche du dernier ;
   l'entrée de journal qui le dit.

## La suite

1. Sur la branche de la session neuve, partie de la branche par défaut :
   `git fetch origin ccr-f176849a-qbyj74`, `git merge --ff-only
   FETCH_HEAD` (à défaut, `git merge --no-edit FETCH_HEAD`), puis
   `git am -3 docs/fabrication/passation-l0019/*.patch`. Un commit
   retire ensuite ce dossier et récrit le chantier actif. Rien ne se
   pousse avant la revue : le commit 7 porte la réponse à D-0140.
2. Théo a validé D-0140 : un sous-agent fait T-0002 puis T-0106, un
   commit chacune, les trois valeurs attendues changées comme D-0140 les
   dit, et la troisième case de T-0106 tenue ; pour T-0002, `grep -r`
   (`-R`, `--recursive`) et `git ls-files` comme un `find` sans filtre,
   `Commande.amont` donnant le producteur.
3. Ce que Théo a retenu en séance s'applique déjà : une tâche qui
   contredit la valeur attendue d'un test le nomme, et sa demande précède
   le lot ; un témoin qui doit passer est sans danger, un trou connu va à
   une liste de limites qui cite son entrée du backlog.
4. La revue du lot entier, depuis 852b0ac (skill `socle-review`, dossier
   complet : le lot touche un garde-fou) ; le relecteur éprouve
   notamment l'ADR de la garde d'un `find` et ses bornes, le resserrement
   de T-0070 aux scripts qui lisent leurs arguments, et le `_cites` qui
   ne cherche plus un mot sans barre oblique ni point de tête parmi les
   fichiers suivis (l'ADR du corps des heredocs).
5. Ses bloquants corrigés, le lot se clôt (son recul, L-0019 `fait`,
   `socle archive`), le prompt de mise à jour de chess
   (`docs/fabrication/chess/prompt-mise-a-jour.md`) dit ce que reçoit un
   projet, la branche se pousse, et sa pull request se fusionne à la CI
   verte ; puis la distribution se vérifie.

## À l'intégration

- `git am` change les SHA de la série ; aucune de ses entrées ne cite un
  SHA de commit, seulement des empreintes de lecture : rien à récrire.
- La série prend les lettres AD à AJ du journal du 19 novembre, les
  trois décisions qui suivent la dernière de la branche, la demande qui
  suit D-0140, quatre besoins nouveaux, une tâche nouvelle et les notes
  de version 2026-11-19-p à s ; la session neuve numérote après elles.
