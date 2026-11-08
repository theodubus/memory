<!-- socle: couche=backlog zone=publique -->
# B-0133 — Un tour ouvert pendant une limite quand l'agent attendait sans travailler n'est jamais relancé, et le réveil d'un tour interrompu bute sur un arbre rouge

> statut : ouvert · origine : J-2026-11-08-M · lu : backlog@567e93bb

La règle de la reprise après une limite (ADR-0050) fait reprendre un agent
coupé en travaillant. Elle laisse deux cas, relevés par la revue du lot de
son skill (J-2026-11-08-M) :

- un tour qu'ouvre, pendant une limite, un rappel de l'agent (le check-in
  d'une pull request), un événement de GitHub ou un message de Théo, alors
  que l'agent attendait sans travailler : ses réveils sont retirés, le tour
  est refusé, et rien ne le relance ; le check-in du 8 novembre en est
  peut-être un (J-2026-11-08-I) ;
- le réveil d'un tour que Théo a interrompu, sur un arbre que les contrôles
  jugent rouge : le contrôle de fin de tour refuse de conclure, et pousse
  l'agent à finir le travail interrompu.

Les couvrir change la règle validée : une demande les soumet à Théo, avec
le coût de chaque piste (garder les réveils tant qu'un rappel attend,
c'est accepter des réveils quand l'agent n'est pas coupé).

Fait quand :
- [ ] une demande soumet ces deux cas à Théo, et sa réponse est consignée.
