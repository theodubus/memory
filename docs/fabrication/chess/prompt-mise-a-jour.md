# Le prompt de la mise à jour du socle sur chess

À coller dans une session de chess, qui tourne sur un autre compte et ne lit
pas ce dépôt. Il met à jour le socle installé le 26 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-26.md`) vers la version
publiée, et dit à l'agent de chess ce qui change pour lui, comme Théo l'a
demandé.

Récrit le 26 novembre pour la mise à jour suivante (L-0046, posé par T-0204 sur D-0215) : celle du
26 novembre a suivi la version précédente de ce prompt, ses 37 points par
thème pour les notes d'après le 13 novembre (T-0186, commit `f24ebfec`),
et chess a reçu toutes les notes jusqu'à `2026-11-26-c`. Les points
d'ici ne couvrent que les notes d'après elle, dans
`engine/socle/CHANGES.md`. Chaque point dit la règle d'aujourd'hui et
finit par les identifiants des notes qu'il couvre ; d'une note qu'une plus
récente remplace, il ne garde que la règle qui reste. Chaque point vaut
dans une session cloud de chess, où le proxy refuse la suppression d'une
branche. Le prompt reste cumulatif : d'ici la mise à jour, chaque lot qui
change ce que chess reçoit ajoute sa note au point de son thème
(J-2026-11-13-L).

````text
Mets à jour le socle de ce dépôt depuis son dépôt public, sans ajouter ce dépôt à la session. Lis d'abord ce qui change, puis fais la mise à jour.

## Ce qui change depuis ta version

Ta version date du 26 novembre. L'installeur t'imprimera les notes de version que ta copie n'a pas, en entier celles qui te demandent quelque chose, puis le seul titre des autres. Ce qui suit les regroupe par thème et dit ce qu'elles changent pour chess ; chaque point finit par les identifiants des notes qu'il couvre. Le détail d'une note se lit dans .socle/engine/socle/CHANGES.md.

### La mise à jour et l'installeur

1. Le propriétaire du CODEOWNERS. Relancé sans --owner, l'installeur lit désormais le propriétaire sur la ligne de ton CODEOWNERS qui protège la politique (/.socle/), complète le fichier avec les lignes que son gabarit a en plus, et le dit (« CODEOWNERS : <propriétaire> … ») : la ligne « !! aucun propriétaire (--owner) » de ta gêne 2 ne doit plus paraître. Ne redonne pas --owner. Si elle paraît encore, rapporte-la mot pour mot. (2026-11-26-d)

2. Les notes d'une copie qui n'en avait pas. Quand la copie remplacée n'avait pas de notes de version, l'installeur n'imprime plus en entier que celles d'après le jour de son dernier commit, les autres par leur seul titre, sous une ligne qui les compte (ta gêne 7). Ta copie a désormais ses notes : ce cas ne te concerne plus, et tu ne reçois que les notes nouvelles. (2026-11-26-g)

3. La demande seule de la mise à jour. Tant que la mise à jour n'est pas commitée, les hooks git avant commit et avant push ne refusent plus que ce que le commit ou le push apporte : la demande seule se commite par git add sur son fichier, git commit et git push, sans le stash ni le --only de ta gêne 1 ; une ligne dit combien de constats déjà commités ils laissent à la CI. La migration du backlog ne met plus ses renommages dans l'index. Si un hook refuse encore la demande seule, ne le contourne pas : rapporte son refus mot pour mot. (2026-11-26-h)

### Les contrôles et la fin de tour

4. Un correctif de la mémoire ou de la documentation. Un commit dont le sujet suit le motif d'un correctif (« Correction : … ») et qui ne change que des fichiers de la mémoire, ou de la documentation (des textes Markdown hors du dossier du socle) avec ou sans la mémoire, n'est plus refusé par tests.regression : il s'avertit, « … non jugé », et le hook commit-msg n'annonce plus que la CI le refusera (ta gêne 4, et le §4 de ton retour du 26 novembre sur le coût du socle). Un correctif qui touche aussi un autre fichier reste jugé comme avant. (2026-11-26-e, 2026-11-27-e)

5. Une commande citée dans « Pour toi ». La fin de tour ne prend plus le nom d'une commande du socle, prune-branches par exemple, cité entre accents graves sur une ligne qui dit supprimer une branche, pour une branche à chercher à l'origine (ta gêne 5). (2026-11-26-f)

6. Les liens du dernier message. Un nom entre accents graves qui n'est pas un chemin du dépôt fait encore refuser la fin du tour, mais le refus donne désormais le chemin complet du seul fichier suivi que ce nom désigne, ou dit de l'écrire sans accents graves ; et le message qui ne corrige que les liens d'un récap refusé pour eux seuls n'a plus à redire le récap (le §3.1 du même retour, et ma question du récap répété deux fois). Si un récap te semble encore exigé deux fois, rapporte le refus mot pour mot. (2026-11-27-c)

### La mémoire et le backlog

7. L'empreinte d'index à citer. socle new et socle show --index font désormais citer l'empreinte de l'index du dernier commit, que le contrôle accepte toujours, sous les lignes de l'arbre ; l'en-tête le dit quand les deux diffèrent. Les entrées que tu crées dans un même tour, un lot et ses tâches par exemple, passent memoire.lectures même si un statut change avant le commit : ne recopie plus l'empreinte courante dans chacune (le point 1 de ton retour d'usage du 26 novembre). Si une empreinte que socle new a écrite est encore refusée, rapporte le refus mot pour mot. (2026-11-26-i)

8. Un besoin pour l'humain. Un besoin « pour : humain » sans tâche n'est plus listé parmi les besoins à découper en tâches, ni par socle state ni par socle roadmap : il ne paraît que sous ce qui revient à l'humain (le point 2 de ton retour d'usage du 26 novembre). Ne lui crée pas de tâche ; ferme-le sur ma parole, et fais d'une part que tu peux mener un autre besoin. (2026-11-26-j)

9. Le plafond des consignes. Le gabarit des garde-fous pose désormais 24 000 octets pour memory/directives.md, au lieu de 16 000 : une consigne ne se lève que sur ma parole, et le fichier ne fait que croître. La mise à jour garde tes garde-fous, donc ta valeur. Mesure memory/directives.md : s'il approche de ton plafond, pose-moi la demande de reprendre 24 000 octets dans .socle/guardrails.toml, qui assouplit un garde-fou ; sinon, n'y touche pas. (2026-11-26-k)

10. Une consigne que tu viens d'écrire. Une consigne née dans la plage jugée, absente de sa base, s'y cite sans empreinte ; une consigne d'avant la plage reste exigée avec la sienne, et son refus donne désormais l'empreinte à citer. Deux refus du hook en disent plus : `rm <chemin>` ne vaut que pour un fichier que git ne suit pas ; un texte qui cite un chemin protégé s'écrit par l'outil d'écriture de fichiers, pas par un script python dans un heredoc, que le hook refuse toujours (les §3.2, §3.5 et §3.8 du même retour). (2026-11-27-d)

11. Clore une tâche en un geste. socle close T-NNNN clôt désormais « fait » une entrée ouverte du backlog, de toute forme : il pose le statut, ajoute au champ ref la valeur « ce commit », qui désigne le commit qui la clôt, ou la référence que tu donnes par --ref, et la range parmi les closes, le déplacement dans l'index. Il ne coche rien : coche toi-même chaque critère tenu, puis clos ; il refuse, sans rien changer, l'entrée que les contrôles du backlog refuseraient close (une case vide, un besoin dont une tâche reste ouverte), avec leurs messages. Une entrée de journal n'est plus exigée pour servir de référence ; socle archive reste le geste de fin de lot qui range les consignes levées (le §2 de ton retour du 26 novembre sur le coût du socle). Si une clôture te coûte encore plus d'un geste, rapporte-moi lesquels. (2026-11-27-g)

### Les skills et la section du socle d'AGENTS.md

12. Les raisons des règles, au guide. Les skills socle-batch, socle-resume, socle-request et socle-handoff, et la section du socle d'AGENTS.md, ne disent plus pourquoi une règle existe : ce qui la justifiait sans la dire (le pourquoi, ce qu'un hook refuse) est passé, mot pour mot, au guide, sous « Pourquoi ces règles », à la fin de sa Référence ; chaque règle reste dans son texte. L'installeur pose les skills et la section changés : n'y touche pas. Si une règle que tu suivais te semble manquer dans un skill ou dans AGENTS.md, rapporte-la mot pour mot. (2026-11-26-l)

13. Le plafond des skills. Le gabarit des garde-fous pose désormais 10 000 octets pour .claude/skills/*/SKILL.md, au lieu de 8 000 : les skills du socle, chargés en entier, n'avaient plus la place d'une règle de plus. La mise à jour garde tes garde-fous, donc ta valeur, et les skills qu'elle pose tiennent encore sous 8 000 octets : n'y touche pas. Si un skill approche de ton plafond, pose-moi la demande de reprendre 10 000 octets dans .socle/guardrails.toml, qui assouplit un garde-fou, en nommant la clé budgets.".claude/skills/*/SKILL.md".max_bytes. (2026-11-27-a)

14. Les réveils de reprise gardés. Le skill socle-resume ne te fait plus armer les deux réveils au début de chaque tour qui agit, ni les retirer à sa fin (environ un appel sur dix de ta séance, le §5 de ton retour du 26 novembre sur le coût du socle) : un tour qui les trouve à la bonne heure n'appelle aucun outil de réveil, et ils ne se retirent qu'au rangement d'une session qui passe la main, ou quand je dis d'arrêter. Un réveil qui tire sans objet se vérifie et se dit en une ligne, sans reprendre le travail. Sans list_events, l'heure de la fenêtre que nomme rateLimitType se lit dans get_session, quand il la donne ; l'autre réveil reste à sa borne, sans s'y repousser à chaque tour. Si un tour te fait encore appeler un outil de réveil sans que leur heure ait changé, rapporte-le. (2026-11-27-h)

15. Ma parole, rangée selon sa nature. Une parole de moi qui vaut au-delà du tour ne devient plus toujours une consigne : une règle de travail (une préférence, une interdiction) va dans les consignes, une décision sur le projet en décision, consignée en séance, une attente en besoin au statut bloqué, qui dit ce qu'il attend (le §8 du même retour) ; le skill socle-request le détaille. Tes consignes du 26 novembre qui sont une décision ou une attente restent en vigueur : dis-moi lesquelles, et propose de les lever et de les ranger ainsi ; je réponds. (2026-11-27-i)

16. Une demande qui assouplit nomme ce qu'elle couvre. Le contrat que socle new request imprime le dit désormais en une ligne : une demande qui assouplit un garde-fou ou change une valeur attendue nomme la clé des garde-fous (budgets."<fichier>".max_bytes) ou la fonction de test qu'elle couvre, faute de quoi sa validation n'autorise rien. (2026-11-27-j)

### La feuille de route

17. Une seule forme. socle roadmap n'a plus qu'une forme, faite pour que je pilote le projet sur mon téléphone : « Maintenant », chaque lot en cours, puis les besoins qu'il mène et leurs tâches ; « Ensuite », tes jalons ouverts numérotés en [K/N], seul le premier déplié en ses besoins ; « Pour toi » ; « En réserve », les besoins d'aucun jalon, comptés. C'est un texte aligné, chaque titre suivi de son identifiant ; --format markdown le met dans un bloc de code : c'est celui que tu colles quand je demande la suite. Les formats compact et détaillé et l'option --by n'existent plus : retire --by de tout appel que le projet écrit. Ta consigne qui choisit le format court de la feuille de route n'a plus d'objet : dis-le-moi, je la garde ou je la lève (le point 3 de ton retour d'usage du 26 novembre). (2026-11-27-b)

18. La réserve triée à trois moments. Un besoin naît désormais rangé : socle new need "…" --milestone JA-NNNN l'ajoute à la fin de l'après d'un jalon ouvert, --reserve "<raison>" écrit sur sa ligne de métadonnées réserve : <raison> · trié : L-NNNN, le plus haut lot du backlog ; sans l'un ni l'autre, une ligne dit comment le ranger. Le contrôle memoire.reserve refuse, quand un jalon est ouvert, un besoin nouveau, ou sorti d'un jalon ouvert, qu'aucun jalon ouvert n'attend et qui n'a pas de raison ; un besoin d'avant ne se refuse pas. socle state nomme « à placer » les besoins de la réserve sans raison, ou sans tri depuis quinze lots clos, avec le trié à écrire, et la ligne « En réserve » de socle roadmap dit combien : à la clôture de ton prochain lot, range chacun de tes besoins d'après les jalons dans un jalon, ou écris sa raison et son trié ; récrire trié fait repartir le compte. Avant de clore un jalon, retrie toute la réserve : socle close JA-NNNN refuse sinon, tant qu'un besoin n'a pas sa raison et un trié au moins égal au plus haut lot de la base ; un besoin à abandonner, propose-le-moi par une demande que sa raison nomme, et il reste en réserve jusqu'à ma réponse. Si ranger, trier ou signaler un besoin te coûte un appel ou un refus de plus, rapporte-le mot pour mot. (2026-11-27-k)

### L'état et la passation

19. Une session en retard sur sa passation. Quand la tête locale est un ancêtre strict de la branche qui porte la passation en attente, socle state le dit désormais en tête, avec les fichiers d'instructions, de skills et de hooks qui changent entre les deux et la commande git diff qui les montre. Une fois placé sur la référence que la garde nomme, lis ce qui change avant tout autre travail (le §7 du même retour). (2026-11-27-f)

## La mise à jour

1. Si le clone est superficiel (git rev-parse --is-shallow-repository répond true), complète son historique : git fetch --unshallow.
2. Clone le socle à jour, après avoir supprimé un /tmp/socle resté d'avant :
   git clone --depth 1 https://github.com/theodubus/socle /tmp/socle
3. Sur une branche de travail neuve depuis main, à la racine du dépôt :
   PYTHONPATH=/tmp/socle python3 -m socle install --target .
   Ne redonne ni l'adaptateur ni --owner : ceux de chess sont en place, et ils sont gardés.
4. Lis les notes de version que l'installeur imprime en entier, et fais ce que chacune demande. Puis lis le reste de ce qu'il dit, et vérifie :
   - sa ligne sur CODEOWNERS (point 1) ;
   - python3 .socle/socle state : sa taille (python3 .socle/socle state | wc -c, sous 9 500), et s'il finit par une ligne « !! coupé » ;
   - rien de changé dans ta politique ni dans ton adaptateur ; ta liste [adoption.tolerated] inchangée.
5. Suis les étapes « Et maintenant » de l'installeur, dans son ordre : la demande qui cite chaque fichier protégé changé avec son empreinte, poussée seule, puis les fichiers commités et poussés, pour que je les lise dans la pull request avant de répondre. Donne-moi son lien, et attends ma réponse.
6. La porte, avant de me demander de fusionner : python3 .socle/socle verify --fast --redo, python3 .socle/socle ci et tools/verify.sh --rapide passent. Donne-moi les durées.
7. Ouvre la pull request, et dis-moi ce qui me revient. Ne la fusionne pas : je la fusionne après avoir lu ton compte rendu.

Rends-moi compte, court : les identifiants des notes de version qu'il t'a données en entier, et ce que tu en as fait ; sa ligne sur CODEOWNERS, mot pour mot ; la taille de l'état avant et après, et s'il est coupé ; les fichiers protégés changés ; chaque refus du hook pendant la mise à jour, avec sa commande ; les lignes « CI » et « branche » de l'état après le push, et si l'état me donne une action ; tout ce qui t'a gêné.
````
