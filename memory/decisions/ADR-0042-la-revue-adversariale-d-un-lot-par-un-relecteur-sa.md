<!-- socle: couche=decisions zone=publique -->
# ADR-0042 — La revue adversariale d'un lot, par un relecteur sans contexte, avant sa livraison

> statut : proposée · date : 2026-11-02 · source : D-0070@51d47c63, B-0124@fe238ccb · lu : decisions@c64b48fd

## Contexte

Les contrôles du socle jugent la forme du travail d'un agent : sa mémoire,
ses tests, ses refus, ses liens. Aucun ne juge le fond : un défaut de
logique, un cas qu'aucun test n'exerce, un code qui contredit une
spécification passent tous les contrôles. BMAD faisait relire le travail
par des relecteurs indépendants, dont un relecteur adversarial ; son
retrait (D-0051@cea58730) a rangé ce principe dans la répartition entre
agents, qui viendra tard. B-0124@fe238ccb l'en sort. Théo a validé les
hypothèses de ses questions de cadrage (D-0070@51d47c63) : elles
s'appliquent ici, « supposées » jusqu'à la mesure.

## Décision

**Quand.** Avant le push qui livre un lot qui change du code, une
spécification ou un test ; jamais pour un lot qui ne touche que la
mémoire. Une passe par lot, sans seconde revue après les corrections.

**Le dossier du relecteur, par le moteur.** `socle review` imprime tout ce
que le relecteur reçoit, et rien d'autre :
- la consigne : prendre le lot en défaut (ce qui casse, ce qu'aucun test ne
  prouve, ce qui contredit la mémoire ou une spécification), et rendre des
  constats numérotés, chacun avec son fichier et sa ligne, ce qui casse et
  comment le vérifier, ou « aucun constat » ;
- le diff du lot : ce que la branche n'a pas encore poussé, ou, sans
  branche distante, ce qui sépare la branche de la branche par défaut,
  tronqué au-delà d'un plafond, la troncature dite ;
- les sujets que le lot ferme, avec leur « Fait quand », et les décisions
  et demandes qu'ils citent, en entier.
Le moteur ne connaît aucun agent : il ne lance pas le relecteur.

**La procédure, côté agent.** Un skill du socle, `socle-review`, posé par
l'installeur et protégé comme les deux autres. Sous Claude Code, l'agent
lance un sous-agent, du modèle de la session, dont le seul message est la
sortie de `socle review` : il n'a ni la conversation, ni la mémoire, ni
l'état. Un agent sans sous-agents saute la revue, et son récap le dit.
Aucun constat ne bloque seul : l'agent corrige chaque constat fondé, et
répond aux autres en une ligne. Le récap le dit en une ligne : combien de
constats, combien corrigés, et pourquoi les autres sont écartés. Rien
n'est posté sur GitHub ; l'humain lit le récap, pas la revue.

**D'abord une option, mesurée.** Les instructions que l'installeur pose
dans un projet ne l'exigent pas encore. Ce dépôt l'applique à ses
propres lots, une règle de sa partie propre de `AGENTS.md`. Le banc la
mesure sur des défauts connus que les contrôles ne voient pas. Si elle en
trouve, une demande à Théo en fait la règle par défaut des instructions ;
sinon, elle devient une option des questions de départ.

## Conséquences

Ce que ça apporte : un jugement sur le fond, par un lecteur qui ne partage
pas les angles morts de l'agent qui a écrit le lot, sans agent maître.

Ce que ça coûte :
- à chaque lot de code, une relecture du diff entier par un second modèle,
  en jetons et en minutes ;
- des constats faux, que l'agent doit écarter, et dont le récap porte la
  raison ;
- un skill de plus à poser et à protéger ; une mise à jour le rafraîchit,
  et l'humain l'approuve comme les autres fichiers protégés.

Ce qui reste supposé, à mesurer au banc : que la revue trouve des défauts
que les contrôles ratent, à un coût qui le vaut.

Pour défaire : retirer le skill et la commande, et la règle de la partie
propre de ce dépôt ; aucune donnée n'en dépend.
