# Le socle : ce qu'il fait, comment il est fait

Ce document explique le socle à qui l'installe ou veut le comprendre. Les
gestes de l'humain, chacun avec sa commande, sont dans le guide
(`engine/socle/HELP.md`, affiché par `python3 .socle/socle help`) ; le
format exact de la mémoire, dans `engine/socle/FORMAT.md` ; la
correspondance entre chaque exigence du cadrage et le contrôle qui
l'applique, dans `docs/architecture.md`.

## Le problème

Un agent de code qui entretient un projet sur des semaines oublie : chaque
session repart de zéro, et un compactage efface une partie de la
conversation. Ce qu'il écrit pour s'en souvenir dérive, comme la
documentation qu'il tient. Ses tests peuvent passer sans rien mesurer. Il
cite un fichier ou un commit qui n'existe pas, relâche un seuil pour faire
passer un contrôle, ou tranche une question qui revenait à l'humain.
Chacune de ces erreurs est plausible et silencieuse : elle se voit trop
tard, quand elle se voit.

## Le principe

Le socle ne demande pas à l'agent d'être fiable : il rend ses erreurs
détectables par une machine, au plus tôt.

- **L'agent écrit tout** : la mémoire, la documentation, les tests.
- **Des contrôles automatiques vérifient**, à trois étages : pendant le
  travail de l'agent, au commit, et en CI. La CI exécute tout, et rien ne
  la contourne.
- **L'humain ne tranche que ce qu'aucun contrôle ne peut trancher** : une
  décision coûteuse à défaire, un seuil à relâcher, une valeur attendue à
  changer, une action irréversible. L'agent la lui pose par une demande qui
  se lit seule.
- **Ce qui se calcule ne s'écrit pas** : où en est le projet (le commit, la
  CI, ce qui attend l'humain) se dérive de git et de la mémoire à chaque
  démarrage, au lieu d'être recopié dans un fichier qui vieillirait.
- **Rien ne s'affaiblit en silence** : un seuil ne se relâche, un fichier
  protégé ne change, qu'avec la validation de l'humain.
- **Chaque garde-fou a été vu échouer** : l'auto-test injecte chaque défaut
  connu dans un projet jetable, et vérifie que l'étage prévu l'attrape.

Le moteur est en Python 3.11 ou plus récent, bibliothèque standard seule,
et ne connaît ni le langage du projet ni l'agent : ce qui dépend du langage
vit dans un adaptateur, ce qui dépend de l'agent dans ses hooks.

## Ce que l'installation pose dans un projet

```text
.socle/
  socle               le lanceur : python3 .socle/socle <commande>
  engine/socle/       le moteur, copié tel quel ; la CI vérifie son empreinte
  engine.lock         sa version et son empreinte
  policy.toml         la politique d'autonomie, à l'humain
  guardrails.toml     les seuils des contrôles, sous cliquet
  adapter.toml        le langage du projet et ses outils
  git-hooks/          les hooks git, branchés par core.hooksPath
memory/               la mémoire du projet
AGENTS.md             les instructions de l'agent ; CLAUDE.md l'importe
.claude/settings.json les hooks de Claude Code
.github/workflows/socle.yml   la CI
.github/workflows/socle-mutation.yml   le balayage de mutation hebdomadaire,
                      quand l'adaptateur en déclare un et que le projet n'en
                      lance pas déjà un
.github/CODEOWNERS    l'humain, propriétaire de la politique, des hooks et de la CI
```

Trois sortes de fichiers, donc : le moteur, que seul l'installeur remplace ;
les fichiers du projet, que l'agent modifie selon la politique ; et les
étages d'application (hooks, CI), protégés.

## La mémoire

Six couches, chacune avec sa règle, toutes lisibles par script : un en-tête
par fichier, des entrées à identifiant stable, des métadonnées sur une
ligne.

- **Les faits** (`F-`) : ce qui est établi, chacun avec un statut. Un fait
  « mesuré » pointe vers sa preuve (un commit, un fichier) ; un fait
  « supposé » attend d'être vérifié ; un fait « réfuté » reste, barré, avec
  la mesure qui le réfute ; un fait « validé » cite la réponse de l'humain.
- **Le chantier actif** : ce qui est en cours et les prochaines étapes. Le
  seul fichier réécrit librement, et borné en taille.
- **Les décisions** (`ADR-`) : une par fichier, avec ses raisons. Seul son
  statut change ensuite.
- **Le journal** (`J-`) : une entrée datée par événement, en ajout seul. Il
  dit pourquoi les choses sont ainsi.
- **Le backlog** (`B-`) : les sujets ouverts, chacun avec son origine ; un
  sujet clos cite ce qui l'a clos.
- **Les demandes** (`D-`) : les décisions qui attendent l'humain, puis sa
  réponse, gelée.

Un identifiant se calcule (`socle new`), il ne se devine pas. Une entrée
citée avec son empreinte (`ADR-NNNN@xxxxxxxx`) prouve qu'elle a été lue dans
cette version ; une décision, une demande ou un sujet nouveaux doivent
prouver ainsi qu'ils ont consulté l'index de leur couche. Le code et les
tests font foi avant la mémoire, et les faits avant le journal.

**Mémoire privée.** Des notes qui ne doivent pas être publiques (une idée,
un client) vont dans une zone privée, au même format. Deux modes : un dépôt
compagnon, privé, cloné dans la zone et ignoré du dépôt public, dont un
verrou commité dit quel commit va avec chaque commit public ; ou des
fichiers commités chiffrés par un filtre git. La politique choisit les
couches privées par défaut, et l'humain peut placer une entrée précise d'un
côté ou de l'autre. Les contrôles vérifient qu'aucun identifiant ni terme
privé ne fuit dans ce qui se publie (fichiers et leurs noms, messages de
commit, branches, pull requests), un terme sous ses variantes d'écriture
compris, et, si l'humain l'a choisi, qu'il a relu ce qui part avant chaque
push. Sans accès à la zone privée, elle est dite indisponible : jamais
sautée en silence, et rien n'y est écrit à l'aveugle. Le mode chiffré est
le moins éprouvé des deux : il dépend d'un filtre que le socle ne pose pas
(git-crypt ou un équivalent), et ses tests n'emploient qu'un filtre
d'essai ; le mode compagnon est le plus sûr.

**Langue.** La mémoire s'écrit en français ou en anglais, au choix du
projet, et se lit dans les deux.

## L'état dérivé

`python3 .socle/socle state` imprime où en est le projet : le commit et la
branche, ce qui n'est pas fusionné, l'état de la CI et si GitHub l'exige
avant de fusionner, l'index des décisions,
le backlog, les demandes en attente, ce qui revient à l'humain, ce que
l'humain a écrit lui-même depuis le dernier commit de l'agent, l'accès à la
mémoire privée ; puis le chantier actif et les faits. Sous Claude Code, le
hook de démarrage l'injecte à chaque session et après chaque compactage :
l'agent repart de ce qui est vrai, pas de ce qu'il croit se rappeler.

## Les contrôles

Une trentaine, que `python3 .socle/socle checks` liste avec leurs étages.
Par famille :

- **La mémoire** : format, références (tout identifiant, fichier, lien ou
  commit cité existe), preuves des faits, origine et clôture des sujets,
  budgets de taille, ajout seul du journal et des décisions, lectures
  prouvées, mémoire en retard sur le code.
- **La documentation** : une valeur citée dans la doc est liée à sa source
  et concorde ; un dispositif du dépôt (hook, workflow) est nommé dans un
  document ; un code associé à une doc ne change pas sans elle ; un même
  paragraphe dans deux fichiers est une copie refusée.
- **Les tests** : pas de test sans assertion, d'assertion tautologique ni de
  test désactivé sans raison ; une valeur attendue ne change pas, un test ne
  disparaît pas, sans la validation de l'humain ; une fonction publique
  ajoutée ou modifiée est nommée par un test ; un correctif apporte un test
  qui échoue sur le commit d'avant.
- **La mutation** : chaque module qui porte du code a un plafond de mutants
  survivants, mesuré, qui ne peut que baisser. Un module pas encore balayé y
  entre « à mesurer ». Le balayage tourne chaque semaine sur GitHub
  (`socle mutation-run`, posé par l'installeur) ; une issue s'ouvre quand le
  cliquet casse, et la CI dit, à chaque push, quand il cesse de tourner :
  GitHub endort les workflows planifiés d'un dépôt public après soixante
  jours sans activité.
- **Ce qui ne doit pas s'affaiblir** : le cliquet des seuils, les fichiers
  protégés, l'empreinte du moteur, la configuration des hooks et leur trace
  dans chaque commit de l'agent.
- **Les demandes** : chaque demande en attente respecte son contrat, chaque
  réponse porte sur le texte exact de sa demande.
- **Le privé** : accès, verrou, chiffrement, fuites, liste des termes.

## Les trois étages

| Étage | Quand | Ce qu'il fait |
| --- | --- | --- |
| L'agent (hooks de Claude Code) | au démarrage, avant chaque outil, à la fin de chaque tour | injecte l'état ; refuse une action irréversible, l'écriture d'un fichier protégé, une réponse à la place de l'humain, une référence ou un SHA inventés, une fuite du privé ; refuse de conclure tant que les contrôles échouent, que la mémoire est en retard sur le code, ou que le dernier message n'a pas son récap (« Pour toi : », « Ensuite : ») et des liens que l'humain peut suivre |
| git | à chaque commit et à chaque push | juge ce qui sera commité (l'index) avec les contrôles rapides ; trace les hooks de l'agent dans le commit ; refuse une fuite dans le message ; avertit d'une fonction sans test ; avant le push, exécute `verify --fast` (ses étapes, seulement si elles n'ont pas déjà passé sur cet arbre), juge la plage qui part comme la CI du push la jugera, et, si elle est choisie, exige la relecture de l'humain |
| La CI | à chaque push et pull request | exécute tout, contre la base : les capacités de l'adaptateur, tous les contrôles, et l'auto-test du socle |

Le même moteur sert les trois étages. Un autre agent que Claude Code n'a
pas les hooks du premier étage : il lance `socle state` lui-même, et les
hooks git et la CI le couvrent comme n'importe qui.

Après trois échecs de suite à la fin d'un tour, l'agent s'arrête et écrit
une demande qui résume ce qu'il a tenté.

## La politique d'autonomie

`.socle/policy.toml` dit ce que l'agent décide seul et ce qu'il demande.
Elle tient en huit points : relâcher un garde-fou, supprimer un test ou
changer une valeur attendue exigent une demande validée ; une décision
réversible et mesurable, l'agent la prend et l'écrit, une décision coûteuse
à défaire, il la demande ; une action irréversible ou externe est toujours
demandée, et le hook la refuse ; la mémoire est en ajout seul ; un bug
voisin va au backlog ; trois échecs de suite, il s'arrête ; une validation
attendue, il travaille sur autre chose sans deviner. La politique est un
fichier protégé : seul l'humain la modifie.

## Les demandes de décision

Une demande est écrite pour être lue sans le projet en tête : la décision,
le contexte résumé sur place, chaque élément cité décrit en clair, un lien
vers chaque document à lire, les options avec leur effort, leur risque et
leur réversibilité, les conséquences de chaque réponse, une recommandation
qui sépare le vérifié du supposé, et les réponses possibles, dont
`contexte-insuffisant`. Le hook refuse une demande incomplète.

Son cycle : l'agent l'écrit et la pousse, puis en donne le lien ;
l'humain répond dans la conversation ; l'agent consigne la réponse avec le
texte exact de l'humain, seulement si la demande a été poussée telle
quelle ; la demande répondue est gelée. Une réponse validée est ce qui
autorise ensuite le changement qu'elle nomme : la clé de seuil, le test,
le fichier protégé.

Quand c'est l'humain qui change lui-même un fichier protégé (une mise à
jour du socle, sa politique), il l'approuve d'une commande, qui écrit la
demande et sa réponse d'un seul geste. L'agent ne peut pas la lancer.

## Les garde-fous et le cliquet

`.socle/guardrails.toml` porte les seuils : les budgets de taille de chaque
couche, les plafonds de mutation, les correspondances entre code et doc,
les valeurs liées, la taille d'une copie, les chemins de spécification.
Le cliquet compare chaque clé à celle de la base, avec un sens par clé (un
budget plus bas est plus strict, une liste d'exclusions plus courte aussi).
Durcir est libre ; relâcher fait échouer la CI tant qu'une demande validée
ne cite pas la clé. Une clé inconnue qui change compte comme un
relâchement.

Les fichiers protégés (la politique, l'adaptateur, le verrou du moteur, les
hooks, la CI, les réponses de l'humain) ne changent qu'avec une validation
qui cite leur chemin et leur empreinte nouvelle.

## Les adaptateurs

L'adaptateur dit au moteur comment le langage du projet se vérifie : ses
capacités (formater, analyser, compiler, tester, muter, mesurer la
couverture, rejouer un test sur le commit d'avant), et comment lire ses
tests et ses fonctions publiques. Une capacité absente se déclare, avec ce
qui la remplace. Huit sont maintenus et éprouvés sur un projet jetable de
leur langage : Rust, Python sous `unittest` et sous pytest, JavaScript et
TypeScript, Go, Java, Ruby, PHP. Un autre langage se décrit dans un fichier
de même forme. Le détail : `engine/socle/adapters/README.md`.

## L'auto-test et les bancs

`python3 .socle/socle selftest` fabrique un projet jetable, y injecte un à
un chaque défaut connu (une référence morte, un test tautologique, un seuil
relâché, une réponse écrite par l'agent…), et vérifie que le contrôle
prévu l'attrape à l'étage prévu ; des témoins sains vérifient qu'un travail
correct passe, et qu'un changement validé par l'humain (un seuil relâché,
un fichier protégé, une valeur attendue) passe aussi. Chaque contrôle et
chaque refus du hook en ont au moins un défaut, ce qu'un test exige. La CI
le lance à chaque push. Un garde-fou ajouté sans son
défaut injecté n'est pas accepté dans ce dépôt.

Deux bancs mesurent le reste : le banc d'évaluation fait travailler un
agent réel sur des scénarios propices aux erreurs, et dit quel étage
attrape quoi (`docs/banc.md`) ; le banc des adaptateurs éprouve chacun sur
les vrais outils de son langage (`bench/adapters.py`).

## Quand un contrôle refuse

Chaque refus dit ce qu'il a vu et comment en sortir. Les plus courants :

| Ce qui refuse | Ce que cela veut dire | Que faire |
| --- | --- | --- |
| `protege.fichiers`, au commit | un fichier protégé a changé sans validation | si c'est l'humain : `socle approve --text "<raison>"` ; si c'est l'agent : une demande |
| `cliquet.garde-fous` | un seuil a été relâché | le remettre, ou une demande validée qui cite la clé |
| `tests.attendus` | une valeur attendue a changé, ou un test a disparu | une demande validée qui nomme le test, ou une spécification que l'humain a changée |
| `tests.code-teste`, en CI | une fonction publique sans test qui la nomme | écrire le test, ou `Dispense-test: f — <raison>` dans le message du commit |
| `tests.regression`, en CI | un correctif sans test qui échoue sur le commit d'avant | écrire ce test |
| `docs.correspondance` | du code associé à une doc a changé sans elle | changer la doc, ou `Dispense-doc: <raison>` dans le commit qui change ce code |
| `memoire.lectures` | une empreinte citée ne correspond plus | relire l'entrée ou l'index (`socle show`), citer l'empreinte affichée |
| `memoire.collisions` | un identifiant que la branche a pris, la branche par défaut l'a pris aussi depuis, pour une autre entrée | `socle renumber <ID>`, qui donne le prochain libre et le reporte |
| `memoire.retard`, en fin de tour | du code a changé et la mémoire non | mettre à jour le chantier actif, le journal ou le backlog |
| fin de tour refusée, « Pour toi : » | le dernier message de l'agent n'a pas son récap | finir par le récap et les deux lignes |
| `prive.verrou` | le verrou du dépôt compagnon manque ou retarde | `socle private lock` ; rien en place : `socle private install --repo <adresse>`, par l'humain |
| `mutation.couverture` | un module qui porte du code n'a pas de plafond | l'y poser « à mesurer », puis `socle mutation-run --record`, ou recopier le plafond qu'imprime le dernier balayage planifié |
| `mutation.vivante`, en CI | le balayage planifié est endormi, ou ne tourne plus depuis quinze jours | le réactiver dans l'onglet Actions de GitHub et le lancer à la main : c'est à l'humain, et l'état le lui dit |
| push refusé, relecture | la politique exige la relecture de l'humain | l'humain relit ce qui part, l'agent consigne son accord |

Un hook peut se contourner en local (`--no-verify`) ; la CI exécute tout,
et l'agent n'a pas le droit de le faire. La CI n'arrête rien d'elle-même :
une CI rouge n'empêche de fusionner que si GitHub l'exige, par un ensemble
de règles (ou une protection) de la branche par défaut. L'installation le
dit à l'humain, et l'état dit si c'est fait.

## Ce qui n'est pas fait

Le backlog le tient (`python3 .socle/socle show --index backlog`) :
l'empreinte du moteur comparée
à la version publiée, un paquet installable par pip, les textes du moteur
dans la langue du projet, et les limites connues des contrôles.
