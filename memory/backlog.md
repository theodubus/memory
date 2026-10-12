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

## B-0029 — Choisir couche par couche ce qui est privé, et y basculer l'existant

> statut : fait · origine : J-2026-10-11-J · lu : backlog@1eb11b2e · ref : J-2026-10-11-O

Demandé par Théo : pouvoir mettre en privé, au-delà des demandes, tout ce
qui touche aux décisions et à la stratégie interne. L'essentiel existe : avec
une mémoire privée (`[private] mode`), tout contenu nouveau va par défaut
dans la zone privée, sauf les demandes (`[private] requests`). Manquent : un
choix couche par couche (par exemple les décisions et le journal privés, les
faits publics), et une commande qui bascule en privé des entrées publiques
existantes, en réécrivant les renvois et sans rien laisser dans
l'historique public qu'une réécriture ne corrige pas (à dire à l'humain).

Précisé par Théo (J-2026-10-11-N) : n'importe quelle couche doit pouvoir
être privée, backlog et faits compris, et une couche publique par défaut
doit pouvoir porter des entrées privées au détail, choisies dans la
conversation (par exemple des décisions publiques, sauf certaines). Ce qui
existe : `socle new <type> --private` ou `--public` choisit la zone entrée
par entrée, pour tout type, dès qu'une mémoire privée existe ; une réponse
privée est protégée comme une publique. Ce qui manque, outre les défauts
par couche et la bascule : une règle dans les instructions de l'agent pour
qu'une consigne « celle-ci en privé » donne `--private` ; et l'état du
démarrage n'injecte que le chantier actif et les faits publics, pas leurs
pendants privés.

## B-0030 — Des adaptateurs pour d'autres langages courants

> statut : fait · origine : J-2026-10-11-J · lu : backlog@d2bc3f03 · ref : J-2026-10-11-Q

Demandé par Théo : plus que Rust et Python. Candidats, avec leurs outils de
test et de mutation usuels : JavaScript et TypeScript (npm, vitest ou jest,
Stryker), Go (go test, gremlins ou go-mutesting), Java et Kotlin (Maven ou
Gradle, JUnit, PIT), C# (dotnet test, Stryker.NET), Ruby (RSpec, mutant), PHP
(PHPUnit, Infection). Chacun avec ses marqueurs de détection pour
l'installeur (package.json, go.mod, pom.xml ou build.gradle, *.csproj,
Gemfile, composer.json) et un projet jetable qui prouve la chaîne, comme
pour `python-pytest` (jalon 6).

## B-0031 — La langue de la mémoire au choix du projet

> statut : fait · origine : J-2026-10-11-J · lu : backlog@a2722fbd · ref : J-2026-10-11-P

Demandé par Théo : proposer l'anglais ou une autre langue pour la mémoire.
Tout est en français aujourd'hui : les mots-clés du format (statuts, champs
des entrées, sections des demandes), les gabarits, les messages des
contrôles et de la CLI. Piste : des clés internes fixes, un vocabulaire par
langue que le lecteur accepte selon la langue du projet (réglée dans la
politique), un catalogue de messages, et une migration qui traduit les
mots-clés d'une mémoire existante, pas son contenu. Effort important mais
mécanique ; plus simple une fois B-0032 fait.

## B-0032 — Des noms de fichiers et de dossiers en anglais pour tous les projets

> statut : fait · origine : J-2026-10-11-J · lu : backlog@487629e3 · ref : J-2026-10-11-N

Demandé par Théo : des noms de dossiers et de fichiers en anglais pour
tous les projets, quelle que soit la langue de la mémoire (`memory/`,
`canonical.md`, `active.md`, `requests/`, `policy.toml`, `guardrails.toml`…).
Avis de l'agent : bonne idée. Un chemin est un identifiant, et ADR-0002 veut
les identifiants en anglais ; un seul jeu de chemins évite d'en traduire par
langue et découple B-0031 ; les permaliens déjà donnés restent valides,
puisqu'ils visent un commit. Coût : une migration de format (le cadre
existe, `migrations.py`), dont le renommage de fichiers protégés, à
approuver par l'humain ; à faire tôt, avant que d'autres projets s'installent.

## B-0033 — Un travail qui attend la validation d'une valeur attendue ne peut ni se commiter ni rester dans l'arbre en fin de tour

> statut : fait · origine : J-2026-10-11-J · lu : backlog@f05f130c · ref : J-2026-10-11-R

Constaté en faisant B-0032 : le renommage des chemins change la valeur
attendue de quatorze tests. Le point 2 de la politique exige une demande
validée qui les nomme ; la demande est posée et poussée. Mais en attendant
la réponse, le travail ne peut pas se commiter (le hook avant commit
refuse), et il ne peut pas rester dans l'arbre : le hook de fin de tour
refuse de conclure tant que les contrôles échouent, puis demande
d'escalader après trois tentatives. L'agent doit remiser son travail
(`git stash`), hors de la mémoire et à la merci du conteneur. La politique
dit pourtant « mettre la demande en file, travailler sur autre chose ».
Piste : à la fin de tour seulement, un refus de `tests.attendus` dont le
test est nommé par une demande en attente, poussée telle quelle, devient
un constat « en attente de la demande » ; le commit et la CI refusent
toujours.

## B-0034 — Le parcours de l'utilisateur, de l'installation à l'usage courant, rendu simple

> statut : fait · origine : J-2026-10-11-N · lu : backlog@22423b8f · ref : J-2026-10-11-V

Demandé par Théo : avant d'écrire la documentation du socle (B-0035),
travailler le parcours de l'utilisateur pour que le socle soit simple à
mettre en place et à utiliser. À examiner : ce que l'humain doit taper,
lire ou décider, de l'installation (choix de l'adaptateur, de la mémoire
privée, du propriétaire) à l'initialisation, puis au travail courant
(répondre à une demande, approuver un fichier protégé, relire avant
publication, migrer à une mise à jour) ; ce qui peut se déduire ou se faire
seul ; les messages d'erreur qui ne disent pas quoi faire. Mesurer le
parcours sur une installation neuve, et noter chaque étape qui demande à
l'humain de lire le code.

Constaté par Théo (J-2026-10-11-R) : sa propre approbation de la migration
a créé une demande, D-0012, écrite et validée d'un seul geste par
`socle approve`. Son numéro n'a paru que dans la sortie de son terminal, et
jamais dans la conversation ; il s'est demandé s'il l'avait validée. Ce que
l'humain fait lui-même devrait lui être rappelé par son nom, et l'agent le
citer au tour suivant.

## B-0035 — La documentation du projet : ce que fait le socle, comment il est fait, comment l'installer et s'en servir

> statut : ouvert · origine : J-2026-10-11-N · lu : backlog@e7973e14

Demandé par Théo : une documentation du projet qui dise ce que fait le
socle, comment il est structuré et fait, comment le mettre en place et
s'en servir. Aujourd'hui, ce savoir est éclaté entre les instructions de
l'agent, l'architecture, le format de la mémoire et le banc, écrits pour
l'agent ou pour qui fabrique le socle, pas pour qui l'installe. À faire
après le parcours de l'utilisateur (B-0034), pour documenter un parcours
déjà simplifié plutôt que l'actuel.

## B-0036 — Migrer ce dépôt au format 2 de la mémoire

> statut : fait · origine : J-2026-10-11-N · pour : humain · lu : backlog@e7557122 · ref : commit:bba48a6

Ce dépôt est encore au format 1 de la mémoire (chemins en français). Sa
migration au format 2 renomme six fichiers protégés (CODEOWNERS, le
workflow de CI, l'adaptateur, le verrou du moteur, la politique et le
lanceur) : seul Théo peut les approuver. Répétée sur une copie du commit qui
livre le format 2 : seul le refus des fichiers protégés reste avant
approbation. Les trois commandes sont dans la conversation du 2026-10-11 ;
la première est `socle install` relancée en mode amont.

## B-0037 — Le conseil du refus d'une empreinte d'index périmée mène à une empreinte refusée

> statut : fait · origine : J-2026-10-11-N · lu : backlog@e6ba5929 · ref : J-2026-10-11-R

Constaté en ouvrant B-0036 : un sujet de backlog cite l'index qu'il a lu ;
si l'index change ensuite (un autre sujet clos), le refus conseille
`socle show --index backlog` et l'empreinte affichée. Mais cet index
compte déjà le sujet qui cite, et le contrôle des lectures ne l'accepte
que sans lui : le conseil suivi mène à un second refus. Corriger l'un ou
l'autre : accepter aussi l'index qui compte l'entrée citante, ou faire
afficher l'empreinte sans elle.

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

## B-0041 — Une passe sur tout le code, avec du recul sur la technique et sur ce que l'outil doit faire

> statut : ouvert · origine : J-2026-10-11-T · lu : backlog@5dcd4e94

Demandé par Théo, texte exact : « une passe de ta part sur tout le code et
prendre du recul pour voir ce qu'on pourrait modifier/ajouter (que ce soit
sur des points techniques ou alors de façon beaucoup plus macro sur le
fonctionnement lui même en réfléchissant à ce que l'outil est censé
faire) ». Deux niveaux : relire le moteur module par module (dette,
duplications, ce qui ne sert plus, ce qui manque de tests ou de clarté) ;
puis repartir du cadrage et des mesures du banc pour juger si le socle
atteint son but, et ce qui changerait le plus pour l'humain et l'agent. Le
résultat se soumet à Théo, comme le relevé du parcours, avant d'être fait.

## B-0042 — Installer le socle sans clone : un paquet installable par pip (P10 du relevé du parcours)

> statut : ouvert · origine : J-2026-10-11-V · lu : backlog@79c52d86

La dixième proposition du relevé du parcours (B-0034) : aujourd'hui,
l'humain clone le dépôt du socle et lance l'installeur par `PYTHONPATH`. Un
paquet installable par pip, qui fournit la commande `socle`, ferait
disparaître cette étape. C'est une publication externe : Théo l'a mise à
part dans sa réponse à D-0014, elle attend sa propre demande.

## B-0043 — Le hook avant push juge contre la branche par défaut, la CI contre le push précédent

> statut : ouvert · origine : J-2026-10-12-A · lu : backlog@79c52d86

La CI d'un push juge la plage de ce push (`github.event.before`), alors que
le hook avant push et `verify` jugent contre la divergence avec la branche
par défaut. Sur une branche longue, la seconde plage est plus large : une
dispense d'un commit ancien y couvre une fonction modifiée plus tard, une
validation ancienne y couvre une assertion réécrite. Deux pushes de B-0034
sont passés en local et ont échoué en CI. À faire : que le hook avant push
juge aussi la plage qui part (du sha distant au sha local, qu'il reçoit sur
son entrée), comme la CI le fera.
