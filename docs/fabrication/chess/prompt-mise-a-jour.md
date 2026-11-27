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

4. Un correctif de la mémoire. Un commit dont le sujet suit le motif d'un correctif (« Correction : … ») et qui ne change que des fichiers de la mémoire n'est plus refusé par tests.regression : il s'avertit, « correctif qui ne touche que la mémoire : non jugé » (ta gêne 4). Un correctif qui touche aussi du code reste jugé comme avant. (2026-11-26-e)

5. Une commande citée dans « Pour toi ». La fin de tour ne prend plus le nom d'une commande du socle, prune-branches par exemple, cité entre accents graves sur une ligne qui dit supprimer une branche, pour une branche à chercher à l'origine (ta gêne 5). (2026-11-26-f)

### La mémoire et le backlog

6. L'empreinte d'index à citer. socle new et socle show --index font désormais citer l'empreinte de l'index du dernier commit, que le contrôle accepte toujours, sous les lignes de l'arbre ; l'en-tête le dit quand les deux diffèrent. Les entrées que tu crées dans un même tour, un lot et ses tâches par exemple, passent memoire.lectures même si un statut change avant le commit : ne recopie plus l'empreinte courante dans chacune (le point 1 de ton retour d'usage du 26 novembre). Si une empreinte que socle new a écrite est encore refusée, rapporte le refus mot pour mot. (2026-11-26-i)

7. Un besoin pour l'humain. Un besoin « pour : humain » sans tâche n'est plus listé parmi les besoins à découper en tâches, ni par socle state ni par socle roadmap : il ne paraît que sous ce qui revient à l'humain (le point 2 de ton retour d'usage du 26 novembre). Ne lui crée pas de tâche ; ferme-le sur ma parole, et fais d'une part que tu peux mener un autre besoin. (2026-11-26-j)

8. Le plafond des consignes. Le gabarit des garde-fous pose désormais 24 000 octets pour memory/directives.md, au lieu de 16 000 : une consigne ne se lève que sur ma parole, et le fichier ne fait que croître. La mise à jour garde tes garde-fous, donc ta valeur. Mesure memory/directives.md : s'il approche de ton plafond, pose-moi la demande de reprendre 24 000 octets dans .socle/guardrails.toml, qui assouplit un garde-fou ; sinon, n'y touche pas. (2026-11-26-k)

### Les skills et la section du socle d'AGENTS.md

9. Les raisons des règles, au guide. Les skills socle-batch, socle-resume, socle-request et socle-handoff, et la section du socle d'AGENTS.md, ne disent plus pourquoi une règle existe : ce qui la justifiait sans la dire (le pourquoi, ce qu'un hook refuse) est passé, mot pour mot, au guide, sous « Pourquoi ces règles », à la fin de sa Référence ; chaque règle reste dans son texte. L'installeur pose les skills et la section changés : n'y touche pas. Si une règle que tu suivais te semble manquer dans un skill ou dans AGENTS.md, rapporte-la mot pour mot. (2026-11-26-l)

10. Le plafond des skills. Le gabarit des garde-fous pose désormais 10 000 octets pour .claude/skills/*/SKILL.md, au lieu de 8 000 : les skills du socle, chargés en entier, n'avaient plus la place d'une règle de plus. La mise à jour garde tes garde-fous, donc ta valeur, et les skills qu'elle pose tiennent encore sous 8 000 octets : n'y touche pas. Si un skill approche de ton plafond, pose-moi la demande de reprendre 10 000 octets dans .socle/guardrails.toml, qui assouplit un garde-fou, en nommant la clé budgets.".claude/skills/*/SKILL.md".max_bytes. (2026-11-27-a)

### La feuille de route

11. Une seule forme. socle roadmap n'a plus qu'une forme, faite pour que je pilote le projet sur mon téléphone : « Maintenant », chaque lot en cours, puis les besoins qu'il mène et leurs tâches ; « Ensuite », tes jalons ouverts numérotés en [K/N], seul le premier déplié en ses besoins ; « Pour toi » ; « En réserve », les besoins d'aucun jalon, comptés. C'est un texte aligné, chaque titre suivi de son identifiant ; --format markdown le met dans un bloc de code : c'est celui que tu colles quand je demande la suite. Les formats compact et détaillé et l'option --by n'existent plus : retire --by de tout appel que le projet écrit. Ta consigne qui choisit le format court de la feuille de route n'a plus d'objet : dis-le-moi, je la garde ou je la lève (le point 3 de ton retour d'usage du 26 novembre). (2026-11-27-b)

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
