"""Le catalogue anglais des messages du moteur (ADR-0028) : le texte français,
tel qu'il est écrit dans le code, vers sa traduction. Les variables `{nom}`
sont les mêmes des deux côtés ; `tests/test_messages.py` le vérifie, et
qu'aucun message enveloppé n'y manque."""

MESSAGES: dict[str, str] = {
    "\n!! hooks git non branchés : `git config core.hooksPath .socle/git-hooks`":
        "\n!! git hooks not wired: `git config core.hooksPath .socle/git-hooks`",
    "SHA fabriqué : {sha} n'est pas un objet de ce dépôt, alors que son préfixe {prefixe} en est un. Le SHA complet "
    "de {prefixe} est {reel}. Ne jamais compléter un SHA de tête : `git rev-parse`.":
        "Fabricated SHA: {sha} is not an object of this repository, while its prefix {prefixe} is. The full SHA of "
        "{prefixe} is {reel}. Never complete a SHA from memory: `git rev-parse`.",
    "`{ident}@{h}` (ligne {ligne}) n'est pas l'empreinte de la version actuelle de {ident} : la relire, `python3 "
    ".socle/socle show {ident}`":
        "`{ident}@{h}` (line {ligne}) is not the fingerprint of the current version of {ident}: read it again, "
        "`python3 .socle/socle show {ident}`",
    "`{index}@{h}` (ligne {ligne}) n'est l'empreinte d'aucune version récente de l'index : le relire, `python3 "
    ".socle/socle show --index {index}`":
        "`{index}@{h}` (line {ligne}) is not the fingerprint of any recent version of the index: read it again, "
        "`python3 .socle/socle show --index {index}`",
    "`{ident}` (ligne {ligne}) ne désigne aucune entrée de la mémoire — créer l'entrée d'abord, ou corriger "
    "l'identifiant ; ne jamais en inventer un":
        "`{ident}` (line {ligne}) names no entry of the memory — create the entry first, or fix the identifier; "
        "never invent one",
    "`commit:{cible}` n'existe pas dans ce dépôt — lire le SHA avec `git rev-parse`, jamais de tête":
        "`commit:{cible}` does not exist in this repository — read the SHA with `git rev-parse`, never from memory",
    "`{id}` passe à « validé » sans demande validée par l'humain : ce statut ne s'écrit que par l'humain (politique, "
    "point 5). Émettre une demande `D-NNNN`.":
        "`{id}` becomes “validated” without a request approved by the human: this status is only written by the "
        "human (policy, rule 5). Open a request `D-NNNN`.",
    "{chemin}/ (dont {touche})":
        "{chemin}/ (including {touche})",
    "push forcé":
        "force push",
    "suppression d'une branche distante":
        "deletion of a remote branch",
    "push de toutes les références":
        "push of all references",
    "push forcé (+)":
        "force push (+)",
    "push sur la branche par défaut ({protegee})":
        "push to the default branch ({protegee})",
    "action externe ou irréversible ({outil}) : validation humaine requise (politique, point 4). Émettre une "
    "demande, travailler sur autre chose en attendant.":
        "external or irreversible action ({outil}): human approval required (policy, rule 4). Open a request, work "
        "on something else meanwhile.",
    "commande irréversible ou externe ({action}) : « {commande} » — validation humaine requise (politique, point 4). "
    "Si c'est une décision, émettre une demande `D-NNNN` ; si c'est une action que l'humain doit faire lui-même, "
    "l'inscrire au backlog avec `pour : humain`. Puis continuer sur autre chose.":
        "irreversible or external command ({action}): “{commande}” — human approval required (policy, rule 4). If it "
        "is a decision, open a request `D-NNNN`; if it is an action the human must do themselves, add it to the "
        "backlog with `for : human`. Then go on with something else.",
    "`{saut}` contourne les hooks du projet : la CI exécute tout, et rien ne la contourne. Corriger ce que le hook "
    "refuse ; s'il refuse à tort, l'inscrire au backlog et le dire à l'humain.":
        "`{saut}` bypasses the project's hooks: the CI runs everything, and nothing bypasses it. Fix what the hook "
        "refuses; if it refuses wrongly, add it to the backlog and tell the human.",
    "`socle private install` est réservé à l'humain : il pousse vers le dépôt privé et crée une clé de déploiement "
    "(politique, point 4). L'inscrire au backlog avec `pour : humain`.":
        "`socle private install` is reserved for the human: it pushes to the private repository and creates a deploy "
        "key (policy, rule 4). Add it to the backlog with `for : human`.",
    "`socle approve` est réservé à l'humain : il valide ses propres changements protégés.":
        "`socle approve` is reserved for the human: it approves their own protected changes.",
    "l'agent ne répond jamais à la place de l'humain. Il ne peut que relayer une réponse donnée dans la conversation "
    ": `socle answer D-NNNN <réponse> --relayed --by <nom> --quote-file <texte exact>` (ADR-0006), ou `socle "
    "reviewed --relayed --by <nom> --quote-file <texte exact>` pour une relecture avant publication.":
        "the agent never answers in the human's place. It can only relay an answer given in the conversation: `socle "
        "answer D-NNNN <answer> --relayed --by <name> --quote-file <exact text>` (ADR-0006), or `socle reviewed "
        "--relayed --by <name> --quote-file <exact text>` for a review before publication.",
    "`{reglage}` : les réglages de Claude Code commandent ses hooks, seul l'humain les modifie (un réglage local "
    "peut les couper tous).":
        "`{reglage}`: Claude Code's settings drive its hooks, only the human changes them (a local setting can turn "
        "them all off).",
    "écriture d'un fichier protégé ({cible}) par le shell : seul l'humain modifie la politique, les hooks, la CI et "
    "le moteur (relance de l'installeur).":
        "write to a protected file ({cible}) through the shell: only the human changes the policy, the hooks, the CI "
        "and the engine (by running the installer again).",
    "`{chemin}` : les réglages de Claude Code commandent ses hooks, seul l'humain les modifie (un réglage local peut "
    "les couper tous).":
        "`{chemin}`: Claude Code's settings drive its hooks, only the human changes them (a local setting can turn "
        "them all off).",
    "`{rel}` est protégé par la politique : seul l'humain le modifie (CODEOWNERS), ou l'installeur pour les hooks, "
    "la CI et le moteur. Proposer le changement par une demande.":
        "`{rel}` is protected by the policy: only the human changes it (CODEOWNERS), or the installer for the hooks, "
        "the CI and the engine. Propose the change in a request.",
    "référence inventée — {fautes}":
        "invented reference — {fautes}",
    "demande hors contrat (elle doit se lire sans le projet en tête) — {fautes}":
        "request out of contract (it must read without the project in mind) — {fautes}",
    "fuite de la mémoire privée : {termes}. Une écriture publique ne cite ni identifiant privé ni terme de la liste "
    "privée : reformuler sans eux (politique, mémoire privée).":
        "private memory leak: {termes}. A public write cites neither a private identifier nor a term of the private "
        "list: rephrase without them (policy, private memory).",
    "contrôles de fin de tour (`socle check --stage agent`)":
        "end-of-turn checks (`socle check --stage agent`)",
    "Les contrôles échouent encore après {essais} tentatives : ARRÊT ET ESCALADE (politique, point 7). Écrire une "
    "demande `D-NNNN` qui résume l'échec, ce qui a été tenté et ce qui est supposé, puis s'arrêter.\n\n{rapport}":
        "The checks still fail after {essais} attempts: STOP AND ESCALATE (policy, rule 7). Write a request `D-NNNN` "
        "that sums up the failure, what was tried and what is assumed, then stop.\n\n{rapport}",
    "Les contrôles échouent (tentative {essais}/{maximum}) : corriger avant de conclure.\n\n{rapport}":
        "The checks fail (attempt {essais}/{maximum}): fix them before concluding.\n\n{rapport}",
    "récap de fin d'intervention non vérifiable : transcript illisible":
        "end-of-intervention recap cannot be checked: unreadable transcript",
    "sans {manque}":
        "without {manque}",
    "{n} lien(s) que l'humain ne pourra pas suivre":
        "{n} link(s) the human will not be able to follow",
    "fin d'intervention {defauts}, malgré un rappel":
        "end of intervention {defauts}, despite a reminder",
    "(le chantier actif n'a pas de section « Prochaines étapes »)":
        "(the active work has no “Next steps” section)",
    "Tu as agi pendant ce tour, et ton dernier message n'a pas {manque}. Termine par un récap de ce qui a été fait, "
    "puis :\n- « Pour toi : » ce qui revient à l'humain — décisions, actions qu'il est seul à pouvoir faire — ou « "
    "rien » ;\n- « Ensuite : » la suite proposée (prochain jalon, ce qu'il reste à faire avant), et ce que tu "
    "attends, s'il y a lieu (une CI, un match : quoi, et jusqu'à quand).\n\nCe qui revient à l'humain, calculé "
    "maintenant :\n{liste}\n\nProchaines étapes, selon le chantier actif :\n{suite}":
        "You acted during this turn, and your last message lacks {manque}. End with a recap of what was done, "
        "then:\n- “For you:” what falls to the human — decisions, actions only they can do — or “nothing”;\n- "
        "“Next:” the proposed next step (next milestone, what remains to do before it), and what you are waiting "
        "for, if anything (a CI run, a match: what, and until when).\n\nWhat falls to the human, computed "
        "now:\n{liste}\n\nNext steps, according to the active work:\n{suite}",
    " ni ":
        " and ",
    "Ton dernier message contient des liens que l'humain ne pourra pas suivre : il lit dans la conversation ou sur "
    "GitHub, pas dans ton conteneur.\n{liens}\nDonne un fichier par son permalien (`socle url <chemin|ID>`, après le "
    "push) ; n'écris entre accents graves que des chemins qui existent dans ce dépôt, et ceux d'un autre dépôt sous "
    "la forme `depot:chemin`.":
        "Your last message contains links the human will not be able to follow: they read in the conversation or on "
        "GitHub, not in your container.\n{liens}\nGive a file by its permalink (`socle url <path|ID>`, after the "
        "push); only put between backticks paths that exist in this repository, and those of another repository as "
        "`repo:path`.",
    "Ton dernier message cite {demandes}, en attente de l'humain, sans son lien : il doit pouvoir l'ouvrir d'un "
    "clic. Ajoute la sortie de `socle url {ids}`.":
        "Your last message cites {demandes}, waiting for the human, without its link: they must be able to open it "
        "in one click. Add the output of `socle url {ids}`.",
    "socle — contrôles avant commit":
        "socle — checks before commit",
    "\nFichiers protégés : si c'est l'humain qui les a changés (une mise à jour du socle, sa politique), `python3 "
    ".socle/socle approve --text \"<raison>\"` les liste et les approuve — réservé à l'humain ; l'agent, lui, ouvre "
    "une demande.":
        "\nProtected files: if the human changed them (a socle update, their policy), `python3 .socle/socle approve "
        "--text \"<reason>\"` lists and approves them — reserved for the human; the agent opens a request instead.",
    "\nCommit refusé. `git commit --no-verify` contourne ce hook, jamais la CI.":
        "\nCommit refused. `git commit --no-verify` bypasses this hook, never the CI.",
    "refus : {geste} est réservé à l'humain, et cette commande tourne dans une session d'agent (CLAUDECODE) — "
    "l'humain la lance dans son propre terminal":
        "refused: {geste} is reserved for the human, and this command runs in an agent session (CLAUDECODE) — the "
        "human runs it in their own terminal",
    "socle — commit refusé : {faute}":
        "socle — commit refused: {faute}",
    "socle — avertissement : ce correctif n'ajoute ni ne change aucun test ({liste}) : la CI le refusera "
    "(`tests.regression`), faute d'un test qui échoue sur le commit d'avant. L'ajouter à ce commit (`git commit "
    "--amend`), tant qu'il n'est pas poussé.":
        "socle — warning: this fix adds or changes no test ({liste}): the CI will refuse it (`tests.regression`), "
        "for lack of a test that fails on the previous commit. Add it to this commit (`git commit --amend`), as long "
        "as it is not pushed.",
    "Ouvrir la session de l'agent dans le dépôt du projet, où ses hooks se chargent (`.claude/settings.json`).":
        "Open the agent's session in the project's repository, where its hooks load (`.claude/settings.json`).",
    "socle — avertissement : commit d'agent sans aucun hook de l'agent pendant sa session (`Socle-Hooks: {valeurs}`) "
    ": la CI le refusera (`hooks.trace`). ":
        "socle — warning: agent commit without any agent hook during its session (`Socle-Hooks: {valeurs}`): the CI "
        "will refuse it (`hooks.trace`). ",
    "socle — avertissement : commit d'agent sans aucun hook de l'agent depuis le commit précédent "
    "(`Socle-Hooks-Since-Commit: {depuis}`) : ses hooks ont cessé de tirer en cours de session, et la CI le refusera "
    "(`hooks.trace`). ":
        "socle — warning: agent commit without any agent hook since the previous commit (`Socle-Hooks-Since-Commit: "
        "{depuis}`): its hooks stopped firing during the session, and the CI will refuse it (`hooks.trace`). ",
    "socle — avertissement : la CI refusera ce commit (`tests.code-teste`) :\n":
        "socle — warning: the CI will refuse this commit (`tests.code-teste`):\n",
    "\nLe commit passe ici. Écrire le test dans un commit suivant, ou amender ce message (`git commit --amend`) avec "
    "la dispense.":
        "\nThe commit goes through here. Write the test in a following commit, or amend this message (`git commit "
        "--amend`) with the waiver.",
    "socle — push refusé : fuite de la mémoire privée dans le nom de la branche : {liste}":
        "socle — push refused: private memory leak in the branch name: {liste}",
    "socle — push refusé : {refus}":
        "socle — push refused: {refus}",
    "socle — vérification avant push":
        "socle — checks before push",
    "décision":
        "decision",
    "action":
        "action",
    "réponse":
        "answer",
    "(pas encore poussé : pas de lien)":
        "(not pushed yet: no link)",
    "supprimer la branche distante `{branche}`, déjà contenue dans la branche par défaut":
        "delete the remote branch `{branche}`, already contained in the default branch",
    "(pas encore poussée : pas de lien)":
        "(not pushed yet: no link)",
    "ce qui revient à l'humain : rien":
        "what falls to the human: nothing",
    "ce qui revient à l'humain : {n}":
        "what falls to the human: {n}",
    "Le projet se construit avec cargo (Rust)":
        "The project builds with cargo (Rust)",
    "Le projet est un paquet Python":
        "The project is a Python package",
    "Le dépôt a {n} fonction(s) de test, dans {fichiers} fichier(s), dont `{premier}`":
        "The repository has {n} test function(s), in {fichiers} file(s), including `{premier}`",
    "Une CI GitHub existe : `{nom}`":
        "A GitHub CI exists: `{nom}`",
    "Le dépôt a un README":
        "The repository has a README",
    "celui du document de cadrage, tel qu'il est écrit":
        "the brief's, as it is written",
    "celui que dit le README, s'il en a un ; sinon aucun, et le backlog reste vide":
        "the one the README states, if there is one; otherwise none, and the backlog stays empty",
    "aucun : le backlog reste vide jusqu'à ce que tu en donnes un":
        "none: the backlog stays empty until you give one",
    "Quel est le but du projet, en une phrase ?":
        "What is the project's goal, in one sentence?",
    "le but alimente le backlog ; en défaut, il est noté « supposé »":
        "the goal feeds the backlog; by default, it is marked “assumed”",
    "Dans quel langage, avec quels outils de test ?":
        "In which language, with which test tools?",
    "celui de l'adaptateur posé à l'installation":
        "the one of the adapter installed with the socle",
    "l'adaptateur décide comment le socle lance les tests ; le changer demande ton accord":
        "the adapter decides how the socle runs the tests; changing it requires your approval",
    "Une partie de la mémoire doit-elle rester privée ?":
        "Should part of the memory stay private?",
    "non : toute la mémoire est publique":
        "no: the whole memory is public",
    "une mémoire privée se pose par l'installeur, en dépôt privé à côté ou chiffrée":
        "a private memory is set up by the installer, in a private repository alongside or encrypted",
    "La politique d'autonomie par défaut (les huit points du cadrage) te convient-elle ?":
        "Does the default autonomy policy (the eight rules of the brief) suit you?",
    "oui, telle quelle":
        "yes, as it is",
    "la politique dit ce que l'agent décide seul et ce qu'il te demande ; toi seul la modifies":
        "the policy says what the agent decides alone and what it asks you; only you change it",
    "Des contraintes à respecter (licence, dépendances, plateformes, délais) ?":
        "Any constraints to respect (licence, dependencies, platforms, deadlines)?",
    "aucune connue":
        "none known",
    "une contrainte devient un fait « supposé » jusqu'à ce que tu la valides":
        "a constraint becomes an “assumed” fact until you validate it",
    "{i}. **{question}** Défaut : {defaut}. Ce que ça change : {effet}.":
        "{i}. **{question}** Default: {defaut}. What it changes: {effet}.",
    "- Le document de cadrage, archivé tel quel sous `{cadrage}` : ce que le projet veut, d'où l'agent tire les "
    "faits « supposés » et le backlog de départ.":
        "- The brief, archived as is under `{cadrage}`: what the project wants, from which the agent draws the "
        "“assumed” facts and the starting backlog.",
    "- Le document de cadrage : [{nom}]({lien}).":
        "- The brief: [{nom}]({lien}).",
    "- Aucun élément de la mémoire : le projet commence, et ces questions en posent le départ.":
        "- No element of the memory: the project is starting, and these questions set its start.",
    "- Les instructions du projet : [{instr}]({lien}), section de la politique d'autonomie.":
        "- The project's instructions: [{instr}]({lien}), autonomy policy section.",
    "refus : le socle n'est pas installé ici (`socle install` d'abord)":
        "refused: the socle is not installed here (`socle install` first)",
    " et ":
        " and ",
    "un document de cadrage":
        "a brief",
    "un dépôt existant":
        "an existing repository",
    "rien du tout":
        "nothing at all",
    "initialisation depuis {entrees}":
        "initialization from {entrees}",
    "refus : avec une mémoire privée, le cadrage s'archive dans sa zone, indisponible ici ({raison}) ; la mettre en "
    "place d'abord":
        "refused: with a private memory, the brief is archived in its zone, unavailable here ({raison}); set it up "
        "first",
    "\n## {ident} — Document de cadrage archivé tel quel\n\n{meta} · empreinte : {emp}\n\nArchivé sans réécriture. "
    "Ce qu'il affirme entre dans la mémoire en « supposé », avec ce fichier pour source, jusqu'à validation "
    "humaine.\n":
        "\n## {ident} — Brief archived as is\n\n{meta} · fingerprint : {emp}\n\nArchived without rewriting. What it "
        "states enters the memory as “assumed”, with this file as its source, until a human validation.\n",
    "document archivé : {archive} ({empreinte}…), journal {ident}":
        "document archived: {archive} ({empreinte}…), journal {ident}",
    "audit d'initialisation":
        "initialization audit",
    "audit du dépôt en lecture seule : {n} fait(s) mesuré(s), chacun avec son fichier":
        "read-only audit of the repository: {n} measured fact(s), each with its file",
    "questions de départ : {ident}, {n} question(s), chacune avec son défaut":
        "starting questions: {ident}, {n} question(s), each with its default",
    "\nPour toi :":
        "\nFor you:",
    "commiter puis pousser : `git add -A && git commit -m \"Initialiser la mémoire\" && git push` (la demande "
    "{ident} doit être sur GitHub pour que tu puisses la lire)":
        "commit then push: `git add -A && git commit -m \"Initialize the memory\" && git push` (the request {ident} "
        "must be on GitHub for you to read it)",
    "ouvrir l'agent dans le projet : il relit les questions de départ et te les pose dans la conversation, avec leur "
    "lien":
        "open the agent in the project: it reads the starting questions again and asks them to you in the "
        "conversation, with their link",
    "y répondre dans la conversation, une ligne par question ou « défauts » : l'agent consigne ta réponse telle "
    "quelle":
        "answer them in the conversation, one line per question or “defaults”: the agent records your answer as is",
    "adaptateur inconnu : {nom} (maintenus : {connus} ; sinon un chemin vers un .toml)":
        "unknown adapter: {nom} (maintained: {connus}; otherwise a path to a .toml)",
    "balayage de mutation : `{autre}` le lance déjà, le socle n'en pose pas un second ; la CI vérifie qu'il tourne "
    "encore":
        "mutation sweep: `{autre}` already runs it, the socle does not add a second one; the CI checks that it still "
        "runs",
    "balayage de mutation hebdomadaire posé : {workflow}":
        "weekly mutation sweep installed: {workflow}",
    "politique du projet":
        "project policy",
    "gabarit de cette version":
        "template of this version",
    "{cible} n'est pas un dépôt git":
        "{cible} is not a git repository",
    "{cible} n'est pas la racine du dépôt git ({haut}) ; le socle s'installe à la racine":
        "{cible} is not the root of the git repository ({haut}); the socle is installed at the root",
    "moteur déjà en place dans {dossier_moteur}/socle (installeur lancé depuis le projet) : conservé ; pour une "
    "autre version, lancer l'installeur depuis le clone du socle":
        "engine already in place in {dossier_moteur}/socle (installer run from the project): kept; for another "
        "version, run the installer from the socle's clone",
    "moteur {version} copié dans {dossier_moteur}/socle":
        "engine {version} copied to {dossier_moteur}/socle",
    "# Verrou du moteur — écrit par l'installeur, jamais à la main.\n# Mode amont : ce dépôt fabrique le moteur, "
    "dont l'empreinte n'est pas figée ici.\n":
        "# Engine lock — written by the installer, never by hand.\n# Upstream mode: this repository builds the "
        "engine, whose fingerprint is not frozen here.\n",
    "verrou en mode amont : le moteur est la source, sous {dossier_moteur}/socle":
        "lock in upstream mode: the engine is the source, under {dossier_moteur}/socle",
    "# Verrou du moteur — écrit par l'installeur, jamais à la main.\n# La CI recalcule l'empreinte ; un moteur "
    "altéré dans le projet fait échouer `moteur.empreinte`.\n":
        "# Engine lock — written by the installer, never by hand.\n# The CI recomputes the fingerprint; an engine "
        "altered in the project fails `moteur.empreinte`.\n",
    "verrou : {empreinte} sur {n} fichiers":
        "lock: {empreinte} over {n} files",
    "mémoire privée ajoutée à la politique ({prive}) : un changement protégé, à approuver":
        "private memory added to the policy ({prive}): a protected change, to approve",
    "la politique du projet diffère du gabarit de cette version ; rien n'est écrit, elle est à l'humain — à relire "
    ":\n      {ecart}":
        "the project's policy differs from the template of this version; nothing is written, it belongs to the human "
        "— to review:\n      {ecart}",
    "{nom} existe : conservé (comparer au gabarit à la main si besoin)":
        "{nom} exists: kept (compare it with the template by hand if needed)",
    "{nom} posé":
        "{nom} installed",
    "mémoire initiale posée, journal ouvert par {ident}":
        "initial memory installed, journal opened by {ident}",
    "hooks git branchés (core.hooksPath)":
        "git hooks wired (core.hooksPath)",
    "!! core.hooksPath pointe ailleurs : hooks git NON branchés":
        "!! core.hooksPath points elsewhere: git hooks NOT wired",
    "refus : {refus}":
        "refused: {refus}",
    "refus : langage non détecté (aucun de Cargo.toml, pyproject.toml, go.mod, pom.xml, Gemfile, composer.json, "
    "package.json, ni fichier Python) : le demander à l'humain, puis `--adapter <{connus}>` ou le chemin d'un .toml":
        "refused: language not detected (none of Cargo.toml, pyproject.toml, go.mod, pom.xml, Gemfile, "
        "composer.json, package.json, nor a Python file): ask the human, then `--adapter <{connus}>` or the path of "
        "a .toml",
    "refus : adaptateur « {nom} » illisible : {erreur}":
        "refused: adapter “{nom}” unreadable: {erreur}",
    "adaptateur : {nom}":
        "adapter: {nom}",
    " (détecté)":
        " (detected)",
    "mise à jour : moteur {avant} → {version}":
        "update: engine {avant} → {version}",
    "socle {version} installé dans {cible}":
        "socle {version} installed in {cible}",
    "\nAudit :":
        "\nAudit:",
    "\nEt maintenant :":
        "\nWhat now:",
    "!! CLAUDE.md gardé : {n} fichier(s) du projet le nomment ({liste}) ; le renommer en AGENTS.md est une décision "
    "humaine — section du socle ajoutée à CLAUDE.md":
        "!! CLAUDE.md kept: {n} file(s) of the project name it ({liste}); renaming it to AGENTS.md is a human "
        "decision — socle section added to CLAUDE.md",
    "CLAUDE.md existant renommé en AGENTS.md (il fait foi désormais)":
        "existing CLAUDE.md renamed to AGENTS.md (it is now authoritative)",
    "# {nom}\n\nÀ compléter : ce que fait le projet, sa structure, ses commandes.\n\n":
        "# {nom}\n\nTo complete: what the project does, its structure, its commands.\n\n",
    "AGENTS.md posé":
        "AGENTS.md installed",
    "## Repris de CLAUDE.md\n\n{propre}\n\n":
        "## Taken from CLAUDE.md\n\n{propre}\n\n",
    "le contenu de CLAUDE.md, propre au projet, est repris dans AGENTS.md, qui fait foi ; CLAUDE.md n'importe plus "
    "qu'AGENTS.md":
        "the content of CLAUDE.md, specific to the project, is taken over into AGENTS.md, which is authoritative; "
        "CLAUDE.md now only imports AGENTS.md",
    "section du socle de {fichier} régénérée":
        "socle section of {fichier} regenerated",
    "section du socle ajoutée à {fichier}":
        "socle section added to {fichier}",
    "!! .claude/settings.json illisible : hooks NON déclarés":
        "!! .claude/settings.json unreadable: hooks NOT declared",
    "hooks de Claude Code déclarés dans .claude/settings.json":
        "Claude Code hooks declared in .claude/settings.json",
    "!! aucun propriétaire (--owner) : CODEOWNERS non posé — la politique n'est protégée que par la CI":
        "!! no owner (--owner): CODEOWNERS not installed — the policy is only protected by the CI",
    "CODEOWNERS : {proprietaire} sur la politique, les hooks et la CI":
        "CODEOWNERS: {proprietaire} on the policy, the hooks and the CI",
    "# Trace locale des hooks du socle":
        "# Local trace of the socle's hooks",
    "{commentaire} (voir {source})":
        "{commentaire} (see {source})",
    "# Le socle : ses fichiers se commitent":
        "# The socle: its files are committed",
    ".gitignore : {n} fichier(s) du socle n'y sont plus ignorés":
        ".gitignore: {n} socle file(s) no longer ignored there",
    "!! encore ignorés par le .gitignore du projet, un dossier parent sans doute : {liste} — à rendre à la main, "
    "sans quoi ils ne seront pas commités":
        "!! still ignored by the project's .gitignore, by a parent folder no doubt: {liste} — to restore by hand, "
        "otherwise they will not be committed",
    "# Le clone du dépôt privé (mémoire privée)":
        "# The clone of the private repository (private memory)",
    "mémoire privée (compagnon) : dépôt privé trouvé, verrou à {sha}":
        "private memory (compagnon): private repository found, lock at {sha}",
    "!! mémoire privée (compagnon) : dépôt privé absent — le mettre en place : `python3 .socle/socle private install "
    "--repo <adresse du dépôt privé>`":
        "!! private memory (compagnon): private repository missing — set it up: `python3 .socle/socle private "
        "install --repo <address of the private repository>`",
    "mémoire privée (chiffrée) : filtre « {filtre} » configuré":
        "private memory (encrypted): filter “{filtre}” configured",
    "!! mémoire privée (chiffrée) : filtre « {filtre} » non configuré ici — l'initialiser (`{filtre} init`, ou "
    "l'équivalent de l'outil) avant d'écrire du privé ; `prive.chiffre` refusera tout fichier privé commité en clair":
        "!! private memory (encrypted): filter “{filtre}” not configured here — initialize it (`{filtre} init`, or "
        "the tool's equivalent) before writing anything private; `prive.chiffre` will refuse any private file "
        "committed in clear",
    "budget de CLAUDE.md, gardé comme source : {taille} octets (il ne pourra que baisser)":
        "budget of CLAUDE.md, kept as a source: {taille} bytes (it can only go down)",
    "budget de {motif} fixé au niveau actuel : {nouveau} octets (il ne pourra que baisser)":
        "budget of {motif} set at the current level: {nouveau} bytes (it can only go down)",
    "# Contrôles en échec sur l'existant, passés en avertissement. En retirer un\n# durcit (libre) ; en ajouter un "
    "assouplit (demande validée).\n":
        "# Checks failing on the existing code, turned into warnings. Removing one\n# tightens (free); adding one "
        "loosens (approved request).\n",
    "adoption : {n} contrôle(s) en avertissement : {liste}":
        "adoption: {n} check(s) as warnings: {liste}",
    "approuver les fichiers protégés que la mise à jour a changés (la liste s'affiche, à confirmer) : `python3 "
    ".socle/socle approve --text \"Mise à jour du socle {version}\"`":
        "approve the protected files the update changed (the list is shown, to confirm): `python3 .socle/socle "
        "approve --text \"Socle update {version}\"`",
    "{n} contrôle(s) en échec ci-dessus ({liste}) : les corriger, ou relancer l'installation avec `--adoption`, qui "
    "les passe en avertissement sur l'existant":
        "{n} check(s) failing above ({liste}): fix them, or run the installation again with `--adoption`, which "
        "turns them into warnings on the existing code",
    "mettre en place le dépôt privé (créé vide sur GitHub, privé) : clone, premier commit, verrou (ce qui règle "
    "`prive.verrou`), clé de déploiement, puis les deux gestes sur GitHub, avec leurs liens : `python3 .socle/socle "
    "private install --repo <adresse du dépôt privé>`":
        "set up the private repository (created empty on GitHub, private): clone, first commit, lock (which settles "
        "`prive.verrou`), deploy key, then the two steps on GitHub, with their links: `python3 .socle/socle private "
        "install --repo <address of the private repository>`",
    "initialiser le filtre de chiffrement « {filtre} » (`{filtre} init`, ou l'équivalent de l'outil) avant d'écrire "
    "du privé":
        "initialize the encryption filter “{filtre}” (`{filtre} init`, or the tool's equivalent) before writing "
        "anything private",
    "décrire le projet à l'agent : `python3 .socle/socle init --brief <document> --repo` (sans document : `--repo` "
    "seul ; un dépôt vide : sans option)":
        "describe the project to the agent: `python3 .socle/socle init --brief <document> --repo` (without a "
        "document: `--repo` alone; an empty repository: no option)",
    "Mettre à jour le socle {version}":
        "Update the socle {version}",
    "Installer le socle {version}":
        "Install the socle {version}",
    "commiter puis pousser : `git add -A && git commit -m \"{message}\" && git push`":
        "commit then push: `git add -A && git commit -m \"{message}\" && git push`",
    "ouvrir l'agent dans le projet : il lit l'état au démarrage":
        "open the agent in the project: it reads the state at startup",
    "ouvrir l'agent dans le projet : il lit l'état au démarrage, et te pose les questions de départ dans la "
    "conversation":
        "open the agent in the project: it reads the state at startup, and asks you the starting questions in the "
        "conversation",
    "après ce premier push, protéger la branche par défaut : un ensemble de règles qui y exige la CI « {ci} » et la "
    "revue des propriétaires du code ({page}) ; sans lui, une CI rouge n'empêche pas de fusionner, et `socle state` "
    "le signale":
        "after this first push, protect the default branch: a ruleset that requires the CI “{ci}” and the code "
        "owners' review there ({page}); without it, a red CI does not prevent merging, and `socle state` reports it",
    "réglages du dépôt":
        "repository settings",
    "ensuite, tes gestes, chacun avec sa commande : `python3 .socle/socle help`":
        "then, your steps, each with its command: `python3 .socle/socle help`",
    "ECHEC":
        "FAILED",
    "indisponible":
        "unavailable",
    "ok (avertissement)":
        "ok (warning)",
    "  … et {n} autre(s) contrôle(s) sans rien à signaler":
        "  … and {n} other check(s) with nothing to report",
    "TOUT PASSE":
        "ALL PASS",
    "ECHEC — {n} contrôle(s) : {controles}":
        "FAILED — {n} check(s): {controles}",
}
