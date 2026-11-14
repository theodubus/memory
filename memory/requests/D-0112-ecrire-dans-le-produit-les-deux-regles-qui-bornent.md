<!-- socle: couche=demandes zone=publique -->
# D-0112 — Écrire dans le produit les deux règles qui bornent le backlog : le tri des remarques non bloquantes de la revue, et la limite du hook de l'agent

> date : 2026-11-14

## Décision demandée

Autoriser l'agent à écrire, dans le moteur que reçoit chaque projet, les deux règles ci-dessous, au mot près, qui disent quels constats et quels trous du hook méritent un sujet du backlog.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui rend fiables la mémoire, la documentation et les tests d'un projet de code entretenu par un agent d'IA. Le moteur est ce qu'un projet reçoit à l'installation (chess, par exemple) ; ce dépôt s'en sert lui-même, comme premier projet équipé.

**Le chantier.** Le 14 novembre, vous avez remarqué que le backlog (la liste des sujets à traiter) grossissait plus vite qu'il ne se vidait : 79 sujets ouverts pour 36 fermés du 9 au 14 novembre, contre un solde à peu près nul les semaines d'avant. Deux sources ne s'arrêtent pas seules : les remarques non bloquantes des revues, et les trous du hook de l'agent.

**La question.** Vous avez validé dans la conversation la distinction entre remarques importantes et exotiques, et la règle qui en découle (D-0111) ; les sujets exotiques sont déjà écartés. Reste à écrire les deux règles dans le produit, pour qu'elles valent dans chaque projet et pas seulement dans ce dépôt, comme vous l'avez demandé.

Deux termes, d'abord. La **revue** : avant de livrer un lot de travail, l'agent le fait relire par un autre agent sans son contexte, qui cherche à le prendre en défaut ; un constat **bloquant** se corrige dans le lot, les autres allaient jusqu'ici tous au backlog (votre décision du 13 novembre, D-0109). Le **hook de l'agent** : un programme qui lit chaque commande de l'agent avant qu'elle tourne, et refuse celle qui écrirait un fichier protégé (la politique, les hooks, la CI) ou ferait une action irréversible. Pour deviner ce qu'une commande fera, il doit relire le langage du shell, qui a une infinité de formes ; chaque revue en trouve de nouvelles. Derrière lui, un second contrôle, `protege.fichiers`, compare l'empreinte de chaque fichier protégé à la fin du tour, au commit et sur GitHub : il attrape toute écriture, quelle qu'en soit la forme.

**Règle 1, la revue.** Écrite dans le skill `socle-review` (la procédure de la revue, en français et en anglais), dans la consigne du relecteur et dans la section du socle du fichier d'instructions des projets :

> **Pour le backlog** : un constat qui ne bloque pas, s'il peut se produire dans l'usage normal du projet, ou si rien ne rattrape ensuite son effet (ni un contrôle, ni la CI) ; un sujet par constat, ou un pour plusieurs de même nature. **Écarté** : un constat exotique (un geste rare, une forme qu'on n'écrit que pour contourner, un cas jamais reproduit) dont l'effet se voit ou se rattrape, et un constat infondé ; une ligne du récap dit pourquoi.

**Règle 2, le hook.** Écrite comme le modèle de menace du hook (ce qu'il arrête, ce qu'il laisse passer), dans une décision et dans le guide d'un projet équipé :

> Le hook de l'agent arrête les erreurs d'un agent coopératif avant qu'elles agissent. Il juge les formes du shell qu'un agent écrit dans son travail, et, quelle qu'en soit la forme, ce que rien ne rattrape ensuite : supprimer le projet ou un dossier qui le contient, une action externe irréversible, une fuite de la mémoire privée dans ce qui se publie. Une écriture d'un fichier protégé sous une forme qu'on n'écrit que pour contourner (un `eval`, `IFS`, un chemin construit au vol dans un autre langage) est hors de son modèle : `protege.fichiers` l'attrape, et elle n'ouvre pas de sujet.

## Éléments cités

- D-0111@034d5e87 — votre décision en séance du 14 novembre : la distinction entre remarques importantes et exotiques, et les sujets écartés.
- D-0109@379b5396 — votre décision du 13 novembre : seuls les bloquants se corrigent dans le lot, le reste va au backlog.
- ADR-0073@1e48220c — la décision qui spécifie la revue, que la règle 1 précise.
- ADR-0072@1a8b5c2d — la décision : le hook refuse ce qu'il ne sait pas juger ; la règle 2 en écrit la limite.
- B-0211@c3507a28 — le sujet des formes du shell déjà acceptées comme risques, abandonné ce jour par D-0111.
- B-0206@2ebfe7b8 — le cas limite, traité dans les bornes que pose la règle 2.
- B-0218@be06bed9 — le sujet des copies protégées de ce dépôt en retard sur leurs gabarits, qui recevra ce changement du skill.

## Où regarder

- [Votre décision en séance, D-0111](https://github.com/theodubus/memory/blob/3b11a9db7db693334ad308e47493fb754b89e940/memory/requests/D-0111-remarques-non-bloquantes.md) : la question posée et votre message entier.
- [Le skill de la revue, son gabarit](https://github.com/theodubus/memory/blob/3b11a9db7db693334ad308e47493fb754b89e940/engine/socle/templates/skills/socle-review/SKILL.md) : la section « Les constats », que la règle 1 remplace.
- [ADR-0072](https://github.com/theodubus/memory/blob/3b11a9db7db693334ad308e47493fb754b89e940/memory/decisions/ADR-0072-le-hook-de-l-agent-developpe-un-chemin-ecrit-comme.md) : ce que le hook juge aujourd'hui, et le refus de ce qu'il ne sait pas juger.

## Options

- Écrire les deux règles : effort faible, des textes et un test de la consigne du relecteur ; risque faible, un constat jugé exotique à tort pourrait manquer, mais une fois l'effet constaté le cas n'est plus « jamais reproduit » et rouvre un sujet ; réversible par une demande nouvelle.
- Ne pas les écrire : aucun effort ; la règle ne vit que dans ce dépôt (D-0111), les projets équipés gardent l'ancienne, et chaque revue y rouvre des sujets exotiques.

## Conséquences

Si vous validez : l'agent écrit les deux textes dans le moteur, avec une décision qui les fixe, et ses revues les appliquent aussitôt ; les projets les reçoivent à leur mise à jour, chess compris, et le prompt de mise à jour de chess le dit. La copie protégée du skill dans ce dépôt reste en retard jusqu'au rafraîchissement que porte B-0218. Si vous refusez : D-0111 continue de valoir dans ce dépôt seul. Sans réponse : rien ne change, et l'agent continue les autres sujets.

## Recommandation

Valider. Vérifié : appliquée aux sujets ouverts, la règle 1 en a fermé trois et réduit quatre, et en a gardé deux points qu'une lecture rapide aurait écartés à tort (D-0111) ; les formes que la règle 2 laisse hors du modèle sont celles que `protege.fichiers` attrape. Supposé : que le backlog né des revues et du hook converge sous ces règles ; on le verra au solde des prochaines semaines.

## Réponses possibles

- `valider` — l'agent écrit les deux règles dans le produit, au mot près.
- `refuser` — la règle reste celle de ce dépôt seul (D-0111).
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
