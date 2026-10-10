@@SECTION_PROJET@@

## Socle : mémoire, documentation et tests

Ce dépôt utilise le socle (version et empreinte : `.socle/moteur.lock`).
Ce fichier dit **comment** travailler ;
**où en est le projet** se calcule, et ne s'écrit jamais à la main.

### Au démarrage, et après chaque compactage

`python3 .socle/socle state` imprime l'état dérivé — commit, base, CI,
backlog, demandes humaines en attente —, puis le chantier actif et la mémoire
canonique. Sous Claude Code, le hook `SessionStart` le fait seul ; sous un
autre agent, le lancer d'abord. Rien de ce qui n'y figure pas n'est acquis.

### La mémoire, dans `memoire/`

| Couche | Où | Règle |
| --- | --- | --- |
| Canonique | `memoire/canonique.md` | faits avec statut et preuve ; ne change qu'avec une preuve nouvelle |
| Actif | `memoire/actif.md` | chantier en cours, prochaines étapes ; réécrit, borné |
| Décisions | `memoire/decisions/` | une ADR par fichier ; seul son statut change ensuite |
| Journal | `memoire/journal/` | une entrée datée par événement ; ajout seul |
| Backlog | `memoire/backlog.md` | sujets avec statut et origine ; clos avec une référence |
| Demandes | `memoire/demandes/` | décisions humaines en file, au contrat ci-dessous |

Une entrée : `## F-NNNN — titre`, puis une ligne `> statut : mesuré · preuve : commit:<sha>`.
Statuts d'un fait : `mesuré` (avec `preuve`), `supposé`, `réfuté` (titre barré,
avec `refutation`), `validé` (avec `validation : D-NNNN`, écrit après la
réponse de l'humain). Format complet : `@@MOTEUR@@/socle/FORMAT.md`.
Un identifiant se calcule (`python3 .socle/socle new <type> "titre"`), il ne
se devine pas. En cas de conflit, l'ordre d'autorité est : le code et les
tests, puis la mémoire canonique, puis le journal.

### Politique d'autonomie (`.socle/politique.toml`, modifiée par l'humain seul)

1. **Assouplir un garde-fou** (`.socle/garde-fous.toml`) exige une demande validée ; durcir est libre.
2. **Supprimer un test ou changer une valeur attendue** exige une spécification changée qui nomme le test, ou une demande validée.
3. **Décision de conception** : réversible et mesurable, l'agent décide et écrit une ADR ; coûteuse à défaire, demande.
4. **Action irréversible ou externe** (force-push, push sur la branche par défaut, publication, suppression distante, dépense) : toujours une demande. Le hook la refuse.
5. **Mémoire** : ajout seul ; « réfuté » exige une référence de mesure ; « validé » ne s'écrit qu'après la réponse de l'humain.
6. **Débordement de périmètre** : un bug voisin va au backlog, il ne se corrige pas, sauf s'il bloque.
7. **Échec répété** : contrôles rouges après trois tentatives, arrêt et escalade par une demande qui résume.
8. **Validation requise** : mettre la demande en file, travailler sur autre chose, ne jamais deviner.

### Demandes de décision humaine

Une demande est lue quand le contexte est perdu : elle se suffit à elle-même.
`python3 .socle/socle new request "<décision>"` pose le squelette des huit
champs : décision demandée, contexte (le problème lui-même, résumé sur place,
pas un renvoi), éléments cités (chacun décrit en clair, jamais un identifiant
seul), où regarder (un lien vers chaque document à lire, et quoi y vérifier),
options (effort, risque, réversibilité),
conséquences (si l'humain valide, refuse, ne répond pas), recommandation
(vérifié séparé du supposé), réponses possibles dont `contexte-insuffisant`.
Le lint refuse une demande incomplète. L'humain répond dans la conversation ;
l'agent consigne sa réponse, sans jamais la choisir, avec le texte exact :
`python3 .socle/socle answer D-NNNN <réponse> --relayed --by <nom> --quote-file <fichier>`,
et la recopie au journal. Une demande répondue est gelée.

### Lire la mémoire à la demande

Le démarrage n'injecte que l'état, le chantier actif et les faits. Le reste
se lit quand il sert, sans attendre qu'on le demande :

- un identifiant cité (`F-`, `B-`, `ADR-`, `D-`, `J-`) se lit avant de
  s'appuyer dessus : `python3 .socle/socle show <ID>`, qui donne aussi son
  empreinte ;
- avant une décision de conception, l'index des décisions de l'état dit si
  elle est déjà prise : on ne la rouvre pas sans fait nouveau ;
- avant d'ouvrir un sujet, le backlog (`socle show --index backlog`) dit
  s'il existe déjà ;
- pour savoir pourquoi une chose est ainsi, chercher dans le journal
  (`grep -rn "<mot>" memoire/journal/`).

La lecture se prouve : une décision, une demande ou un sujet de backlog
nouveaux citent ce qu'ils ont lu avec son empreinte (`ADR-NNNN@xxxxxxxx`,
`lu : decisions@…`, `lu : backlog@…`). Une empreinte périmée ou inventée est
refusée ; il faut relire l'entrée. `socle new` pose l'empreinte de l'index.

### Avant de conclure

- `python3 .socle/socle verify --rapide` passe (le hook `Stop` le vérifie) ; `verify` exécute tout.
- Si du code a changé, la mémoire aussi : chantier actif, journal, backlog.
- Si du code associé à une doc a changé (`[[docmap]]` des garde-fous), la doc change dans le même travail, ou un commit porte le trailer `Dispense-doc: <raison>`.
- Un correctif (sujet `fix:` ou trailer `Corrige: B-NNNN`) livre un test qui échoue sur le commit parent.
- Une action que seul l'humain peut faire (refusée par le hook, réglage d'un service, fichier qu'il détient) va au backlog avec `pour : humain`.
- **Toute intervention qui a agi se termine par un récap, puis deux lignes** : `Pour toi :` — ce qui revient à l'humain, décisions en attente et actions à faire, ou « rien » —, et `Ensuite :` — la suite proposée (prochain jalon, ce qu'il reste à faire avant), et ce que l'agent attend s'il attend quelque chose (une CI, un match : quoi, et jusqu'à quand). L'état calcule ce qui revient à l'humain ; le hook `Stop` refuse de conclure sans les deux lignes.
- **Un fichier à lire se donne par son lien** : l'humain lit dans la conversation ou sur GitHub, pas dans le conteneur de l'agent. `python3 .socle/socle url <chemin|ID>` donne le permalien, une fois le fichier poussé ; une demande en attente citée sans son lien, un lien relatif, ou un chemin entre accents graves qui n'existe pas dans le dépôt font refuser la fin du tour. Un chemin d'un autre dépôt s'écrit `depot:chemin`.

### Ne jamais

- compléter un SHA de tête, inventer un identifiant ou une référence : le hook les refuse ;
- écrire dans un fichier protégé (politique, adaptateur, verrou du moteur, hooks, CI, réponses humaines) ;
- répondre à la place de l'humain (`socle answer` sans `--relayed` ni citation), ou lancer `socle approve`, réservé à l'humain ;
- contourner un hook (`--no-verify`) : la CI exécute tout, et rien ne la contourne.

### Ce qui tourne tout seul

| Où | Quoi |
| --- | --- |
| `.claude/settings.json` | hooks de Claude Code : `SessionStart` (état dérivé), `PreToolUse` (refus), `Stop` (contrôles de fin de tour) |
| `.socle/git-hooks/` | hooks git : `pre-commit` (contrôles rapides), `prepare-commit-msg` (trailer `Socle-Hooks`), `pre-push` (`verify --rapide`) |
| `.github/workflows/socle.yml` | CI : capacités de l'adaptateur, tous les contrôles contre la base, auto-test du socle |
| `.git/socle/hooks.log` | trace locale de chaque hook qui tire, non versionnée, commune à tous les worktrees du dépôt |

Liste des contrôles : `python3 .socle/socle checks`.
