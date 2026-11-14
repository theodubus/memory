# Le prompt de la mise à jour du socle sur chess

À coller dans une session de chess, qui tourne sur un autre compte et ne lit
pas ce dépôt. Il met à jour le socle installé le 13 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-13.md`) vers la version qui
borne la sortie du démarrage (B-0010), fait développer au hook les chemins
qu'une commande shell écrit (B-0171) et donne les notes de version à la mise
à jour (B-0151), et dit à l'agent de chess ce qui
change pour lui, comme Théo l'a demandé. Il est cumulatif : chess n'est mis à
jour qu'une fois l'ensemble à finir avant les nouvelles fonctions fait, et
chaque lot qui change ce que chess reçoit le complète d'ici là
(J-2026-11-13-L).

````text
Mets à jour le socle de ce dépôt depuis son dépôt public, sans ajouter ce dépôt à la session. Lis d'abord ce qui change, puis fais la mise à jour.

## Ce qui change depuis ta version

1. Le démarrage te parvient enfin entier. Jusqu'ici, la sortie du hook de démarrage dépassait 10 000 caractères, et Claude Code ne t'en remettait qu'un aperçu de 2 000 : le chantier actif et les faits ne t'arrivaient presque jamais. Elle est désormais bornée sous [startup] max_bytes des garde-fous (9 500 octets) :
   - en tête, ce qui demande d'agir (ce qui revient à l'humain, les demandes, ce qu'il a écrit lui-même, les lignes du hook) ; puis l'état ; puis le chantier actif en entier, les faits par leur titre et les dix dernières décisions ;
   - chaque partie a sa part de la borne ; une partie qui dépasse perd des lignes entières, et une dernière ligne « !! coupé » dit ce qui manque et où le lire : lis-le aussitôt ;
   - python3 .socle/socle state --short imprime l'état dérivé entier, sans borne ; un fait ou une décision en entier : python3 .socle/socle show <ID> ; l'index des décisions : python3 .socle/socle show --index decisions.
2. Le budget du chantier actif passe à 3 700 octets (public et privé ensemble), pour qu'il tienne dans sa part. Si tes garde-fous gardent un budget plus haut, l'installeur le signale (« !! le budget de memory/active.md … ») avec la valeur qui tient : baisse-le à cette valeur (durcir est libre), puis raccourcis memory/active.md si le contrôle memoire.budgets le demande, ce qui en sort allant au journal.
3. Le hook de l'agent juge un chemin qu'une commande shell écrit tel que le shell le développerait : variables, motifs (*, ?), accolades, ~, cd et pushd suivis, chemins relatifs depuis ton dossier courant. Un chemin qu'il ne sait pas développer (une variable qu'il ne connaît pas, $(…), un cd vers un tel chemin) est refusé s'il peut tomber dans le projet. Si un refus te gêne : écris le chemin en toutes lettres, ou affecte la variable plus tôt dans la même commande (F=/tmp/x; echo y > "$F"). Les faux refus connus : $(mktemp -d) ou $(git rev-parse --show-toplevel) tenus dans une variable ou en cible de cd, une boucle for sur une liste écrite. Le hook reste une première barrière : la garantie est le contrôle protege.fichiers, à la fin du tour, au commit et dans la CI.
4. La revue adversariale juge un lot contre ses sujets. Le dossier de python3 .socle/socle review donne au relecteur le « Fait quand » de chaque sujet que le lot touche, même ouvert, et les titres de ceux qu'il ouvre ; il lui fait classer chaque constat : bloquant (un critère coché ou une décision contredits, une régression, une perte de données, un contournement d'un garde-fou dans son modèle de menace) ou pour le backlog (le reste). Seuls les bloquants se corrigent dans le lot ; les autres vont au backlog. Une seconde revue seulement si la correction des bloquants est lourde, et sur elle seule : python3 .socle/socle review --since <commit relu>. En conséquence, un sujet qui pose ou change un garde-fou écrit avant son code son modèle de menace, dans une section « ## Modèle de menace » (ce qu'il arrête, ce qu'il laisse passer), et un sujet dont la conception n'est pas tranchée, sa spécification. Le skill socle-review, une copie protégée, change : il est dans la demande de l'installeur.
5. Une réponse que je donne dans la conversation se consigne aussitôt, dans l'arbre (python3 .socle/socle answer D-NNNN valider --relayed …) : l'état lit l'arbre, et la lit répondue avant son commit ; je ne la vois plus « en attente ». Elle se commite et se pousse avec le changement qu'elle autorise (une valeur attendue, une clé des garde-fous, un fichier protégé), dans le même push, jamais avant : la CI d'un push ne compte que les validations de sa plage. Seul un fichier protégé peut la précéder, poussé sous la demande en attente, comme ceux de la mise à jour : ma réponse part ensuite seule, sans dommage. Un contrôle nouveau, demandes.reponse-seule, t'en avertit quand la réponse partirait seule, sans le test, le fichier de cas, la clé des garde-fous ou le fichier protégé qu'elle nomme : dans verify --fast, au commit et avant que le push parte, sur la sortie du hook. C'est un avertissement, pas un refus. Le skill socle-request le dit ; c'est une copie protégée, elle est dans la demande de l'installeur.
6. Entre l'installation et le push de sa demande, la fin de tour dit la mise à jour en une ligne, et non plus une ligne par fichier (ta gêne 3) : « une mise à jour du socle attend sa demande : la poser », avec le nombre de fichiers et la commande qui les liste avec leurs empreintes (python3 .socle/socle check --stage agent --only protege.fichiers). Les fichiers que la mise à jour a posés n'ont plus de commande de remise : ne les remets pas, pose la demande. Un fichier protégé qu'elle n'a pas posé tel qu'il est, changé avant ou après le passage de l'installeur, garde sa ligne et sa commande de remise. Le verrou du moteur, qui change, nomme désormais sous [installed] les fichiers protégés que l'installeur a posés hors du moteur, avec leur empreinte : c'est ainsi que la fin de tour les reconnaît.
7. L'installeur donne désormais les notes de version du socle : à chaque mise à jour qui recopie le moteur, il imprime, entre ce qu'il a posé et l'audit, les entrées que ta copie du moteur n'avait pas, chacune avec ce que tu dois faire (« À faire : »), et le message de commit qu'il propose nomme leurs identifiants dans un second paragraphe. Elles sont dans .socle/engine/socle/CHANGES.md. Ta copie n'en a pas : il te les donne toutes. Celles datées d'avant le 13 novembre décrivent ce que tu as déjà ; les autres reprennent les points ci-dessus. Garde ce second paragraphe dans le commit de la mise à jour.
8. Un lot se garde désormais au backlog, et non plus dans la seule prose du chantier actif : un sujet marqué forme : lot, dont après nomme les sujets que tu mènes ensemble (ceux qui touchent les mêmes fichiers, le même garde-fou ou les mêmes tests, qu'une seule revue juge ensemble) et le lot d'avant. L'état montre le prochain lot à côté du prochain jalon, avec ce qui en reste et où en est chacun (prêt, en cours, attend, sans réponse pour une demande). Un lot n'est jamais un sujet prêt, et il se clôt quand ses sujets le sont : memoire.ordre refuse de le clore avant.

Pas encore faits, inutile de les signaler de nouveau : l'installeur muet sur une adoption déjà vide et le diff de politique réaffiché (tes gênes 1 et 5), le coût de la relecture à froid (7), la reprise sans list_events (8).

Une règle à connaître, que le socle rappelle sans l'imposer (le point 5) : poussée seule, ma réponse ne couvre pas le changement qui la suit ; le push de ce changement reste refusé, et ma réponse se consigne alors une seconde fois.

## La mise à jour

1. Si le clone est superficiel (git rev-parse --is-shallow-repository répond true), complète son historique : git fetch --unshallow.
2. Clone le socle à jour, après avoir supprimé un /tmp/socle resté d'avant :
   git clone --depth 1 https://github.com/theodubus/socle /tmp/socle
3. Sur une branche de travail neuve depuis main, à la racine du dépôt :
   PYTHONPATH=/tmp/socle python3 -m socle install --target .
   Ne redonne pas l'adaptateur : celui de chess est en place, et il est gardé.
4. Lis les notes de version que l'installeur imprime, et fais ce que chacune demande. Puis lis le reste de ce qu'il dit, et vérifie :
   - le budget de memory/active.md et [startup] max_bytes : ce qu'il en dit, et ce que tu as changé ;
   - python3 .socle/socle state : sa taille (python3 .socle/socle state | wc -c, sous 9 500), et s'il finit par une ligne « !! coupé » ;
   - rien de changé dans ta politique ni dans ton adaptateur ; ta liste [adoption.tolerated] inchangée.
5. Suis les étapes « Et maintenant » de l'installeur, dans son ordre : la demande qui cite chaque fichier protégé changé avec son empreinte, poussée seule, puis les fichiers commités et poussés, pour que je les lise dans la pull request avant de répondre. Donne-moi son lien, et attends ma réponse.
6. La porte, avant de me demander de fusionner : python3 .socle/socle verify --fast --redo, python3 .socle/socle ci et tools/verify.sh --rapide passent. Donne-moi les durées.
7. Ouvre la pull request, et dis-moi ce qui me revient.

Rends-moi compte, court : les identifiants des notes de version qu'il t'a données, et ce que tu en as fait ; ce que l'installeur a dit, mot pour mot, du budget et de la borne ; la taille de l'état avant et après, et s'il est coupé ; les fichiers protégés changés ; chaque refus du hook pendant la mise à jour, avec sa commande ; tout ce qui t'a gêné.
````
