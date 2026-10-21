# Le socle, côté humain : guide d'utilisation

Ce guide décrit l'usage d'un projet équipé du socle, du point de vue de
l'humain qui le conduit : son rôle, chaque geste avec sa commande, la
conduite à tenir quand un contrôle refuse, et la référence des commandes,
de la politique et des seuils. Il suppose le socle installé ; ce qu'est le
socle, son principe et son installation sont présentés dans le README de
son dépôt.

Les commandes se lancent à la racine du projet :
`python3 .socle/socle <commande>`. Ce guide s'affiche par
`python3 .socle/socle help`.

## Le rôle de l'humain

L'agent écrit le code, les tests, la documentation et la mémoire ; les
contrôles vérifient son travail. L'humain intervient sur quatre points :

- **répondre aux demandes de l'agent**, quand une décision lui revient ;
- **approuver ses propres changements** aux fichiers protégés ;
- **effectuer les actions que seul l'humain peut faire** : celles que le
  hook refuse à l'agent (pousser sur la branche par défaut, publier,
  supprimer à distance, dépenser) et les réglages des services (GitHub,
  dépôt privé). L'agent les inscrit au backlog avec `pour : humain` et leur
  mode d'emploi ; l'état les liste ;
- **fixer la politique d'autonomie**, `.socle/policy.toml`, qu'il est seul à
  modifier.

### La politique d'autonomie

La politique tient en huit règles, que l'agent applique et que les hooks
font respecter :

1. Assouplir un garde-fou (`.socle/guardrails.toml`) exige une demande
   validée ; le durcir est libre.
2. Supprimer un test ou changer une valeur attendue exige une demande
   validée, ou une spécification que l'humain a lui-même changée et qui
   nomme le test.
3. Une décision de conception réversible et mesurable, l'agent la prend et
   l'écrit ; une décision coûteuse à défaire, il la demande.
4. Une action irréversible ou externe est toujours demandée ; le hook la
   refuse à l'agent.
5. La mémoire est en ajout seul ; un fait « réfuté » cite la mesure qui le
   réfute ; « validé » ne s'écrit qu'après la réponse de l'humain.
6. Un défaut voisin du travail en cours va au backlog ; il ne se corrige
   que s'il bloque.
7. Après trois échecs de suite des contrôles, l'agent s'arrête et écrit une
   demande qui résume ce qu'il a tenté.
8. Une validation attendue ne se devine pas : l'agent met la demande en
   file et travaille sur autre chose.

## Suivre le projet

- `python3 .socle/socle state` imprime l'état du projet, calculé à chaque
  appel : le commit, la CI et si GitHub l'exige avant la fusion, le
  backlog, les demandes en attente, ce qui revient à l'humain, puis le
  chantier actif et les faits. L'agent reçoit le même état au démarrage de
  chaque session.
- Chaque intervention de l'agent qui a agi se termine par deux lignes :
  « Pour toi : », ce qui revient à l'humain, et « Ensuite : », la suite
  prévue.
- La mémoire se lit dans `memory/` : les faits et leurs preuves, le
  chantier actif, les décisions, le journal, le backlog, les demandes. Son
  format est spécifié dans `.socle/engine/socle/FORMAT.md`.

## Les gestes

### Décrire le projet

Juste après l'installation :

```sh
python3 .socle/socle init --brief <document> --repo
```

Le document de cadrage est archivé tel quel ; `--repo` relève ce que le
dépôt contient déjà (outils, tests, CI). Sans document, `--repo` seul ;
dans un dépôt vide, sans option. L'agent pose ensuite, dans la
conversation, quelques questions de départ, chacune avec sa valeur par
défaut.

### Répondre à une demande

Quand une décision revient à l'humain, l'agent écrit une demande, la pousse
et en donne le lien. La demande se lit seule : la décision, le contexte,
les options, la recommandation, et la liste des réponses possibles, à sa
fin.

Répondre dans la conversation par l'une de ces réponses, avec au besoin
une précision ; l'agent consigne la réponse avec le texte exact de
l'humain. `valider` est la seule réponse qui autorise un geste réservé à
l'humain (relâcher un seuil, supprimer un test, changer un fichier
protégé). `contexte-insuffisant` renvoie la demande à l'agent, qui la
réécrit.

Hors de la conversation, depuis un terminal :

```sh
python3 .socle/socle answer D-NNNN <réponse> --text "<texte de la réponse>"
```

Une demande répondue est gelée : elle ne change plus.

### Consigner une décision prise en séance

Une question tranchée sur le moment, l'humain présent (approuver une spec,
trancher une question ouverte), n'a pas besoin d'une demande complète :
répondre dans la conversation ; l'agent consigne aussitôt la question et la
réponse, mot pour mot, dans le même registre que les demandes
(`socle decision`).

### Approuver ses propres changements protégés

La politique, les seuils, l'adaptateur, les hooks, la CI et le moteur sont
protégés : un commit qui les change sans validation est refusé. Quand le
changement vient de l'humain (une mise à jour du socle, une politique
modifiée) :

```sh
python3 .socle/socle approve --text "<raison>"
```

La commande liste les fichiers protégés changés, puis les approuve sur
confirmation en écrivant une demande validée, à commiter avec eux. Elle est
réservée à l'humain : le hook la refuse à l'agent, qui cite ensuite le
numéro de cette approbation.

### Relire avant publication

Si la politique l'exige (`review` dans la section `[private]`), rien ne part
vers le dépôt public sans l'accord de l'humain : l'agent montre ce qui part,
l'humain répond dans la conversation, et l'agent consigne l'accord. Depuis
un terminal : `python3 .socle/socle reviewed --by <nom>`.

### Commiter soi-même

Les commits de l'humain passent par les mêmes contrôles. Une fonction
publique ajoutée ou modifiée est nommée par un test, ou dispensée dans le
message du commit (`Dispense-test: f — <raison>`) ; le hook le signale au
commit, et la CI refuse sans. Un correctif (sujet `fix:`, ou trailer
`Corrige: B-NNNN`) apporte un test qui échoue sur le commit parent.

### Mettre en place la mémoire privée en mode compagnon

En mode compagnon, la mémoire privée vit dans un second dépôt, privé.
Créer ce dépôt, vide, sur GitHub, puis :

```sh
python3 .socle/socle private install --repo <adresse du dépôt privé>
```

La commande clone le dépôt privé, y fait le premier commit, écrit le
verrou et crée une clé de déploiement. Elle termine par les deux gestes qui
restent sur GitHub (la clé de déploiement du dépôt privé, deux secrets du
dépôt public), avec le lien de chaque page. Elle est réservée à l'humain.

### Protéger la branche par défaut

Après le premier push, sur GitHub, dans les réglages du dépôt (« Rules ») :
créer un ensemble de règles qui exige, avant toute fusion, la CI du socle
(« Socle — verify, contrôles, auto-test ») et la revue des propriétaires du
code. Sans lui, une CI rouge n'empêche pas de fusionner. `socle state` dit
si la CI est exigée.

### Retirer un état de démarrage en double

Si le projet avait déjà son propre hook `SessionStart`, l'installeur le
signale : chaque session recevrait deux états qui se recoupent. Retirer ce
hook de `.claude/settings.json`, ou n'y garder que ce qui est propre au
projet. C'est un réglage de l'agent, modifié par l'humain seul.

### Mettre à jour le socle

Relancer la commande d'installation depuis une copie à jour du moteur. Le
moteur est remplacé en bloc ; les fichiers du projet ne sont jamais
écrasés, et le diff de la politique est montré sans la modifier. Les
fichiers protégés changés par la mise à jour s'approuvent ensuite
(`socle approve`), puis se commitent.

## Avec BMAD Method

Quand BMAD Method est installé dans le projet, il planifie (brief, PRD,
architecture, epics, stories, specs, sprint) et le socle prouve et retient.
L'usage courant :

- **Lancer un workflow de BMAD** comme d'habitude, en le nommant à l'agent
  (par exemple le workflow de construction, `bmad-build`). L'installeur du
  socle a posé la personnalisation de chaque skill de BMAD : à
  l'activation, l'agent lit l'état du socle ; à la fin du workflow, il tient
  la mémoire à jour et termine avec les contrôles verts.
- **Approuver une spec.** Quand le workflow s'arrête pour faire approuver
  une spec, répondre dans la conversation. L'agent consigne l'approbation
  mot pour mot, en décision prise en séance qui cite la spec, avant d'écrire
  le code. Une spec qui exige cette approbation ne quitte pas le brouillon
  sans elle, et son intention figée ne change plus sans une approbation
  nouvelle : le contrôle `bmad.approbation` le vérifie.
- **Les travaux reportés.** Ce que BMAD reporte (sa liste des travaux
  reportés) entre au backlog du socle par `python3 .socle/socle
  bmad-import`, que l'agent lance ; le contrôle `bmad.reports` refuse un
  report resté hors du backlog. Le backlog reste la seule liste des
  trouvailles.
- **Ce que l'état montre en plus** : les specs non terminées, les stories en
  cours ou en revue, les actions de rétrospective ouvertes, et les skills
  de BMAD sans la personnalisation du socle.
- **Les fichiers de BMAD** (ses skills, ses scripts) sont déclarés tiers dans
  `.socle/guardrails.toml` (`[thirdparty] paths`) et échappent aux contrôles.
  Ses documents de planification, eux, sont contrôlés comme le reste.
  Déclarer d'autres fichiers tiers est un assouplissement : il exige une
  demande validée.
- **Mettre à jour BMAD** relève de BMAD
  (`npx bmad-method install --action update`) ; relancer ensuite
  l'installation du socle repose sa personnalisation sur les skills
  nouveaux.

## Quand un contrôle refuse

Chaque refus dit ce qu'il a vu et comment en sortir. Les plus courants :

| Ce qui refuse | Signification | Conduite à tenir |
| --- | --- | --- |
| `protege.fichiers`, au commit | un fichier protégé a changé sans validation | si le changement vient de l'humain : `socle approve --text "<raison>"` ; s'il vient de l'agent : une demande |
| `cliquet.garde-fous` | un seuil a été relâché | le rétablir, ou une demande validée qui cite la clé |
| `tests.attendus` | une valeur attendue a changé, ou un test a disparu | une demande validée qui nomme le test, ou une spécification changée par l'humain |
| `tests.code-teste`, en CI | une fonction publique sans test qui la nomme | écrire le test, ou `Dispense-test: f — <raison>` dans le message du commit |
| `tests.regression`, en CI | un correctif sans test qui échoue sur le commit précédent | écrire ce test |
| `docs.correspondance` | du code associé à un document a changé sans lui | mettre le document à jour, ou `Dispense-doc: <raison>` dans le commit qui change ce code |
| `memoire.lectures` | une empreinte citée ne correspond plus | relire l'entrée ou l'index (`socle show`), citer l'empreinte affichée |
| `memoire.collisions` | un identifiant pris par la branche l'a été aussi sur la branche par défaut | `socle renumber <ID>`, qui attribue le prochain libre et reporte les citations |
| `memoire.retard`, en fin de tour | du code a changé et la mémoire non | mettre à jour le chantier actif, le journal ou le backlog |
| fin de tour refusée, « Pour toi : » | le dernier message de l'agent n'a pas son récapitulatif | terminer par le récapitulatif et les deux lignes |
| `prive.verrou` | le verrou du dépôt compagnon manque ou retarde | `socle private lock` ; sans dépôt en place, `socle private install --repo <adresse>`, par l'humain |
| `mutation.couverture` | un module qui porte du code n'a pas de plafond | l'y inscrire « à mesurer », puis `socle mutation-run --record`, ou reprendre le plafond du dernier balayage planifié |
| `mutation.vivante`, en CI | le balayage planifié est suspendu, ou ne tourne plus depuis quinze jours | le réactiver dans l'onglet Actions de GitHub et le lancer à la main ; c'est un geste de l'humain |
| `bmad.reports` | un travail reporté par BMAD n'est pas au backlog | `socle bmad-import` |
| push refusé, relecture | la politique exige la relecture de l'humain | l'humain relit ce qui part ; l'agent consigne son accord |

Un hook peut se contourner localement (`--no-verify`) ; la CI exécute tout,
et l'agent n'a pas le droit de contourner un hook. La CI n'arrête rien
d'elle-même : une CI rouge n'empêche la fusion que si la branche par défaut
l'exige (voir « Protéger la branche par défaut »).

## Référence

### Les commandes

| Commande | Usage |
| --- | --- |
| **Pour l'humain** | |
| `help` | ce guide |
| `install` | installer ou mettre à jour le socle |
| `init` | initialiser la mémoire depuis un cadrage, le dépôt existant, ou rien |
| `state` | l'état du projet, calculé à chaque appel |
| `answer` | répondre à une demande |
| `decision` | consigner une décision prise en séance |
| `approve` | approuver ses propres changements protégés (humain seul) |
| `reviewed` | consigner la relecture avant publication |
| `private install` | mettre en place le dépôt compagnon (humain seul) |
| **Pour l'agent** | |
| `new`, `next-id` | ajouter une entrée à la mémoire, avec son identifiant calculé |
| `show`, `url` | afficher une entrée avec son empreinte ; donner le lien d'un fichier |
| `verify`, `check`, `checks` | lancer les outils du langage et les contrôles ; lister les contrôles |
| `private` | état de la mémoire privée, verrou, termes, bascule d'une entrée |
| `mutation-run`, `mutation-verdict` | lancer le balayage de mutation et juger ses survivants |
| `renumber`, `archive` | renuméroter une entrée en collision ; ranger les sujets clos |
| `bmad-import` | faire entrer au backlog les travaux reportés par BMAD |
| **Internes** | |
| `hook`, `ci`, `selftest`, `fingerprint` | les hooks, la CI, l'auto-test, l'empreinte du moteur |

`python3 .socle/socle <commande> --help` détaille les options de chacune.

### Les seuils et le cliquet

`.socle/guardrails.toml` porte les seuils des contrôles : les budgets de
taille de chaque couche de la mémoire, les plafonds de mutation par module,
les correspondances entre code et documentation, les valeurs liées à leur
source, la taille minimale d'une copie, les chemins de spécification, les
fichiers tiers. Le cliquet compare chaque clé à celle de la base, avec un
sens par clé (un budget plus bas est plus strict, une liste d'exclusions
plus courte aussi). Durcir est libre ; relâcher fait échouer la CI tant
qu'une demande validée ne cite pas la clé. Une clé inconnue qui change
compte comme un relâchement.

Les fichiers protégés (la politique, l'adaptateur, le verrou du moteur, les
hooks, la CI, les réponses de l'humain) ne changent qu'avec une validation
qui cite leur chemin et leur empreinte nouvelle.

### Les contrôles

`python3 .socle/socle checks` liste chaque contrôle, les étages où il
s'exécute et ce qu'il vérifie.
