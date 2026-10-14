# Architecture du socle

Ce document dit où chaque exigence du cadrage
(`memory/archives/cadrage-2026-10-10.md`) est appliquée, et ce qui ne l'est
pas encore. Il s'adresse à qui fabrique le socle ; pour le comprendre
sans entrer dans le code, `docs/socle.md`. La liste exacte des contrôles se dérive du code :
`python3 .socle/socle checks`.

## Les trois pièces

| Pièce | Où, dans un projet | Qui la modifie |
| --- | --- | --- |
| Moteur immuable | dans un projet, .socle/engine/socle/ (ici, la source : `engine/socle/`), lanceur `.socle/socle`, verrou .socle/engine.lock | l'installeur seul ; la CI vérifie l'empreinte |
| Fichiers du projet | memory/, .socle/policy.toml, .socle/adapter.toml, .socle/guardrails.toml | le projet, selon la politique |
| Étages d'application | `.claude/settings.json`, `.socle/git-hooks/`, `.github/workflows/socle.yml` (et le balayage de mutation hebdomadaire, quand l'adaptateur en déclare un), `.github/CODEOWNERS` | l'installeur ; fichiers protégés |

Les trois étages appellent le même moteur : `python3 .socle/socle hook …`
pour l'agent et pour git, `python3 .socle/socle ci` pour la CI.

Ces chemins sont ceux du **format 2** de la mémoire (`ADR-0018`) : en
anglais pour tous, quelle que soit la langue du contenu. Un projet au
format 1 (`memory/`, `.socle/policy.toml`, `.socle/engine.lock`…, comme
ce dépôt jusqu'à sa migration) se lit tel quel : le moteur choisit la table
des chemins d'après le verrou, puis la politique, puis le dossier de
mémoire. La migration renomme et traduit les chemins de la configuration et
de la documentation, jamais la mémoire, qui est en ajout seul : un ancien
chemin cité dans une entrée gelée reste une référence valide, et une ancre
écrite avant le renommage aussi. En CI, la plage qui migre lit la base sous
les noms de la tête, pour que le cliquet, l'ajout seul et les références
comparent le même fichier sous ses deux noms.

## Le moteur, module par module

| Module | Rôle |
| --- | --- |
| `cli.py` | les commandes, rangées par public dans l'aide (l'humain, l'agent, les hooks et la CI) : `help`, `state`, `show`, `check`, `verify`, `ci`, `hook`, `new`, `next-id`, `url`, `private`, `reviewed`, `answer`, `approve`, `install`, `init`, `selftest`, `fingerprint`, `mutation-verdict`, `mutation-run`, `renumber`, `archive`, `checks` ; sans commande, l'aide de l'humain ; les anciens noms français (`aide`, `prive`, `relu`, `--oui`…) restent acceptés une version, lus sous leur nom anglais par la ligne de commande comme par le hook (ADR-0027) |
| `HELP.md` | le guide de l'humain, source unique : ses gestes, chacun avec sa commande ; `socle help` l'affiche |
| `memory.py` | lecture des cinq couches : en-têtes, entrées, identifiants, métadonnées, références |
| `requests.py` | le contrat des demandes, son lint, les réponses humaines gelées |
| `context.py` | le registre des contrôles, leurs étages, la base de comparaison, le mode adoption |
| `readings.py` | la lecture prouvée, une seule fonction pour le contrôle et le hook (ADR-0023) |
| `checks_memory.py` | format, références (un chemin cité par une couche gelée vaut s'il a existé dans l'historique, ADR-0027), fuite d'identifiants privés (blocs de code et archives compris), preuves, backlog, budgets, péremption, retard, ajout seul (la mémoire privée relue à la base, B-0044, L3), demandes, source unique des instructions |
| `checks_docs.py` | outillage documenté, valeurs liées, correspondance code ↔ doc, refus des copies |
| `checks_tests.py` | capacités de l'adaptateur, tests creux, valeurs attendues, régression rejouée sur le parent, couverture de mutation, code nouveau nommé par un test (un fichier renommé se compare à son ancien nom) |
| `checks_ratchet.py` | cliquet des garde-fous (une correspondance ou une valeur liée qui suit ses fichiers renommés n'assouplit rien, ADR-0027), fichiers protégés (un renommage compte ses deux chemins ; le déplacement d'une migration de format se juge sous le nom nouveau), empreinte du moteur, configuration et trace des hooks |
| `tests_reader.py` | extraction des fonctions de test selon l'adaptateur (blocs à accolades, indentés ou fermés par `end`) ; transitivité des assertions |
| `hooks.py` | les points d'entrée des hooks de l'agent et de git, la trace, dont chaque refus et l'étage qui l'a prononcé ; chaque commande shell de l'agent jugée commande simple par commande simple : écriture d'un fichier protégé ou d'un réglage de Claude Code, commande réservée à l'humain, push forcé ou vers la branche par défaut, publication, suppression distante (B-0044, L2) |
| `commands.py` | le découpage d'une commande shell en commandes simples, par `shlex` : séparateurs, redirections, `cd` suivi, `bash -c` et `eval` ouverts, préfixes (`env`, `sudo`, `python -m`) retirés ; le corps d'un heredoc n'est que du texte |
| `state.py` | l'état dérivé ; si GitHub exige la CI du socle avant de fusionner sur la branche par défaut (ensemble de règles ou protection classique, lus par `gh`), sinon une action de l'humain avec le lien de la page (B-0044, L2, R1) |
| `human.py` | ce qui revient à l'humain ; ce qu'il a écrit lui-même depuis le dernier commit de l'agent (approbations, réponses de son terminal), que l'état liste pour que l'agent le cite ; la lecture du dernier message de l'agent pour le récap |
| `private.py` | la mémoire privée : modes compagnon et chiffré, verrou, accès, couches privées par défaut, contrôles `prive.*` ; un terme privé cherché sous ses variantes d'écriture, dans le contenu, les noms de fichier et de branche ; rien d'écrit sans accès ; la mémoire privée lue à une révision |
| `move.py` | la bascule d'une entrée publique dans la mémoire privée (`socle private move`) |
| `identifiers.py` | les identifiants que deux branches prennent ensemble : ceux des branches distantes, la collision avec la branche par défaut, la renumérotation (ADR-0026) |
| `private_setup.py` | la mise en place du dépôt compagnon, réservée à l'humain (`socle private install`) |
| `links.py` | le permalien d'un fichier ou d'une entrée ; les liens d'un message que l'humain ne pourra pas suivre |
| `verification.py` | le contrat `verify` : les capacités de l'adaptateur |
| `mutation.py` | le balayage de l'adaptateur, module par module quand sa commande en nomme un, puis le verdict contre les plafonds ; un lecteur par outil (cargo-mutants, mutmut, Stryker, gremlins, PIT, mutant, Infection) ; un module « à mesurer » reçoit son plafond mesuré (`--record`) ; la vivacité du workflow planifié, lue par l'API de GitHub |
| `fingerprint.py` | l'empreinte du moteur |
| `installer.py` | installation, mise à jour, adoption ; adaptateur déduit du dépôt ; mémoire privée posée à l'installation, ou ajoutée à un projet installé ; diff de politique à la mise à jour ; le code existant entre « à mesurer » au cliquet de mutation ; un audit court, puis « Et maintenant », les étapes de l'humain avec leur commande ; ne s'installe qu'à la racine du dépôt ; relancé, il ne perd rien : le moteur reste en place s'il est lancé depuis le projet, un CLAUDE.md propre au projet passe dans AGENTS.md, une seconde adoption complète sa liste, et ce que le .gitignore du projet écarterait reçoit une exception (B-0044, L1) ; le format de la mémoire en paramètre, l'actuel par défaut, que fixe un test qui porte sur un format antérieur, et la ligne du backlog des instructions et son plafond qui le suivent (ADR-0025) |
| `language.py` | la langue de la mémoire : le vocabulaire du format par langue, ramené à des clés internes à la lecture, et celui du projet à l'écriture |
| `config.py` | la configuration du projet et les deux tables de chemins (formats 1 et 2), choisie par projet et par révision |
| `migrations.py` | les migrations de format, appliquées dans l'ordre à la mise à jour ; du format 1 au 2, le renommage des chemins |
| `initialization.py` | les trois entrées d'initialisation : document archivé tel quel, audit du dépôt en lecture seule, questions de départ |
| `selftest.py` | l'injection de défauts dans un projet jetable : chaque contrôle du registre et chaque refus reconnu en ont au moins un (un test l'exige, ou une exemption écrite), une mutation factice exerce le cliquet de mutation, et des témoins vérifient qu'un changement validé par l'humain passe (B-0044, L4) ; un sujet s'y ajoute dans l'un ou l'autre format du backlog (ADR-0025) |
| `adapters/` | Rust (extrait de chess), Python sous `unittest`, Python sous `pytest` avec `mutmut` (jalon 6), JavaScript et TypeScript, Go, Java, Ruby et PHP (B-0030, éprouvés par `bench/adapters.py`), maintenus ; ce qu'est un adaptateur : `engine/socle/adapters/README.md` |
| `templates/` | les gabarits posés par l'installeur |

## Exigences du cadrage et contrôles qui les appliquent

| Exigence | Contrôle ou mécanisme | Étages |
| --- | --- | --- |
| Format parsable, identifiants stables, statuts ; un titre qui commence comme une entrée sans en être une lisible est refusé | `memoire.format` | agent, git, CI |
| Toute référence vérifiée, lien mort refusé ; une référence nue s'arrête avant sa ponctuation finale, un lien se lit décodé (B-0020) ; un chemin d'un autre dépôt (`depot:chemin`) n'est admis sans avertissement que si le projet lie ce dépôt par son adresse, ou, à défaut, le déclare dans `[references] repos`, ce que seul l'humain valide (B-0052) | `memoire.references`, `cliquet.garde-fous` | agent, git, CI |
| Fait mesuré avec preuve, réfuté barré, validé par l'humain | `memoire.preuves`, hook `pre-tool-use` | agent, git, CI |
| Backlog : origine, clôture avec référence | `memoire.backlog` | agent, git, CI |
| Budgets de taille | `memoire.budgets` | agent, git, CI |
| Péremption de l'actif (avertissement) | `memoire.peremption` | agent, git, CI |
| Journal et décisions en ajout seul (une citation d'une décision comprise, un ajout au journal sur une ligne nouvelle) ; fait jamais effacé ; une validation se reconnaît à son identifiant, migration comprise | `memoire.ajout-seul` | agent, git, CI |
| Mémoire en retard sur le code : fin de tour refusée | `memoire.retard` | agent |
| Le privé ne fuit pas dans le public (identifiants) | `memoire.prive` | agent, git, CI |
| Mémoire privée en dépôt compagnon : rien de privé dans le dépôt public, verrou à jour | `prive.verrou`, `socle private lock`, `socle private extract` | agent, git, CI |
| Mémoire privée chiffrée : rien de commité en clair, filtre en place | `prive.chiffre` | agent, git, CI |
| Mémoire privée indisponible : signal explicite, jamais en silence | `prive.acces`, état dérivé au démarrage | agent, git, CI |
| Liste des termes privés : ajout libre, retrait sur validation humaine (D-0007) | `prive.termes`, `socle private term` | agent, git, CI |
| Aucun terme privé ni identifiant privé dans ce qui se publie (D-0008), un terme sous ses variantes (`acme_corp`, `AcmeCorp`, coupé en fin de ligne) | `prive.fuites` (contenus, noms des fichiers nouveaux, nom de la branche en CI) ; hook `pre-tool-use` (écritures et noms de fichier, `git commit`, `gh` et les fichiers qu'ils publient par `--body-file` ou `-F`, branches créées ou poussées, outils `mcp__`) ; hook git `commit-msg` ; hook git `pre-push` (nom de la branche distante) | agent, git, CI |
| Le cadrage, d'où viennent les termes privés, archivé dans la zone privée quand elle existe | `socle init --brief` | — |
| Relecture humaine avant publication, au choix de l'humain : aucune, à chaque push, par lots (D-0006) | hook `pre-tool-use` sur `git push`, hook git `pre-push`, `socle reviewed` | agent, git |
| Demandes et réponses privées, sur décision de l'humain (`[private] requests`) | `socle new`, réponses privées protégées comme les publiques | agent, git, CI |
| Le privé choisi couche par couche (`[private] layers`) et entrée par entrée ; une entrée publique existante basculée en privé sans casser un renvoi ni rien effacer | `socle new --private/--public`, `socle private move` ; `memoire.format` (l'entrée publique ne garde que son identifiant), `memoire.ajout-seul` (une copie privée reprend son texte) | agent, git, CI |
| Journaux de CI sans contenu privé | masquage des constats de la zone privée à l'étage CI ; `socle private recover` n'écrit ni l'adresse ni la sortie de git | CI |
| Contrat des demandes : huit champs (les sept du cadrage et « Où regarder », avec un lien vers chaque document à lire), contexte d'au moins soixante mots, aucun identifiant nu | `demandes.contrat`, hook `pre-tool-use` | agent, git, CI |
| Décision archivée avec le texte exact | `demandes.reponses` (empreinte de la demande) | agent, git, CI |
| Un identifiant ne se définit qu'une fois, même entre deux branches : `socle new` saute ceux des branches distantes ; celui que la branche par défaut a pris aussi depuis la divergence est dit avant la fusion, et se renumérote (ADR-0026) | `socle new`, `memoire.collisions`, `socle renumber` | agent, git, CI |
| Le backlog en un fichier par sujet (format 3), un plafond par sujet, rien d'archivé ; un lien vers l'ancre d'un sujet dans l'ancien fichier unique reste valide ; une action humaine donnée avec le lien de son sujet (ADR-0025) | `memoire.format`, `memoire.budgets`, `memoire.references`, la migration 2 → 3, l'état | agent, git, CI |
| `AGENTS.md` fait foi, `CLAUDE.md` l'importe ; ou, sans `AGENTS.md`, `CLAUDE.md` que l'installeur a gardé parce que le projet le nomme, et qui porte la section du socle (B-0049) | `instructions.source-unique` | agent, git, CI |
| Valeurs dupliquées liées à leur source ; `3,5` vaut `3.5`, pas `35` | `docs.valeurs` | agent, git, CI |
| Outillage documenté | `docs.outillage` | agent, git, CI |
| Correspondance code ↔ doc, dispense motivée, qui ne couvre que le code de son commit | `docs.correspondance` (pas au commit : le hook ne voit pas le message, donc pas la dispense) | agent, CI |
| Pas de copie | `docs.copie` | agent, git, CI |
| Capacité absente déclarée avec remplacement | `adaptateur.capacites` | agent, git, CI |
| Tests creux, lus hors de leurs commentaires ; une aide qui affirme vient des tests, jamais du code de production ; un groupe de tests désactivé hors de tout test exige sa raison | `tests.creux` (sur le diff aux étages agent et git) | agent, git, CI |
| Test supprimé, valeur attendue changée ; à la fin du tour, en attente d'une demande poussée qui nomme le test, un avertissement (B-0033) ; une assertion se lit entière, sur toutes ses lignes et normalisée hors des littéraux, et des tests homonymes s'apparient dans l'ordre du fichier ; une valeur changée hors des assertions (variable, constante, aide) est dite, pas refusée (ADR-0024) | `tests.attendus` | agent, git, CI |
| Correctif avec test de régression rejoué sur le parent, où il échoue sans y manquer de se charger (`load_error`) ; un test écrit dans le module qu'il teste (Rust) s'y rejoue avec ses seules lignes de test, le code du parent gardé (B-0051) | `tests.regression` | CI |
| Code nouveau ou modifié testé : une fonction publique est nommée par un test, hors de ses commentaires, ou dispensée nommément avec sa raison (`Dispense-test:`) | `tests.code-teste` ; au commit, un avertissement du hook `commit-msg`, le premier qui voit la dispense (B-0034, P9) | agent, CI ; avertissement au commit |
| Mutation : plafond par module, cliquet ; un module pas encore balayé y entre « à mesurer » (un avertissement), et le premier verdict pose son plafond, relu après écriture (un plafond qu'il ne sait pas écrire est dit) | `mutation.couverture`, `socle mutation-verdict --record` | agent, git, CI ; verdict hebdomadaire |
| Le balayage tourne : un workflow hebdomadaire, posé par l'installeur sauf si le projet en lance déjà un, lance la commande de l'adaptateur (module par module, chacun dans son dossier `{output}`), rend le verdict et ouvre une issue quand le cliquet casse ; un workflow endormi par GitHub, ou qui ne tourne plus depuis quinze jours, casse la CI et revient à l'humain dans l'état (B-0005) | `socle mutation-run`, `mutation.vivante`, la ligne `mutation` de l'état | CI ; chaque semaine |
| Rien ne s'affaiblit en silence | `cliquet.garde-fous`, `protege.fichiers` | agent, git, CI |
| Moteur et politique non altérés | `moteur.empreinte`, `protege.fichiers` | agent, git, CI |
| Seule la CI est incontournable : GitHub l'exige avant toute fusion | une étape de « Et maintenant » à l'installation ; la ligne `branche` de l'état, et une action de l'humain quand elle n'est pas exigée | GitHub |
| Hooks chargés et déclenchés | `hooks.configuration`, `hooks.trace` (trailer `Socle-Hooks`) | CI |
| Action irréversible ou externe refusée | hook `pre-tool-use` | agent |
| Anti-fabrication | hook `pre-tool-use` : SHA complété de tête, identifiant ou commit inventé | agent |
| Échec répété : arrêt et escalade | hook `stop`, `max_attempts` de la politique | agent |
| État dérivé au démarrage et après compactage, avec l'index des décisions | `socle state`, hook `session-start` ; `socle show <ID>` pour lire une entrée à la demande | agent |
| Ce qui revient à l'humain et la suite, dits à chaque fin d'intervention qui a agi (lignes « Pour toi : » et « Ensuite : ») | `human.py` (demandes en attente, backlog `pour : humain`, branches distantes supprimables, prochaines étapes du chantier actif), hook `stop` | agent |
| Des liens que l'humain peut suivre : permaliens au commit poussé, aucun lien relatif ni chemin inexistant, chaque demande en attente avec son lien | `links.py`, `socle url`, hook `stop` | agent |
| Lire avant de décider, prouvé par l'empreinte de la version lue | `memoire.lectures` ; hook `pre-tool-use` (empreinte périmée ou inventée) ; `socle show`, `socle new` | agent, git, CI |
| Installation en une commande, adaptateur déduit du dépôt, mémoire privée et langue de la mémoire choisies à l'installation | `socle install --adapter auto [--private …] [--language en]` | — |
| Mise à jour : moteur remplacé, formats migrés, diff de politique montré pour validation humaine | `socle install` relancé, `migrations.py` ; en CI, base lue sous les noms de la tête | — |
| Initialisation depuis un cadrage, rien, un dépôt existant, ou les deux : rien d'inventé, questions plafonnées avec leurs défauts | `socle init`, demande de départ au contrat, `memoire.preuves` | agent, git, CI |
| Auto-tests par injection de défauts | `socle selftest`, dans `socle ci` | CI |

## Les choix qui ne sont pas dans le cadrage

- **Une validation humaine est une réponse ajoutée dans la plage, qui cite ce
  qu'elle valide** (`ADR-0004`) : la clé assouplie, le nom du test, ou le
  chemin et l'empreinte du fichier protégé. **L'humain répond dans la
  conversation**, et l'agent consigne la réponse avec sa citation exacte
  (`ADR-0006`), seulement si la demande est poussée telle quelle : l'humain
  doit avoir pu la lire.
- **La trace des hooks voyage dans les commits** (`ADR-0005`). Elle vit
  dans le répertoire git commun (`.git/socle/hooks.log`), partagé par tous
  les worktrees du dépôt. Chaque refus y est noté (`Refus`, avec l'étage
  et ce qui a refusé) : le banc d'évaluation y lit quel étage attrape quoi.
  Le trailer compte la session qui commite, pas la plus récente : une
  session aux hooks coupés compte zéro, et la CI la refuse (B-0044, L2).
- **Le hook de l'agent juge ce qu'une commande fait, pas le texte qu'elle
  cite** (B-0044, L2) : découpée en commandes simples, chacune jugée par
  son programme et ses arguments. Un message de commit, un heredoc ou un
  `grep` qui citent une commande dangereuse passent ; un lanceur entre
  guillemets, un `cd` préalable ou des drapeaux groupés ne la cachent plus.
  Les réglages de Claude Code (`.claude/settings*.json`, où qu'ils soient)
  ne s'écrivent pas par l'agent, et les commandes réservées à l'humain
  refusent d'elles-mêmes de tourner sous un agent, en défense derrière le
  hook.
- **Le hook avant commit juge l'index**, figé en arbre par `git write-tree` :
  ce qui sera commité, pas ce qui est sur disque. **Le hook avant push juge
  aussi la plage qui part** (B-0043), du commit distant au commit local :
  c'est celle que la CI du push jugera, plus étroite que la divergence avec
  la branche par défaut.
- **Le cliquet compare la base et la tête clé par clé**, avec un sens par
  clé : plus bas est plus strict pour un budget, plus long pour une
  couverture, plus court pour une liste d'exclusions. Une clé inconnue qui
  change est un assouplissement jusqu'à preuve du contraire. Une doc
  ajoutée à une correspondance code ↔ doc assouplit (l'exigence est plus
  facile à satisfaire) ; un plafond de mutation qui apparaît vient de la
  mesure : nul, ou avec la raison qu'écrit `mutation-verdict --record`, au
  même compte (B-0044, L2).
- **Lecture prouvée** (`ADR-0008`, `ADR-0023`) : une entrée citée
  `ID@empreinte` l'a été dans cette version, l'actuelle ou celle du commit
  où la citation paraît ; un index, dans une version de la plage ; une
  décision, une demande ou un sujet de backlog nouveaux doivent le faire.
  Le contrôle et le hook appellent la même fonction. La preuve porte sur l'accès au texte, pas sur
  sa compréhension. Une entrée qui change de fichier, un sujet clos archivé
  au journal, garde sa preuve sans relire : la citation se juge au commit où
  elle a paru pour la première fois, dans l'entrée qui la porte.
- **Une vérification réussie se mémorise** (L6) : les étapes rapides de
  l'adaptateur ne se relancent pas sur un arbre où elles ont déjà toutes
  passé, que ce soit la vérification que l'agent lance (`verify --fast`,
  `--redo` pour forcer), la fin de tour ou le hook avant push. L'empreinte
  de l'arbre est HEAD, le diff et le contenu des fichiers non suivis. La
  marque est locale, donc falsifiable : la CI, elle, refait tout. Le
  compteur des échecs de la fin de tour (politique, point 7) appartient à sa
  session : une session nouvelle ne commence pas à l'escalade.
- **L'auto-test tourne sur plusieurs fils**, un clone par cas (de 76 à 33
  secondes sur quatre cœurs), et une seule fois en CI : `socle ci` le lance
  lui-même, et le test de ce dépôt qui le joue lui cède alors la place.
- **Ce qui est trop long pour une fin de tour attend la CI** (D-0019) : le
  moteur pose `SOCLE_RAPIDE` pendant les étapes rapides, et un test peut
  s'y mettre de côté, avec sa raison écrite ; la CI, qui lance toutes les
  étapes, le joue toujours. Ce dépôt y met le banc et l'auto-test complet :
  sa suite rapide passe de 290 à 143 secondes (mesuré le 13 octobre).
- **Les liens donnés à l'humain sont des permaliens** (`ADR-0010`) : au
  commit poussé, pas à la branche, qui disparaît à la fusion ; vérifiés par
  le hook de fin de tour, que l'agent ait agi ou non.
- **Une fonction publique ajoutée ou modifiée est nommée par un test**
  (`ADR-0011`), au sens littéral : son nom figure dans un test. Une fonction
  privée en est exemptée, une dispense la nomme avec sa raison ; la qualité
  des assertions reste l'affaire de la mutation.
- **Mode adoption** : à l'installation sur un projet existant, les budgets
  sont fixés au niveau actuel et les contrôles en échec passent en
  avertissement (`[adoption] warn_only`), liste dont on ne retire que pour
  durcir.
- **Une valeur attendue ne change que sur une spécification écrite par
  l'humain** (`ADR-0017`), ou sur une demande validée : une ADR que l'agent
  écrit dans le même travail ne l'autorise pas à changer un test.
  Hors des assertions, une valeur changée est signalée sans être refusée
  (`ADR-0024`) : rien ne distingue une donnée de test d'une valeur
  attendue, et le refus mesuré sur la migration de format frappait 34
  tests à tort.
- **Les demandes échappent au refus des copies** (`ADR-0016`) : une demande se
  lit seule, son contexte recopié sur place, et elle est gelée une fois
  répondue ; deux approbations du même gabarit ne bloquent plus un commit.
- **Une entrée basculée dans la mémoire privée garde son identifiant en
  public** (`ADR-0019`), sans titre ni texte : les renvois restent valides
  sans réécrire les entrées gelées, et la copie privée qui cite
  `depuis : <ID>` prouve que rien n'est effacé. L'historique public garde
  l'ancien texte ; le réécrire revient à l'humain.
- **Les chemins d'un projet sont en anglais** (`ADR-0018`), au format 2 de
  la mémoire ; le format 1 reste lu, et la migration ne réécrit pas la
  mémoire.
- **La mémoire s'écrit dans la langue du projet et se lit dans toutes**
  (`ADR-0020`) : le moteur ramène chaque mot-clé à une clé interne, une
  mémoire existante n'a rien à réécrire, et les messages du moteur restent
  en français.
- **Ce qu'on tape et ce qu'on voit dans l'arborescence est en anglais, le
  code se lit en français** (`ADR-0027`) : commandes, options, dossiers,
  modules et gabarits portent des noms anglais, les anciens noms de
  commandes et d'options restent acceptés une version, un module s'importe
  sous son nom français ; les noms des tests et de la documentation ne
  changent pas, et la mémoire gelée garde les chemins d'avant.
- **Une tautologie voulue passe avec sa raison écrite** (`socle: voulu —`),
  validé par Théo (`D-0004`).

## Ce qui n'est pas fait

Le banc d'évaluation du jalon 9 (`docs/banc.md`) mesure ce que fait un agent
réel équipé du socle ; ses résultats vont au journal.

Le backlog le tient : jalon 9, empreinte comparée à la
version publiée, workflow de mutation générique. Les limites connues des contrôles y sont aussi :
chemins qui n'existent que dans une rustine, copie non marquée d'une valeur
qui n'est qu'un avertissement.
