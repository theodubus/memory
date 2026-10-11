# Le parcours de l'utilisateur : relevé et propositions

B-0034, à la demande de Théo : avant d'écrire la documentation du socle
(B-0035), mesurer ce que l'humain tape, lit et décide, de l'installation à
l'usage courant, et proposer de quoi le simplifier. Relevé le 2026-10-11, en
jouant le parcours sur un projet Python neuf (sous pytest, avec un document
de cadrage), puis une mise à jour du socle, l'ajout d'une mémoire privée et
un commit fait à la main.

## Le parcours, étape par étape

| # | Étape | Ce que l'humain tape | Ce qu'il lit | Ce qu'il doit décider ou deviner | Constat |
| --- | --- | --- | --- | --- | --- |
| 1 | Obtenir le socle | `git clone https://github.com/theodubus/memory /tmp/socle` | rien | où le mettre | simple |
| 2 | Installer | `PYTHONPATH=/tmp/socle/moteur python3 -m socle install --target . --adapter auto --owner @moi` | 56 lignes : 12 de journal, puis l'audit contrôle par contrôle | l'adaptateur, le propriétaire, et s'il faut `--adoption`, `--private`, `--language` | **finit en échec** (code 1) dès que le projet a du code : `mutation.couverture` |
| 3 | Débloquer | éditer `.socle/guardrails.toml` à la main | « lui mesurer un plafond, depuis un arbre vert » | comment mesurer, et quelle valeur écrire | nulle part expliqué ; le seul chemin trouvé est d'écrire `max = 0` |
| 4 | Initialiser | `python3 .socle/socle init --cadrage cadrage.md --depot` | 27 lignes, écrites pour l'agent | qui fait la suite, et quand | la sortie parle à l'agent alors que l'humain la lit |
| 5 | Vérifier | `python3 .socle/socle verify --rapide` | 40 lignes | rien | clair (pytest absent : dit tel quel) |
| 6 | Commiter, pousser | `git add -A`, `git commit`, `git push` | la sortie du hook | rien | rien ne dit qu'il faut commiter l'installation |
| 7 | Premier échange avec l'agent | ouvrir l'agent dans le projet | les questions de départ | répondre à quatre questions, chacune avec son défaut | bien guidé ; le lien n'existe qu'une fois poussé sur GitHub |
| 8 | Mettre à jour le socle | la commande de l'étape 2 | 52 lignes, fin en échec : `protege.fichiers` | recopier chaque fichier changé dans `socle approve --files …` | la liste peut être longue : chaque fichier du moteur qui a changé |
| 9 | Ajouter une mémoire privée à un projet installé | la commande de l'étape 2 avec `--private compagnon` | « dépôt privé absent — le cloner… » | rien | **défaut** : la politique n'est pas réécrite, et la mémoire privée reste « non configurée », contrairement à ce qui est annoncé |
| 10 | Mettre en place le mode compagnon | créer un dépôt privé, le cloner dans le dossier privé, y commiter, `socle prive verrouiller`, créer une clé de déploiement, poser deux secrets dans la CI | une ligne de commentaire de la politique | tout | six gestes, dont trois sur GitHub, aucun guidé |
| 11 | Commiter du code soi-même | `git commit` | rien : le hook passe | rien | la CI refuse ensuite une fonction publique sans test ; il faut connaître le trailer `Dispense-test:` |
| 12 | Approuver son propre changement protégé | `python3 .socle/socle approve --files … --text "…"` | « D-NNNN écrite et validée » | rien | ce numéro n'est rappelé nulle part ensuite (la question de Théo sur D-0012) |

## Ce que l'humain doit savoir aujourd'hui

- **Vingt commandes** dans l'aide de `socle`, sans distinction : cinq sont pour
  l'humain (`install`, `approve`, `answer`, `relu`, `state`), les autres pour
  l'agent, les hooks ou la CI.
- **Aucun texte n'est écrit pour lui** : le README tient en 45 lignes et
  annonçait encore trois adaptateurs (corrigé avec ce relevé) ; `AGENTS.md` et
  le format de la mémoire sont écrits pour l'agent.
- **Ce qu'il fait de ses mains** : répondre aux demandes dans la
  conversation, approuver ses propres changements protégés, relire avant
  publication s'il l'a choisi, mettre à jour le socle, et dispenser un test
  par un trailer quand il commite lui-même.
- **Ce qu'il doit comprendre pour décider** : la politique (huit points), les
  garde-fous et leur cliquet, le plafond de mutation, les modes de mémoire
  privée et de relecture.

## Propositions

Chacune avec son effort, ce qu'elle change, et si elle se défait.

| # | Proposition | Effort | Ce qu'elle change |
| --- | --- | --- | --- |
| P1 | **Une installation qui finit verte.** Les modules qui ont déjà du code entrent au cliquet de mutation « à mesurer » : un avertissement, jusqu'au premier balayage, qui pose la valeur mesurée. | moyen | l'étape 3 disparaît ; plus d'échec à la première commande |
| P2 | **« Et maintenant »** à la fin de chaque commande de l'humain (`install`, `init`, mise à jour) : trois à cinq lignes, dans l'ordre, de ce qui reste à faire (commiter, pousser, ouvrir l'agent, répondre à la demande D-NNNN). L'audit ne montre que ce qui échoue. | faible | les étapes 4 et 6 se lisent seules ; une sortie de 56 lignes en devient une de 15 |
| P3 | **Approuver d'un geste ce que l'humain vient de changer** : `socle approve` sans `--files` liste les fichiers protégés changés, puis les approuve sur confirmation ; l'installeur imprime la commande exacte. | faible | l'étape 8 tient en une commande |
| P4 | **Corriger `--private` sur un projet installé** : la section de la politique s'écrit si elle manque, puisque c'est l'humain qui lance la commande. | faible | le défaut de l'étape 9 |
| P5 | **Mettre en place le mode compagnon pas à pas** (`socle prive installer`) : clone, premier commit, verrou, clé de déploiement créée, et les deux secrets à poser, avec le lien de la page GitHub où les poser. | moyen | l'étape 10 passe de six gestes à un, plus deux copier-coller sur GitHub |
| P6 | **Une page pour l'humain** : `socle aide`, ses cinq gestes, chacun avec sa commande ; l'aide de `socle` range les commandes en trois groupes (humain, agent, interne). | faible | l'humain trouve son chemin sans lire `AGENTS.md` |
| P7 | **Rappeler ce que l'humain a fait lui-même** : l'état du démarrage liste les approbations et réponses écrites depuis le dernier tour de l'agent, qui les cite. | faible | la question sur D-0012 ne se pose plus |
| P8 | **Le README à jour, et un guide de l'humain court** : la base de la documentation (B-0035). | faible | l'entrée du dépôt dit vrai |
| P9 | **Prévenir au commit plutôt qu'en CI** : le hook avant commit avertit qu'une fonction publique sans test sera refusée par la CI sans `Dispense-test:` dans le message. | faible | l'étape 11 ne surprend plus |
| P10 | **S'installer sans clone** : un paquet installable par pip, qui fournit la commande `socle`. | important | l'étape 1 disparaît ; publication externe : une décision à part |

Recommandation : P1 à P4 et P6 à P9 maintenant, P5 ensuite, P10 plus tard et
par une demande à part, puisqu'elle publie un paquet.

## Suite donnée

Théo a validé la recommandation (D-0014). Chaque proposition retenue a été
éprouvée sur une installation neuve, d'un projet Python sous pytest ; le
détail est au journal (J-2026-10-11-U, J-2026-10-11-V).

| # | Ce qui a été fait | Étapes du parcours |
| --- | --- | --- |
| P1 | le code existant entre « à mesurer » au cliquet de mutation ; un avertissement, et `socle mutation-verdict --poser` écrit le plafond mesuré | l'installation finit verte ; l'étape 3 disparaît |
| P2 | l'audit et les hooks git ne montrent que ce qui échoue, avertit ou n'a pas pu s'exécuter ; l'installation finit par « Et maintenant », `init` par « Pour toi » ; un commit refusé pour des fichiers protégés rappelle l'approbation | l'installation tient en 28 lignes au lieu de 56 ; les étapes 4 et 6 se lisent seules |
| P3 | l'approbation sans `--files` liste les fichiers protégés changés et les approuve sur confirmation | l'étape 8 tient en une commande, que « Et maintenant » donne |
| P4 | `--private` sur un projet installé écrit la section de la politique qui manque | le défaut de l'étape 9 |
| P5 | `socle prive installer --depot <adresse>` : clone, premier commit poussé, verrou, clé de déploiement, puis les deux gestes sur GitHub avec leurs liens | l'étape 10 passe de six gestes à un, plus deux sur GitHub |
| P6 | le guide de l'humain, `moteur/socle/AIDE.md`, affiché par `socle aide` ; l'aide rangée par public ; `socle` seul donne celle de l'humain ; `--adapter auto` par défaut | l'humain trouve son chemin sans lire `AGENTS.md` |
| P7 | l'état liste ce que l'humain a écrit lui-même depuis le dernier commit de l'agent, que l'agent lui cite | la question sur D-0012 ne se pose plus |
| P8 | le README commence par le parcours simplifié, et renvoie au guide | l'entrée du dépôt dit vrai |
| P9 | le hook `commit-msg` avertit, sans refuser, d'une fonction publique sans test ni dispense | l'étape 11 ne surprend plus |
| P10 | pas faite : une publication externe, qui attend sa propre demande (B-0042) | — |

