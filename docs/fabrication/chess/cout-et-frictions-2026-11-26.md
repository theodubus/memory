# Usage du socle 0.2.0 sur chess, 26 novembre 2026 : le coût en appels, les frictions, des propositions

Le troisième retour de la session de chess (B-0367), sur son usage du
socle du 12 au 26 novembre, recopié par Théo dans la session du socle au
premier message après « reprends », tel quel. Sa relecture critique et
l'arbitrage de Théo (D-0217) viennent après B-0364 et B-0365.

```text
Retour d'usage du socle 0.2.0 sur le dépôt chess : le coût mesuré en appels, les frictions, des propositions

CONTEXTE
Le dépôt chess (un moteur d'échecs en Rust et son interface) emploie le socle depuis le 12 nov. 2026, en version 0.2.0 depuis le 26 nov. Un agent Claude Code y travaille en session cloud ; l'humain relit par intermittence.
Ce retour complète les deux précédents, déjà transmis, et n'en répète rien. Ils portaient sur les empreintes de lecture qui périment, le besoin « pour : humain » listé à découper, le format de la feuille de route, et deux principes : un refus offre une voie légitime moins chère que son contournement ; une preuve produite par l'agent contrôlé ne prouve que la forme.
Sources :
- le journal local des hooks, du 12 au 26 nov. : 4 905 déclenchements, 56 refus ;
- socle consumption sur la séance du 26 nov. ;
- un décompte des appels d'outil dans la transcription de cette séance ;
- les incidents, avec leur reproduction ;
- la reprise par une session programmée, le 26 nov. au soir : le reflog de son dépôt, l'état imprimé à son démarrage, ses refus, et une session sonde.

DEUX PRINCIPES DE PLUS
P3. Le coût fixe d'une tâche doit être à la mesure de la tâche. Ce que du code déterministe peut faire (statuts, rangement, entrée de journal dérivée du commit) ne doit pas coûter d'appels à l'agent.
P4. Un contrôle qui juge une commande arbitraire ne peut pas être exact : savoir si un programme écrit un fichier est indécidable en général. Il choisit entre refuser à tort et laisser passer. Pour un fichier protégé, refuser à tort est le bon choix à deux conditions : la voie légitime est bon marché, et un contrôle en aval (protege.fichiers, au commit et en CI) rattrape ce qui passe.

1. CE QUE COÛTE LE SOCLE : LA BONNE MESURE EST L'APPEL, PAS L'OCTET
socle consumption dit que les sorties du socle pèsent 3,5 % du contexte de la conversation principale, 4,2 % avec la section d'instructions. Ce chiffre trompe : il compte les octets injectés, pas les appels que le socle fait faire.
Or, dans une conversation longue, chaque appel relit tout le contexte. Le 26 nov., la médiane était de 582 k jetons relus par appel. Un appel de plus coûte donc à peu près autant que n'importe quel autre, et le coût que cause le socle est sa part des appels.
Décompte dans la transcription, du compactage à la passation : un lot de deux tâches (un texte de workflow, le découpage du balayage de mutation) et des échanges avec l'humain, soit 118 appels d'outil.
- 36 (30,5 %) sont des appels shell qui lancent une commande du socle, seule ou avec du vrai travail (commit, push).
- 12 (10,2 %) servent aux réveils de reprise et aux tâches programmées. Aucune limite n'a coupé la séance : ces réveils n'ont servi à rien ce jour-là.
- Environ 40 % est une borne haute : une partie de ces appels est du travail utile (le dossier de revue, une décision consignée, la feuille de route demandée). Le tri appel par appel n'est pas fait ; je ne donne pas de borne basse.
- La revue adversariale d'un lot (un sous-agent, 43 appels) a pesé 1,13 M pondérés sur 15,99 M pour la journée, soit 7 %.
Corollaire : la cérémonie coûte d'autant plus que la conversation est longue. La règle des 150 000 jetons de socle-batch et la réduction des appels de cérémonie sont deux leviers sur le même coût.
1.1. Que socle consumption compte les appels d'outil par nature : commande du socle (en séparant les contrôles et le rangement du travail utile), réveil de reprise, correction après un refus, et le reste. Mon décompte tient en quarante lignes sur la transcription : chaque appel d'outil classé par son nom et, pour le shell, selon que sa commande appelle le socle. C'est grossier, parce qu'un appel mixte compte entier. Sans ce compte, la cérémonie reste invisible, et aucune des propositions suivantes ne peut se juger sur pièces.

2. LA CÉRÉMONIE D'UNE PETITE TÂCHE
Exemple réel : corriger deux lignes de texte dans un workflow. Le travail tient en deux éditions. Autour :
- socle new task, puis remplir l'entrée ;
- une entrée de journal : une tâche close exige une référence, et le commit qui la clôt n'existe pas encore, donc seule une entrée de journal peut servir ;
- passer la tâche à « fait » et cocher ses cases ;
- socle check, refusé : l'entrée close doit d'abord être rangée par socle archive, et les empreintes de lecture sont périmées (retour déjà transmis). Le premier commit est refusé pour les mêmes raisons ;
- socle archive, socle check, commit.
Environ huit gestes de mémoire pour deux lignes de travail. Chacun coûte un appel, donc une relecture du contexte. Propositions :
2.1. Une tâche close dans le commit qui la fait peut prendre ce commit pour référence, par exemple « ref : ce commit », que le contrôle résout par l'historique du fichier (le commit qui a passé le statut à « fait »). L'entrée de journal devient facultative quand le commit dit tout.
2.2. Une commande de clôture (socle close T-NNNN) pose le statut et la référence, range l'entrée et rafraîchit ce qui doit l'être. Elle ne coche pas les cases : cocher reste un geste délibéré de l'agent, qui atteste un critère.
2.3. À défaut, le hook avant commit range lui-même une entrée close au lieu de refuser le commit : ce refus n'apprend rien que la commande ne pourrait faire. Revu le 26 nov. au soir : un commit de plus refusé pour cette seule raison, sur une tâche et son lot clos ensemble.
2.4. À examiner : un seuil sous lequel une tâche n'a pas besoin d'un lot à elle seule. Un lot d'une seule tâche ajoute une entrée et une revue.

3. LES REFUS DES HOOKS, CLASSÉS (56 du 12 au 26 nov.)
3.1. Liens du dernier message (Stop:liens), 20 refus, le premier poste. Un nom entre accents graves qui n'est pas un chemin du dépôt : un nom de fichier nu (search.rs pour engine/src/search.rs), un nom de workflow nu, un nom de commande, un fichier ignoré par git.
Ce sont de vraies fautes : le client en fait un lien qui mène à une page introuvable. Mais le contrôle tombe après l'envoi. Chaque refus coûte un tour de plus (plusieurs appels au contexte plein) et un second message, que l'humain lit après le message fautif ; il s'en est plaint (« Pourquoi tu répètes 2 fois le récap de fin ? »). Propositions :
- le message de refus donne la correction exacte quand elle est mécanique : le chemin complet quand le nom nu désigne un seul fichier suivi, « à écrire sans accents graves » sinon. La correction tient alors en une ligne, sans redire le récap ;
- la section d'instructions donne la règle en une phrase positive, à l'endroit où l'agent écrit : entre accents graves, seulement un chemin complet et suivi par git ; un nom de commande ou un nom nu s'écrit sans ;
- une vérification que l'agent lancerait sur son brouillon avant de conclure coûterait un appel par message : à n'envisager que si le compte du point 1.1 montre que les deux premières ne suffisent pas.
3.2. Écriture d'un fichier protégé supposée dans une commande shell, 2 refus le 26 nov. : un heredoc Python dont une chaîne de texte, le corps d'une entrée de journal, citait le chemin .socle/socle. Rien n'écrivait ce fichier.
La voie légitime proposée, écrire le script avec l'outil d'écriture puis l'exécuter, est bon marché. Mais elle contourne aussi le contrôle : le hook ne lit pas un script exécuté depuis un fichier, qui pourrait écrire un fichier protégé. La protection réelle est donc protege.fichiers, au commit et en CI (P4).
Proposition : ne refuser que ce qui ressemble à une écriture du chemin (redirection, tee, sed -i, cp ou mv vers lui, open en écriture sur le chemin littéral), laisser passer une simple mention, et garder le contrôle en aval tel quel.
3.3. Opérations jugées irréversibles ou externes, 3 refus : deux pushes sur la branche main d'un dépôt jetable fabriqué dans un dossier temporaire pour éprouver un script, et un reset --hard précédé d'un stash.
Les deux pushes sont des faux positifs : rien ne sort de la machine. Proposition : juger la cible (le dépôt où la commande s'exécute, l'option -C, l'URL du distant). Un push vers un distant local, dans un dossier temporaire, n'est pas externe.
3.4. Installeur visé sur une cible que le hook ne sait pas résoudre, 3 refus.
- Deux visaient une variable : la voie légitime (écrire le chemin en toutes lettres) est bon marché, c'est acceptable selon P4.
- Le troisième visait un chemin écrit en toutes lettres sous le dossier temporaire de la session : à relire, je n'ai pas la commande entière.
3.5. Remise en état d'un fichier protégé, en cascade : une écriture shell dans un fichier de réponse humaine (vraie faute, bien attrapée), puis deux remises en état refusées (un préfixe d'environnement, un fichier non suivi). Une faute qui coûte trois refus suggère que la voie acceptée de remise en état n'est pas assez lisible dans le message de refus.
3.6. Vraies fautes, refus utiles, à garder tels quels :
- un SHA complété de tête ;
- deux références à des entrées pas encore créées ;
- une demande qui citait un SHA sans le décrire ;
- des budgets de mémoire dépassés (6 refus, avant commit ou avant push) ;
- un récap sans ses deux lignes ;
- des liens de demande manquants (3) ;
- un fichier protégé modifié.
3.7. Non classés : 3 refus de hooks.filtre avant commit.
3.8. Une consigne citée sans son empreinte dans le commit même qui la crée, 2 refus le 26 nov. au soir (memoire.lectures). L'agent venait d'écrire la consigne : il n'avait rien à prouver d'avoir lu. Le message de refus dit de lancer socle show pour lire l'empreinte, sans la donner, et il tombe sur chaque mention, titres compris. Propositions : comme en 3.1, le message donne l'empreinte exacte à recopier ; ou le contrôle accepte sans empreinte une entrée que le même commit crée.

4. UN TITRE DE COMMIT PRIS POUR UN CORRECTIF
tests.regression traite comme un correctif, avec un test qui échoue sur le parent, tout commit dont le sujet commence par fix, corrige, correctif ou correction. En français, « Correction : … » se dit aussi d'une correction de texte ou de mémoire.
Incident : un commit de documentation titré ainsi a dû être déplacé sur une autre branche.
Proposition : ne retenir que le préfixe conventionnel fix: et le trailer Corrige:, ou ignorer un commit qui ne touche aucun code.

5. LES RÉVEILS DE REPRISE (skill socle-resume)
Coût mesuré : 12 appels sur 118, soit 10,2 % des appels de la séance, donc environ autant de son coût, pour un filet qui n'a pas servi ce jour-là. Par tour qui agit : armer deux réveils, les récrire au lancement d'un sous-agent, les retirer à la fin.
Sans l'outil list_events, absent de cette session, chaque réveil s'arme à la borne (maintenant plus cinq heures et cinq minutes) et n'est plus qu'un filet tardif. Pourtant get_session rend l'heure de remise à zéro de la fenêtre (rate_limit_info.resetsAt) : le skill pourrait la lire là. Vérifié le 26 nov. au soir : get_session ne rend que la fenêtre que nomme rateLimitType, ce jour-là celle de cinq heures, et rien pour la semaine ; le réveil de la semaine reste à la borne.
Observation : la vérification au réveil (le tour d'avant a-t-il fini sur une limite ? l'humain a-t-il écrit depuis ?) suffit déjà à empêcher une reprise à tort. Retirer les réveils à chaque fin de tour pour les réarmer au suivant double donc les appels, pour éviter des réveils que la vérification neutralise de toute façon.
Propositions :
- garder les réveils d'un tour à l'autre, et ne les déplacer que quand leur heure change ; un réveil sans objet coûte une vérification de deux ou trois appels, plus rarement que quatre appels à chaque tour ;
- n'armer que pour un tour qui s'annonce long (un sous-agent, un lot), un tour court étant rarement coupé ;
- lire l'heure de remise à zéro dans get_session quand list_events manque.

6. LA REVUE ÉCRIT DANS L'ARBRE AVANT SON RETOUR
socle review écrit la passe dans l'entrée du lot dès qu'il produit le dossier. En session cloud, le hook de fin de tour de l'environnement exige alors de commiter et de pousser ce changement pendant que le relecteur travaille. Le lot part avant sa revue, et la note « lot déjà poussé » s'applique à tort.
Même hook, autre cas, le 26 nov. au soir : une vérification complète de plusieurs minutes, lancée en arrière-plan sur un changement pas encore commité. Le tour qui l'attend se termine, et le hook exige de commiter et de pousser ce que rien n'a encore vérifié. Les procédures du socle qui attendent un résultat devraient supposer ce hook présent en session cloud.
Proposition : n'écrire la passe qu'au retour, par une commande qui consigne en même temps les bloquants et ce que la passe ouvre, ou garder la passe hors de l'arbre jusque-là.

7. UNE SESSION PROGRAMMÉE DÉMARRE SUR UNE COPIE PÉRIMÉE, ET RIEN NE LE DIT
Incident du 26 nov. au soir. La passation désignait c2c9ab9, la tête de la branche de travail. La session créée pour la reprendre a démarré sur 4f309d7, trois heures plus vieille. Le reflog de son dépôt le montre : un clone daté de 16 h 05, l'heure de démarrage de la session d'avant ; puis, à 19 h 10, la mise en place s'est placée sur c2c9ab9 et a aussitôt basculé sur la branche locale du même nom, restée à 4f309d7.
Conséquence : le contexte de la session a reçu les instructions, les skills et les hooks de 4f309d7. Ce jour-là, une ligne d'écart, sans effet. Mais le lot précédent venait de déplacer les instructions (CLAUDE.md réduit à un import d'AGENTS.md), et le critère qu'il laissait à la session suivante, « une session neuve reçoit les instructions par l'import », ne pouvait pas s'y constater. Il a fallu une session sonde, créée avec une branche de sortie neuve, qui a démarré, elle, sur la bonne tête.
Ni la garde ni l'état ne l'ont signalé : socle state imprimait « commit : 4f309d71 » et, plus bas, « passation : en attente sur origin/claude/agents-md » ; handoff check disait « se placer sur origin/claude/agents-md (c2c9ab925e) », sans dire que le contexte déjà chargé venait d'ailleurs.
La cause est dans la plateforme : un conteneur repris d'une session précédente, et une branche locale qu'on n'avance pas. Le fait est lu au reflog ; le mécanisme exact est supposé. Le socle ne peut pas corriger la cause, mais il peut la voir.
Propositions :
7.1. Au démarrage, quand une passation attend et que la tête locale est un ancêtre strict de sa référence, socle state le dit en tête : la tête chargée, celle de la passation, et les fichiers d'instructions, de skills et de hooks qui changent entre les deux.
7.2. Le skill de passation demande alors à la session neuve de lire ce diff avant tout travail : ce qu'elle a reçu en contexte n'est pas ce qui est dans l'arbre.
7.3. À examiner : avancer la branche locale dans le hook de démarrage, quand elle est un ancêtre strict de son distant et que l'arbre est propre. Cela ne corrige les instructions que si Claude Code les lit après ce hook, ce qui reste à vérifier, et cela fait écrire un hook qui jusqu'ici ne fait que lire.
7.4. Hors du socle : signaler à la plateforme qu'une session créée sur une branche qui existe déjà dans le conteneur démarre sur sa copie locale périmée.

8. OÙ RANGER LA PAROLE DE L'HUMAIN
La section d'instructions dit : une consigne de l'humain qui vaut au-delà du tour (une règle, une préférence, une interdiction) s'écrit dans les consignes. Appliquée à la lettre le 26 nov., elle a rangé en consignes deux paroles qui n'en étaient pas. « On ne fera ce projet que dans Claude Code » est une décision de projet. « Ne reprends pas les travaux avant que je dise le socle prêt » est un état d'attente. Le 23 nov., la même attente, avant la mise à jour du socle, avait été rangée en décision au journal et en besoin bloqué du backlog : l'état le calcule, et l'attente se lève en fermant l'entrée.
Proposition : la règle distingue trois natures. Une règle de travail de l'agent va dans les consignes. Une décision de projet va en décision, avec la parole citée. Une attente qui se lèvera sur un signal de l'humain va dans un besoin bloqué que l'état affiche ; s'il ne l'affiche pas assez haut, c'est l'état qu'il faut corriger, pas la nature de l'entrée.

9. CE QUE JE NE PROPOSE PAS
- Affaiblir protege.fichiers, le refus d'un SHA ou d'une référence inventés, les budgets de mémoire, ou l'exigence d'un récap à deux lignes : ce sont les refus qui ont attrapé de vraies fautes.
- Supprimer la revue adversariale : sur le seul lot observé, elle n'a trouvé aucun bloquant, ce qui ne dit rien de sa valeur sur un échantillon d'un.

CRITÈRE DE RÉUSSITE PROPOSÉ
Sur les quelques lots qui suivront la correction, mesurés par le compte du point 1.1, à lot comparable :
(a) la part des appels de cérémonie (contrôles, rangement, réveils) au moins divisée par deux ;
(b) les refus à tort au moins divisés par deux ;
(c) les gestes de mémoire d'une tâche triviale ramenés de huit à deux ou trois ;
(d) une session programmée qui démarre en retard sur sa passation le dit dans le premier état qu'elle imprime.
```
