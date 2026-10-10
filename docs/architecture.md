# Architecture du socle

Ce document dit où chaque exigence du cadrage
(`memoire/archives/cadrage-2026-10-10.md`) est appliquée, et ce qui ne l'est
pas encore. La liste exacte des contrôles se dérive du code :
`python3 .socle/socle checks`.

## Les trois pièces

| Pièce | Où, dans un projet | Qui la modifie |
| --- | --- | --- |
| Moteur immuable | dans un projet, .socle/moteur/socle/ (ici, la source : `moteur/socle/`), lanceur `.socle/socle`, verrou `.socle/moteur.lock` | l'installeur seul ; la CI vérifie l'empreinte |
| Fichiers du projet | `memoire/`, `.socle/politique.toml`, `.socle/adaptateur.toml`, `.socle/garde-fous.toml` | le projet, selon la politique |
| Étages d'application | `.claude/settings.json`, `.socle/git-hooks/`, `.github/workflows/socle.yml`, `.github/CODEOWNERS` | l'installeur ; fichiers protégés |

Les trois étages appellent le même moteur : `python3 .socle/socle hook …`
pour l'agent et pour git, `python3 .socle/socle ci` pour la CI.

## Le moteur, module par module

| Module | Rôle |
| --- | --- |
| `cli.py` | les commandes : `state`, `show`, `check`, `verify`, `ci`, `hook`, `new`, `next-id`, `answer`, `approve`, `install`, `selftest`, `fingerprint`, `mutation-verdict`, `archive`, `checks` |
| `memoire.py` | lecture des cinq couches : en-têtes, entrées, identifiants, métadonnées, références |
| `demandes.py` | le contrat des demandes, son lint, les réponses humaines gelées |
| `contexte.py` | le registre des contrôles, leurs étages, la base de comparaison, le mode adoption |
| `controles_memoire.py` | format, références, fuite d'identifiants privés, preuves, backlog, budgets, péremption, retard, ajout seul, demandes, source unique des instructions |
| `controles_docs.py` | outillage documenté, valeurs liées, correspondance code ↔ doc, refus des copies |
| `controles_tests.py` | capacités de l'adaptateur, tests creux, valeurs attendues, régression rejouée sur le parent, couverture de mutation |
| `controles_cliquet.py` | cliquet des garde-fous, fichiers protégés, empreinte du moteur, configuration et trace des hooks |
| `tests_lecture.py` | extraction des fonctions de test selon l'adaptateur ; transitivité des assertions |
| `hooks.py` | les points d'entrée des hooks de l'agent et de git, la trace |
| `etat.py` | l'état dérivé |
| `humain.py` | ce qui revient à l'humain, et la lecture du dernier message de l'agent pour le récap |
| `verification.py` | le contrat `verify` : les capacités de l'adaptateur |
| `mutation.py` | le verdict de mutation contre les plafonds |
| `empreinte.py` | l'empreinte du moteur |
| `installeur.py` | installation, mise à jour, adoption |
| `autotest.py` | l'injection de défauts dans un projet jetable |
| `adaptateurs/` | Rust (extrait de chess) et Python, maintenus |
| `modeles/` | les gabarits posés par l'installeur |

## Exigences du cadrage et contrôles qui les appliquent

| Exigence | Contrôle ou mécanisme | Étages |
| --- | --- | --- |
| Format parsable, identifiants stables, statuts | `memoire.format` | agent, git, CI |
| Toute référence vérifiée, lien mort refusé | `memoire.references` | agent, git, CI |
| Fait mesuré avec preuve, réfuté barré, validé par l'humain | `memoire.preuves`, hook `pre-tool-use` | agent, git, CI |
| Backlog : origine, clôture avec référence | `memoire.backlog` | agent, git, CI |
| Budgets de taille | `memoire.budgets` | agent, git, CI |
| Péremption de l'actif (avertissement) | `memoire.peremption` | agent, git, CI |
| Journal et décisions en ajout seul ; fait jamais effacé | `memoire.ajout-seul` | agent, git, CI |
| Mémoire en retard sur le code : fin de tour refusée | `memoire.retard` | agent |
| Le privé ne fuit pas dans le public (identifiants) | `memoire.prive` | agent, git, CI |
| Contrat des demandes : huit champs (les sept du cadrage et « Où regarder », avec un lien vers chaque document à lire), contexte d'au moins soixante mots, aucun identifiant nu | `demandes.contrat`, hook `pre-tool-use` | agent, git, CI |
| Décision archivée avec le texte exact | `demandes.reponses` (empreinte de la demande) | agent, git, CI |
| `AGENTS.md` fait foi, `CLAUDE.md` l'importe | `instructions.source-unique` | agent, git, CI |
| Valeurs dupliquées liées à leur source | `docs.valeurs` | agent, git, CI |
| Outillage documenté | `docs.outillage` | agent, git, CI |
| Correspondance code ↔ doc, dispense motivée | `docs.correspondance` (pas au commit : le hook ne voit pas le message, donc pas la dispense) | agent, CI |
| Pas de copie | `docs.copie` | agent, git, CI |
| Capacité absente déclarée avec remplacement | `adaptateur.capacites` | agent, git, CI |
| Tests creux | `tests.creux` (sur le diff aux étages agent et git) | agent, git, CI |
| Test supprimé, valeur attendue changée | `tests.attendus` | agent, git, CI |
| Correctif avec test de régression rejoué sur le parent | `tests.regression` | CI |
| Mutation : plafond par module, cliquet | `mutation.couverture`, `socle mutation-verdict` | agent, git, CI ; verdict hebdomadaire |
| Rien ne s'affaiblit en silence | `cliquet.garde-fous`, `protege.fichiers` | agent, git, CI |
| Moteur et politique non altérés | `moteur.empreinte`, `protege.fichiers` | agent, git, CI |
| Hooks chargés et déclenchés | `hooks.configuration`, `hooks.trace` (trailer `Socle-Hooks`) | CI |
| Action irréversible ou externe refusée | hook `pre-tool-use` | agent |
| Anti-fabrication | hook `pre-tool-use` : SHA complété de tête, identifiant ou commit inventé | agent |
| Échec répété : arrêt et escalade | hook `stop`, `max_attempts` de la politique | agent |
| État dérivé au démarrage et après compactage, avec l'index des décisions | `socle state`, hook `session-start` ; `socle show <ID>` pour lire une entrée à la demande | agent |
| Ce qui revient à l'humain et la suite, dits à chaque fin d'intervention qui a agi (lignes « Pour toi : » et « Ensuite : ») | `humain.py` (demandes en attente, backlog `pour : humain`, branches distantes supprimables, prochaines étapes du chantier actif), hook `stop` | agent |
| Lire avant de décider, prouvé par l'empreinte de la version lue | `memoire.lectures` ; hook `pre-tool-use` (empreinte périmée ou inventée) ; `socle show`, `socle new` | agent, git, CI |
| Auto-tests par injection de défauts | `socle selftest`, dans `socle ci` | CI |

## Les choix qui ne sont pas dans le cadrage

- **Une validation humaine est une réponse ajoutée dans la plage, qui cite ce
  qu'elle valide** (`ADR-0004`) : la clé assouplie, le nom du test, ou le
  chemin et l'empreinte du fichier protégé. **L'humain répond dans la
  conversation**, et l'agent consigne la réponse avec sa citation exacte
  (`ADR-0006`).
- **La trace des hooks voyage dans les commits** (`ADR-0005`).
- **Le cliquet compare la base et la tête clé par clé**, avec un sens par
  clé : plus bas est plus strict pour un budget, plus long pour une
  couverture, plus court pour une liste d'exclusions. Une clé inconnue qui
  change est un assouplissement jusqu'à preuve du contraire.
- **Lecture prouvée** (`ADR-0008`) : une entrée citée `ID@empreinte` l'a été
  dans cette version ; une décision, une demande ou un sujet de backlog
  nouveaux doivent le faire. La preuve porte sur l'accès au texte, pas sur
  sa compréhension.
- **Mode adoption** : à l'installation sur un projet existant, les budgets
  sont fixés au niveau actuel et les contrôles en échec passent en
  avertissement (`[adoption] warn_only`), liste dont on ne retire que pour
  durcir.
- **Une tautologie voulue passe avec sa raison écrite** (`socle: voulu —`),
  validé par Théo (`D-0004`).

## Ce qui n'est pas fait

Le backlog le tient : jalons 6 à 9, mémoire privée, empreinte comparée à la
version publiée, workflow de mutation générique, hook pre-commit sur l'index
plutôt que sur l'arbre. Les limites connues des contrôles y sont aussi :
chemins qui n'existent que dans une rustine, copie non marquée d'une valeur
qui n'est qu'un avertissement.
