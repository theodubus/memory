# Format de la mémoire

La mémoire est un ensemble de fichiers markdown en cinq couches, plus la file
des demandes humaines. Un script sait la lire : sans cela, aucun contrôle
automatique ne serait possible. Ce document fait foi pour le format ; le code
qui le lit est `socle/memoire.py`, les contrôles sont listés par
`python3 .socle/socle checks`.

## Emplacements

```text
memoire/
  canonique.md            faits vérifiés, avec statut et preuve
  actif.md                chantier en cours, prochaines étapes
  backlog.md              sujets à traiter, avec statut et origine
  decisions/ADR-0001-*.md une décision par fichier
  journal/2026-10.md      un fichier par mois, une entrée par événement
  demandes/D-0001-*.md    une demande de décision humaine par fichier
  demandes/D-0001-*.reponse.toml   la réponse de l'humain, et elle seule
  archives/               documents archivés tels quels (cadrage…), non lus par les contrôles
  prive/                  zone privée, même arborescence (voir « La zone privée »)
```

## En-tête

La première ligne non vide de chaque fichier déclare sa couche et sa zone.
L'emplacement impose la couche ; la zone est celle de l'emplacement
(`publique` sous `memoire/`, `privee` sous `memoire/prive/`).

```markdown
<!-- socle: couche=canonique zone=publique -->
```

## Entrées

Une entrée est un titre qui commence par son identifiant, suivi d'une ligne
de métadonnées (une ou plusieurs lignes `>` consécutives), puis d'un corps
libre qui court jusqu'au titre suivant de même niveau ou de niveau supérieur.

```markdown
## F-0007 — Le bench à profondeur 7 explore 70 452 nœuds

> statut : mesuré · preuve : cmd:`cargo run --release -- bench 7` · date : 2026-10-10

Mesuré sur le binaire de base ; le chiffre change avec l'arbre de recherche.
```

Les métadonnées sont des paires `clé : valeur` séparées par un point médian
(`·`). Les clés s'écrivent sans souci des accents ni des majuscules
(`Réfutation` et `refutation` se valent).

### Identifiants

| Couche | Forme | Exemple |
| --- | --- | --- |
| Canonique | `F-` et quatre chiffres | `F-0007` |
| Backlog | `B-` et quatre chiffres | `B-0012` |
| Décisions | `ADR-` et quatre chiffres | `ADR-0003` |
| Demandes | `D-` et quatre chiffres | `D-0004` |
| Journal | `J-` date et lettre | `J-2026-10-10-A` |

Dans la zone privée, l'identifiant prend un `P` devant (`PF-0001`,
`PJ-2026-10-10-A`) : un fichier public qui en cite un est une fuite, et le
contrôle la voit même sans accès à la zone privée. Un identifiant se calcule
(`socle next-id`, `socle new`), il ne se devine pas. Il est défini une seule
fois ; toute mention ailleurs doit mener à une définition.

### Références

Une valeur de métadonnée, ou le texte, peut citer :

| Forme | Vérifiée en CI |
| --- | --- |
| `commit:3f2a9c1` | l'objet existe dans le dépôt (historique complet) |
| `fichier:src/x.rs`, `fichier:src/x.rs:12`, `fichier:doc.md#ancre` | le chemin existe |
| ``cmd:`cargo test, puis bench` `` ou `cmd:tools/verify.sh` | le script existe s'il est un chemin du dépôt |
| `url:https://…` | jamais suivie : aucun service externe |
| `F-0007`, `J-2026-10-10-A`… | l'entrée existe |

Les liens markdown relatifs et leurs ancres, et les chemins du dépôt cités
entre accents graves, sont vérifiés aussi. Un bloc de code clôturé porte des
exemples : rien n'y est vérifié.

## Couches

### Canonique — `F-`

| Statut | Exigence |
| --- | --- |
| `mesuré` | `preuve` : commit, fichier, commande ou entrée qui la porte |
| `supposé` | rien ; `source` dit d'où vient le fait |
| `réfuté` | titre barré `~~…~~`, corps conservé, `refutation` vers la mesure |
| `validé` | `validation : D-NNNN`, une demande à laquelle l'humain a répondu `valider` |

Un fait ne s'efface pas : il se barre, ou s'archive dans le journal (voir
plus bas). Modifié, il porte une référence de preuve qu'il n'avait pas.

### Actif

Réécrit librement, borné par son budget. Il ne définit aucun identifiant :
un identifiant est stable, l'actif ne l'est pas. Il renvoie aux entrées du
backlog et du journal.

### Décisions — `ADR-`

Un fichier par décision, nommé d'après son identifiant. Statuts : `proposée`,
`acceptée`, `rejetée`, `abandonnée`, `remplacée` (avec
`remplacée-par : ADR-NNNN`). Ajout seul : seuls le statut et ses métadonnées
changent ensuite, selon les passages proposée → acceptée, rejetée ou
abandonnée, et acceptée → remplacée ou abandonnée.

### Journal — `J-`

Un fichier par mois (`AAAA-MM.md`), une entrée par événement, datée par son
identifiant. Ajout seul : une entrée publiée ne change plus, sauf pour
recevoir à sa suite une archive.

### Backlog — `B-`

Statuts : `ouvert`, `en-cours`, `bloqué`, `fait`, `abandonné`. Toute entrée
a une `origine` (entrée de journal, commit, demande) ; une entrée close
(`fait`, `abandonné`) a une `ref` vers ce qui l'a close. Une action que seul
l'humain peut faire porte `pour : humain` : elle figure dans « ce qui revient
à l'humain », dans l'état et dans le récap de fin d'intervention, jusqu'à ce
qu'elle soit close. `socle archive`
déplace les entrées closes dans une entrée de journal datée, en sous-titres :

```markdown
## J-2026-10-12-A — Backlog clos archivé

### B-0003 — Corriger le lien mort du README

> statut : fait · origine : J-2026-10-10-A · ref : commit:3f2a9c1
```

Un sujet ou un fait archivé reste défini, donc toute référence vers lui
reste vivante.

### Demandes — `D-`

Un fichier par demande, titre `# D-NNNN — <la décision, en une phrase>`, et
huit sections de niveau deux : `Décision demandée`, `Contexte`, `Éléments
cités`, `Où regarder`, `Options`, `Conséquences`, `Recommandation`,
`Réponses possibles`. Les sept champs du cadrage, plus « Où regarder »,
ajouté après qu'une première série de demandes, conformes au lint, s'est
révélée impossible à trancher pour l'humain.

- « Contexte » raconte, en au moins soixante mots : la tâche, ce qui a
  déclenché la question, et le problème lui-même — un extrait de code, la
  règle en cause. Si la décision porte sur un contenu (un inventaire, un
  format), elle le résume sur place.
- « Où regarder » donne un lien (relatif ou URL) vers chaque document ou
  passage à lire pour décider, et dit ce qu'il faut y vérifier.

- « Éléments cités » décrit en clair, en au moins cinq mots, chaque
  identifiant interne de la demande (identifiants de mémoire, SHA, numéros de
  PR, et les motifs que le projet déclare) : `- B-0012 — le lien mort du
  README signalé par la CI`.
- « Options » dit l'effort, le risque et la réversibilité ; « Conséquences »
  ce qui se passe si l'humain valide, refuse, ne répond pas ;
  « Recommandation » sépare le vérifié du supposé.
- « Réponses possibles » est une liste `` - `valeur` — sens `` qui propose
  `contexte-insuffisant`.

La réponse vit dans `<demande>.reponse.toml`. L'humain répond dans la
conversation, et l'agent consigne sa réponse avec le texte exact
(`socle answer D-NNNN <réponse> --relayed --by <nom> --quote-file <fichier>`,
`canal = "conversation"`) ; ou l'humain la lance lui-même au terminal
(`canal = "terminal"`). L'agent ne choisit jamais la réponse : il relaie
celle que l'humain a écrite, citation à l'appui.

```toml
reponse = "valider"
texte = "ok, mais garder l'ancien plafond une semaine"
par = "Théo"
date = "2026-10-11"
canal = "conversation"
citation = "ok pour 5, mais garde l'ancien plafond une semaine"   # texte exact de l'humain
empreinte = "sha256:…"   # le texte exact de la demande au moment de la réponse
```

L'état de la demande se dérive de la réponse : en attente, répondue, renvoyée
(`contexte-insuffisant` : l'agent la réécrit en une nouvelle demande),
retirée (métadonnée `retirée : <raison>`). Une demande répondue est gelée.

## La zone privée

Une mémoire privée est une option, choisie par l'humain dans la politique
(`[private] mode`). Elle vit sous `memoire/prive/`, avec la même
arborescence, les mêmes formats, statuts et contrôles, et les mêmes budgets
de taille que la zone publique ; ses identifiants prennent un `P` devant.
Le privé peut citer le public, jamais l'inverse.

| Mode | Où vit la mémoire privée | Ce que le moteur vérifie |
| --- | --- | --- |
| `compagnon` | le clone d'un dépôt privé dans `memoire/prive/`, que le dépôt public ignore | aucun fichier privé n'est commité dans le dépôt public ; le verrou `.socle/prive.lock` désigne le commit du dépôt privé qui va avec chaque commit public ; rien de privé ne reste hors commit |
| `chiffre` | dans le dépôt public, chiffrée par un filtre git (git-crypt ou équivalent) | aucun fichier privé n'est commité en clair ; un filtre couvre `memoire/prive/` dans `.gitattributes` |

Le moteur ne connaît pas l'outil de chiffrement : un fichier privé est
lisible quand sa première ligne porte l'en-tête du socle, chiffré sinon.

**Indisponible.** Sans le clone du dépôt privé, ou sans la clé, la mémoire
privée est indisponible : l'état dérivé l'écrit au démarrage, et les
contrôles qui en dépendent le signalent, sans passer en silence. Un fichier
privé chiffré ici compte pour absent : il n'est ni lu ni jugé.

**Le verrou** (mode compagnon) s'écrit par `socle prive verrouiller`, une
fois les changements privés commités dans le dépôt privé ;
`socle prive extraire` remet la mémoire privée au commit du verrou, après un
retour à un ancien commit du code. En CI, `socle prive recuperer` la clone au
verrou avec les secrets `SOCLE_PRIVE_DEPOT` et `SOCLE_PRIVE_CLE`.

**En CI**, le journal d'un dépôt public est public : un constat de la zone
privée n'y montre ni son texte ni son chemin.

**Le contenu nouveau est privé par défaut** quand une mémoire privée existe :
`socle new` l'écrit sous `memoire/prive/`, sauf `--public`. Les demandes
font exception : elles ne sont privées, réponses comprises, que si l'humain
l'a choisi (`[private] requests = true`), car il doit pouvoir les lire là où
il lit ; en mode chiffré, GitHub n'en montre que le chiffré, et l'agent les
donne en entier dans la conversation.

**La liste des termes privés** (`memoire/prive/termes.txt`) nomme ce qui ne
doit jamais paraître en public : un terme par ligne, `#` pour un
commentaire, `re:` devant une expression régulière ; la recherche ignore la
casse et les accents et ne prend que des mots entiers. Sa première ligne
est `# socle: termes privés`. L'agent y ajoute librement
(`socle prive terme <terme>`) ; en retirer un exige une demande validée qui
cite la liste et son empreinte nouvelle. Un terme trouvé n'est jamais
réécrit, seulement désigné par son rang dans la liste.

**Les fuites** se cherchent à trois étages : le hook de l'agent (écritures
hors de la zone privée, messages de commit, pull requests et commentaires),
le hook git du message de commit, et la CI (fichiers publics modifiés,
messages des commits).

**La relecture avant publication** se règle par projet
(`[private] review`) : `aucune`, `chaque-push` ou `lots`. Avec les deux
dernières, un push vers le dépôt public attend que l'humain ait relu le
commit qui part : il le dit (`socle relu`), ou l'agent relaie son accord
donné dans la conversation, avec son texte exact
(`socle relu --relayed --by <nom> --quote-file <fichier>`).

## Lecture prouvée

Chaque entrée a une empreinte, les huit premiers caractères du SHA-256 de
son texte ; chaque index aussi (`decisions@…` pour toutes les décisions,
`backlog@…` pour le backlog ouvert). `socle show <ID>` et
`socle show --index decisions|backlog` les impriment avec le texte.

Citer `ADR-NNNN@xxxxxxxx`, c'est montrer qu'on a lu cette version-là. Une
citation ajoutée doit désigner la version actuelle de l'entrée, ou de l'index
tel qu'il était au début du travail ; sinon elle est périmée ou inventée, et
refusée. Elle est obligatoire :

- dans une décision nouvelle : `lu : decisions@…`, et chaque entrée citée
  avec son empreinte ;
- dans une demande nouvelle : chaque entrée citée avec son empreinte ;
- dans un sujet de backlog nouveau : `lu : backlog@…`.

`socle new adr` et `socle new backlog` affichent l'index concerné et posent
son empreinte dans le squelette. Une citation ancienne n'est pas revérifiée
quand l'entrée change ensuite : elle dit ce qui a été lu à l'époque.

## Ordre d'autorité

En cas de conflit : le code et les tests, puis la mémoire canonique, puis le
journal.
