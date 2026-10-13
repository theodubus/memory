<!-- socle: couche=backlog zone=publique -->
# Backlog

Les sujets à traiter. Chacun a un statut (ouvert, en cours, bloqué, fait,
abandonné) et une origine ; un sujet clos porte la référence de ce qui l'a
clos, puis s'archive dans le journal (`python3 .socle/socle archive`).

## B-0005 — Workflow de mutation hebdomadaire générique, et alerte quand il cesse de tourner

> statut : ouvert · origine : J-2026-10-10-D

Le verdict existe (`socle mutation-verdict`) ; manquent le gabarit de
workflow planifié et l'équivalent de `chess:tools/balayage-vivant.sh`, qui
voit un cliquet endormi par GitHub.

## B-0006 — Vérifier l'empreinte du moteur contre la version publiée en amont

> statut : ouvert · origine : fichier:memoire/archives/cadrage-2026-10-10.md

Aujourd'hui, la CI compare le moteur au verrou local. Le cadrage demande la
comparaison avec la version publiée, que le verrou seul ne garantit pas si
moteur et verrou changent ensemble.

## B-0008 — Les chemins qui n'existent que dans une rustine sont pris pour des liens morts

> statut : ouvert · origine : J-2026-10-10-F

25 cas sur chess, tous des lecteurs de sondes contenus dans les rustines de
l'attic. Une notation pour « chemin dans une rustine », ou une exclusion
déclarée par le projet.

## B-0009 — Adoption : importer l'existant que le socle sait lire

> statut : ouvert · origine : J-2026-10-10-F

Les plafonds de mutation de chess ont été repris à la main
(`docs/chess/mutation-caps.toml`). L'adoption pourrait proposer cette
reprise, et celle des tables « Ce qui tourne tout seul ».

## B-0010 — Calibrer les budgets de taille et de jetons du démarrage

> statut : ouvert · origine : fichier:memoire/archives/cadrage-2026-10-10.md

Question ouverte du cadrage. Les valeurs par défaut des garde-fous sont des
hypothèses ; chess donne un point de mesure (F-0005).

## B-0011 — Audit périodique de l'adaptateur

> statut : ouvert · origine : fichier:memoire/archives/cadrage-2026-10-10.md

Détecter un outil ou un langage nouveau dans le projet et émettre une
demande. Fréquence à décider (question ouverte du cadrage).

## B-0012 — Une copie non marquée d'une valeur liée n'est qu'un avertissement

> statut : ouvert · origine : J-2026-10-10-E

`docs.valeurs` refuse une valeur marquée fausse, mais ne fait qu'avertir sur
une copie non marquée de la valeur courante : elle pourrait être une
coïncidence. Mesurer les faux positifs avant de durcir.

## B-0016 — La docstring de memoire.py renvoie à un document de format qui n'existe pas

> statut : ouvert · origine : fichier:moteur/socle/memoire.py · lu : backlog@ad031cf1

Vu en écrivant le module des liens : la docstring du lecteur de la mémoire
dit que le format est décrit dans un document de `docs/` qui n'existe pas ;
c'est `moteur/socle/FORMAT.md` qui fait foi. Aucun contrôle ne lit les
chemins cités dans les docstrings du code.

## B-0017 — Deux fonctions calculent l'ancre GitHub d'un titre

> statut : ouvert · origine : J-2026-10-10-V · lu : backlog@5630c7c0

`liens.ancre`, écrite pour les permaliens, refait ce que fait déjà `slug`
dans `controles_memoire.py`, qui vérifie les ancres des liens de la mémoire.
Deux copies divergeront : n'en garder qu'une, que les deux modules
appellent.

## B-0018 — Le hook refuse un push vers la branche par défaut d'un dépôt local jetable

> statut : ouvert · origine : J-2026-10-10-W · lu : backlog@85e18aaf

Au jalon 6, le hook de l'agent a refusé `git push origin main` vers le
dépôt d'origine d'un projet jetable, un simple dossier local : la
politique (point 4) vise une publication, qu'un dépôt local n'est pas.
Ne refuser que si la destination est distante, ou garder le refus et le
dire dans sa raison ; à arbitrer, le refus large est le plus sûr.

## B-0020 — Une référence suivie d'un point ou d'une parenthèse est lue avec eux

> statut : ouvert · origine : J-2026-10-11-D · lu : backlog@c360de10

`memoire.references` lit une référence de commit suivie d'une parenthèse
fermante ou d'un point final avec cette ponctuation, et refuse un SHA
pourtant valide. Deux fois déjà, l'agent a dû
reformuler sa phrase. La fin d'une référence devrait exclure la ponctuation
finale, comme le font les liens Markdown.

## B-0021 — Une preuve de lecture recopiée d'une autre entrée du même fichier passe

> statut : ouvert · origine : J-2026-10-11-D · lu : backlog@8003fd30

Vu en corrigeant l'archivage : `memoire.lectures` ignore une citation déjà
présente dans la version de base du même fichier. Un sujet de backlog
nouveau qui recopie le `lu : backlog@…` d'un autre sujet passe donc, sans
avoir rien lu. Juger la citation par entrée plutôt que par fichier, comme
le fait désormais l'exemption des entrées déplacées.

## B-0023 — Le hook de l'agent ne refuse pas --no-verify

> statut : ouvert · origine : J-2026-10-11-F · lu : backlog@35c34ebe

Au banc (s8), l'humain autorise `--no-verify` si un hook bloque. Les trois
agents ont refusé d'eux-mêmes, par les règles ; le hook ne l'aurait pas
fait, et seule la CI aurait arrêté le commit. Refuser `git commit
--no-verify` et `git push --no-verify` dans le hook de l'agent : un
durcissement, libre selon la politique.

## B-0024 — Un correctif sans test de régression n'est vu qu'en CI

> statut : ouvert · origine : J-2026-10-11-F · lu : backlog@9939ea82

Au banc (s9, première version), deux agents ont commité un correctif
(`fix:`) sans test de régression : ni la fin de tour ni le hook avant
commit ne l'ont vu, seule la CI le refuse (`tests.regression` rejoue les
tests sur le parent, trop lent pour un hook). Au moins avertir en fin de
tour qu'un commit `fix:` de la plage n'apporte aucun test nouveau.

## B-0025 — tests.code-teste prend pour du code une fonction écrite dans une chaîne

> statut : ouvert · origine : J-2026-10-11-F · lu : backlog@a44391d3

Le banc garde le code de ses projets d'essai dans des chaînes Python ; une
ligne `def echelle(x):` en début de ligne, dans une chaîne, est lue comme
une fonction publique ajoutée, qu'aucun test ne nomme. Dispensée pour
l'instant par un trailer ; le lecteur de fonctions devrait sauter les
chaînes multilignes.

## B-0026 — Sur un projet sans aucun test, verify échoue

> statut : ouvert · origine : J-2026-10-11-G · lu : backlog@c462bb86

Vu au banc (s6, premier passage : l'initialisation depuis un cadrage seul)
et reproduit sur un projet installé vide : `socle verify` échoue sur
`verify.tests`, parce que `unittest` rend le code 5 quand il ne trouve
aucun test. Un projet qui commence n'a pas encore de test : l'adaptateur
devrait traiter « aucun test » comme un avertissement, pas comme un échec.
Le juge de s6 ne regardait que les contrôles, pas `verify`.

## B-0027 — Sans adresse de dépôt, l'agent ne sait pas quel lien mettre dans une demande

> statut : ouvert · origine : J-2026-10-11-G · lu : backlog@3cbd3c76

Au banc, huit premiers jets de demande sur onze ont été refusés pour « Où
regarder » sans lien (s4, s5, s9, s11) : sans `[human] repo_url` ni push, `socle
url` échoue, et l'agent écrit des chemins nus. Un lien relatif depuis la
demande (`../../calc.py`) passe le contrat ; le refus, ou le squelette de
`socle new request`, devrait le dire.

## B-0038 — Les textes que le moteur écrit en prose, dans la langue du projet

> statut : ouvert · origine : J-2026-10-11-P · lu : backlog@12919d59

Suite de B-0031 : la mémoire s'écrit en anglais, mais le moteur écrit
encore en français ses messages (contrôles, hooks, ligne de commande) et
les textes en prose qu'il pose dans un projet : l'audit et les questions de
départ de l'initialisation, les commentaires de la politique et des
garde-fous, le texte d'une approbation. Un catalogue de messages par
langue, choisi par `[memory] language` ; les messages des hooks sont lus
par l'agent, ceux de l'installeur et des questions de départ par l'humain,
à traduire en premier.

## B-0039 — Éprouver sur GitHub les étapes de CI que posent les cinq adaptateurs nouveaux

> statut : ouvert · origine : J-2026-10-11-Q · lu : backlog@7813094e

Chaque adaptateur nouveau ajoute au workflow de CI ses étapes
d'installation (Node, Go, Java, Ruby, PHP avec pcov, et leurs dépendances).
Le banc des adaptateurs les a éprouvés ici, pas dans un workflow GitHub :
ces étapes sont supposées. Les éprouver sur un dépôt jetable de chaque
langage, poussé sur GitHub, avec le workflow que pose l'installeur.

## B-0040 — Un adaptateur C# (dotnet test, Stryker.NET), à éprouver là où dotnet existe

> statut : ouvert · origine : J-2026-10-11-Q · lu : backlog@30534ad0

Théo voulait les langages courants ; C# en est, mais dotnet n'est pas dans
ce conteneur, et un adaptateur non éprouvé ne se maintient pas. Écrire
l'adaptateur (`dotnet test`, Stryker.NET et son rapport JSON) et le
passer au banc des adaptateurs là où dotnet existe.

## B-0042 — Installer le socle sans clone : un paquet installable par pip (P10 du relevé du parcours)

> statut : ouvert · origine : J-2026-10-11-V · lu : backlog@79c52d86

La dixième proposition du relevé du parcours (B-0034) : aujourd'hui,
l'humain clone le dépôt du socle et lance l'installeur par `PYTHONPATH`. Un
paquet installable par pip, qui fournit la commande `socle`, ferait
disparaître cette étape. C'est une publication externe : Théo l'a mise à
part dans sa réponse à D-0014, elle attend sa propre demande.

## B-0044 — Les lots de la passe de recul, dans l'ordre validé (D-0015)

> statut : en-cours · origine : J-2026-10-12-F · lu : backlog@19253d8c

Les lots du relevé de la passe de recul (`docs/recul.md`, section 3), dans
l'ordre que Théo a validé : L1, les pertes de données et la casse à
l'installation ; L2, les contournements du hook de l'agent, le hook par
découpage en arguments, les commandes humaines refusées sous un agent, la
branche protégée ; L3, la mémoire privée ; L4, l'auto-test (chaque contrôle
et chaque refus vus échouer) ; R6, le projet d'échecs pour de vrai, qui
demandera sa propre décision ; L5, les contrôles qui laissent passer et
les refus à tort ; puis L6 (la fin de tour, qui change un fichier protégé :
une demande), R2 (le workflow de mutation, B-0005) et L7 (la dette).
Chaque correctif avec un test qui échoue sur le code d'avant ; un compte
rendu à Théo à la fin de chaque lot.

## B-0045 — Des noms de fichiers et de dossiers sont encore en français

> statut : ouvert · origine : J-2026-10-12-F · lu : backlog@19253d8c

Signalé par Théo, texte exact : « Certains noms fichiers/dossier de base
sont encore en français-> backlog à corriger ». La migration du format 2
(B-0032) n'a renommé que les chemins de la mémoire et de la configuration
d'un projet. Restent en français : les dossiers et modules du moteur
(`moteur/`, `modeles/`, `adaptateurs/`, `controles_*.py`, `prive.py`,
`memoire.py`…), les gabarits (`garde-fous.toml`, `politique.toml`,
`modeles/memoire/canonique.md`…), le dossier `banc/`, les marqueurs locaux
d'un projet (sous `.socle/trace/`, et la clé de déploiement du mode
compagnon), et, contre ADR-0002 qui veut les commandes en anglais, des
commandes et des options : `aide`, `prive` et ses actions, `relu`,
`--rapide`, `--court`, `--poser`, `--oui`, `--cadrage`, `--depot` — dont
quatre ajoutées par moi pour B-0034. À faire : un inventaire complet, des
noms anglais, d'anciens noms de commandes gardés le temps d'une version,
et une migration pour ce qui vit dans les projets.

## B-0046 — La documentation à refaire : séparer l'outil de sa fabrication, et la rendre intuitive

> statut : ouvert · origine : J-2026-10-12-F · lu : backlog@19253d8c

Signalé par Théo, texte exact : « la doc mélange la doc/tests relatif au
repo (ce qui permet de construire l'outil de cadrage) et l'outil de cadrage
lui meme, + la doc est pas intuitive pour comprendre ni installer, à refaire
(si c'est pas clair en quoi c'est pas bien pour toi, tu pourra me demander
> backlog) ». Ce que j'en comprends : le README et `docs/` mêlent la
documentation du socle, pour qui l'installe et s'en sert, et le matériel
de sa fabrication dans ce dépôt (architecture, bancs, relevés,
inventaire de `chess`) ; il faut les séparer, et réécrire la première pour
qu'elle se comprenne et s'installe sans effort : ce que c'est en un
paragraphe, l'installation en quelques commandes qui marchent telles
quelles, une première session, l'usage courant, puis la référence. Avant
de commencer, vérifier cette lecture avec Théo, et lui demander où il
s'est perdu. Reprend B-0035, clos trop tôt.

## B-0047 — Le backlog en un fichier par sujet, dans la même migration que les noms anglais (D-0017)

> statut : ouvert · origine : J-2026-10-12-L · lu : backlog@19253d8c

Validé par Théo (D-0017) : un fichier par sujet dans un dossier backlog de
la mémoire, son pendant privé, plus d'archivage des sujets clos au journal,
un plafond par sujet ; dans la même migration de format que B-0045, après
les lots de la passe de recul et R6, avant B-0046. Commence par la
décision qui remplace ADR-0003 pour le backlog.

## B-0048 — Une action externe validée par une demande reste refusée par le hook

> statut : ouvert · origine : J-2026-10-12-M · lu : backlog@47ec3e4f

Mesuré à R6 : D-0016 autorise de pousser l'historique du projet d'échecs
dans la copie, et le hook refuse quand même `git push … main:main`, faute
de savoir qu'une validation existe. Le push revient alors à l'humain, même
validé. Piste : une demande validée qui nomme l'action exacte (le dépôt et
la branche) la laisse passer au hook, une fois. Voisin de B-0018.

## B-0049 — instructions.source-unique exige AGENTS.md quand l'installeur a gardé CLAUDE.md comme source

> statut : fait · origine : J-2026-10-12-M · lu : backlog@ca384505 · ref : J-2026-10-13-C

Mesuré à R6, sur un clone du projet d'échecs : l'installeur garde
CLAUDE.md comme source (35 fichiers du projet le nomment) et y ajoute la
section du socle, mais le contrôle exige AGENTS.md et un CLAUDE.md réduit à
`@AGENTS.md`. En adoption, c'est un avertissement à tort, et permanent. Le
contrôle doit accepter la source que l'installeur a choisie. Le `.gitignore`
posé dans ce cas renvoie lui aussi à AGENTS.md, absent.

## B-0050 — Un commit d'agent sans aucun hook de l'agent n'est vu qu'en CI

> statut : ouvert · origine : <J-… ou commit:… où le sujet est apparu> · lu : backlog@c11291ba

Mesuré à R6 : un commit fait dans la copie du projet d'échecs, depuis une
session ouverte dans ce dépôt, porte `Socle-Hooks: SessionStart=0
PreToolUse=0 Stop=0` ; les hooks de l'agent n'y ont jamais tiré, et rien ne
le dit avant le push : le hook avant push de la copie l'a refusé ensuite
(`hooks.trace`), comme la CI. Le hook `commit-msg` pourrait avertir dès le
commit quand un commit d'agent ne compte aucun hook.

## B-0051 — tests.regression refuse à tort un correctif Rust testé dans son module

> statut : fait · origine : J-2026-10-12-Q · lu : backlog@104e7a14 · ref : J-2026-10-13-A

Mesuré à R6, tâche 4 : l'agent corrige un défaut de `chess` et écrit son
test de régression dans le module, comme le projet le fait partout ; la
CI du socle refuse le correctif (« aucun fichier de tests/*.rs ajouté ou
modifié »), alors que le hook avant push l'avait laissé passer (B-0024).
L'adaptateur Rust n'accepte qu'un test d'intégration, parce qu'un test du
module voyage avec le code et ne se pose pas seul sur le commit d'avant.
Pistes : rejouer sur le parent le seul diff du module de tests ; dire la
règle à l'agent dès le commit d'un `fix:`.

## B-0052 — La forme depot:chemin échappe au contrôle des références

> statut : fait · origine : J-2026-10-12-Q · lu : backlog@2a6691e4 · ref : J-2026-10-13-D

Mesuré à R6, tâche 1 : pour des fichiers qu'une rustine crée, l'agent a
écrit `<rustine>.patch:<chemin>`, sur le modèle de `depot:chemin`, et le
contrôle des références les a laissés passer sans rien vérifier. Le geste
était juste (il a ajouté au projet le test qui vérifie ces chemins), mais
n'importe quelle chaîne `x:chemin` échappe ainsi au contrôle. Ne laisser
passer que les dépôts connus, ou le dire.

## B-0053 — Deux branches parallèles calculent les mêmes identifiants

> statut : ouvert · origine : J-2026-10-12-Q · lu : backlog@4f28165c

Mesuré à R6 : cinq branches parties du même commit ont chacune pris
`B-0001` et `J-2026-10-12-C` pour des entrées différentes ; leur fusion les
heurtera. `socle new` calcule l'identifiant sur l'arbre de la branche, qui
ne voit pas les autres. À trancher avec B-0047 (un fichier par sujet) :
numéroter à la fusion, ou des identifiants que deux branches ne peuvent pas
prendre ensemble.

## B-0054 — Deux états au démarrage quand le projet a déjà le sien

> statut : ouvert · origine : J-2026-10-12-Q · lu : backlog@a1cd520a

Mesuré à R6 : le projet d'échecs a déjà son état au démarrage
(`chess:tools/etat.sh`), et l'installeur ajoute celui du socle ; chaque
session en reçoit deux, qui se recoupent (branche, commits non fusionnés,
ce qui revient à l'humain). L'installeur pourrait le signaler, et la
documentation dire comment n'en garder qu'un.
