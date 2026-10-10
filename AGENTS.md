# memory — le socle de mémoire, documentation et tests pour agents de code

Ce dépôt fabrique le **socle** : un moteur Python, bibliothèque standard
seule, qui rend fiables la mémoire, la documentation et les tests d'un projet
de code entretenu par un agent. L'agent écrit, des contrôles automatiques
attrapent les erreurs, et l'humain n'arbitre que ce qu'aucun contrôle ne peut
trancher. Le cadrage fondateur est archivé tel quel dans
`memoire/archives/cadrage-2026-10-10.md` ; ce qui vient du dépôt `chess` est
inventorié dans `docs/inventaire-chess.md`, et `docs/architecture.md` dit où
chaque exigence du cadrage est appliquée.

Ce dépôt est en **mode amont** : il est le premier utilisateur du socle qu'il
fabrique. Le moteur vit dans `moteur/socle/` ; il est la source, donc son
empreinte n'est pas figée ici. Les fichiers du projet vivent dans `.socle/`
comme dans n'importe quel projet.

## Structure

- `moteur/socle/` — le moteur : lecture de la mémoire, contrôles, hooks,
  installeur, auto-test. `moteur/socle/FORMAT.md` fait foi pour le format de
  la mémoire.
- `moteur/socle/adaptateurs/` — les adaptateurs maintenus (Rust, Python).
- `moteur/socle/modeles/` — les gabarits que l'installeur pose dans un projet.
- `tests/` — les tests du moteur (`unittest`), dont l'auto-test complet par
  injection de défauts.
- `docs/` — l'architecture et l'inventaire de `chess`.
- `memoire/` — la mémoire de ce projet, au format du socle.

## Commandes

```sh
python3 .socle/socle verify --rapide     # compilation, tests, contrôles
python3 .socle/socle ci                  # tout, dont l'auto-test
python3 .socle/socle selftest --verbose  # les défauts injectés, un par un
python3 .socle/socle install --target ../projet --adapter rust --owner @moi
```

## Règles propres à ce dépôt

- **Tout contrôle nouveau a son défaut injecté** dans `moteur/socle/autotest.py`,
  et un témoin sain qui passe : un garde-fou qu'on n'a jamais vu échouer ne
  prouve rien. L'auto-test a trouvé cinq contrôles muets à sa première
  exécution (`J-2026-10-10-E`).
- **Le moteur ne connaît ni langage ni agent** : ce qui dépend du langage va
  dans un adaptateur, ce qui dépend de l'agent dans les hooks.
- **Bibliothèque standard de Python 3.11+ seulement** (`ADR-0001`), vérifié
  par `tests/test_moteur.py`.
- **Commentaires, messages et documentation en français, identifiants en
  anglais** (`ADR-0002`).

<!-- socle:debut — section posée par l'installeur, régénérée à chaque mise à jour -->

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
réponse de l'humain). Format complet : `moteur/socle/FORMAT.md`.
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
Le lint refuse une demande incomplète. L'humain répond par
`python3 .socle/socle answer D-NNNN <réponse>` ; une demande répondue est gelée.

### Avant de conclure

- `python3 .socle/socle verify --rapide` passe (le hook `Stop` le vérifie) ; `verify` exécute tout.
- Si du code a changé, la mémoire aussi : chantier actif, journal, backlog.
- Si du code associé à une doc a changé (`[[docmap]]` des garde-fous), la doc change dans le même travail, ou un commit porte le trailer `Dispense-doc: <raison>`.
- Un correctif (sujet `fix:` ou trailer `Corrige: B-NNNN`) livre un test qui échoue sur le commit parent.

### Ne jamais

- compléter un SHA de tête, inventer un identifiant ou une référence : le hook les refuse ;
- écrire dans un fichier protégé (politique, adaptateur, verrou du moteur, hooks, CI, réponses humaines) ;
- lancer `socle answer` ou `socle approve`, réservés à l'humain ;
- contourner un hook (`--no-verify`) : la CI exécute tout, et rien ne la contourne.

### Ce qui tourne tout seul

| Où | Quoi |
| --- | --- |
| `.claude/settings.json` | hooks de Claude Code : `SessionStart` (état dérivé), `PreToolUse` (refus), `Stop` (contrôles de fin de tour) |
| `.socle/git-hooks/` | hooks git : `pre-commit` (contrôles rapides), `prepare-commit-msg` (trailer `Socle-Hooks`), `pre-push` (`verify --rapide`) |
| `.github/workflows/socle.yml` | CI : capacités de l'adaptateur, tous les contrôles contre la base, auto-test du socle |
| `.socle/trace/hooks.log` | trace locale de chaque hook qui tire, non versionnée |

Liste des contrôles : `python3 .socle/socle checks`.

<!-- socle:fin -->
