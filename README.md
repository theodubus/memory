# Socle

**Mémoire et garde-fous pour les agents de code qui entretiennent un projet
dans la durée.**

Le socle s'installe dans un dépôt qu'un agent de code (Claude Code, ou un
autre) fait évoluer de session en session. Il garde la mémoire du projet
dans le dépôt, la remet à l'agent à chaque session, et vérifie
automatiquement ce que l'agent produit. L'humain ne tranche que ce
qu'aucun contrôle ne peut trancher.

## Le problème

Un agent de code repart de zéro à chaque session. Sur un projet de
plusieurs semaines, il :

- **oublie** les décisions, les consignes et les écueils déjà rencontrés ;
- **laisse dériver** ses notes et la documentation par rapport au code ;
- **écrit des tests sans portée** : assertions tautologiques, tests
  désactivés, valeurs attendues ajustées pour passer ;
- **invente des références** : fichiers, commits ou identifiants qui
  n'existent pas ;
- **affaiblit les garde-fous** : un seuil relâché, une question tranchée à
  la place de l'humain.

Ces erreurs sont plausibles et silencieuses ; elles se découvrent tard.

## Le fonctionnement

L'agent écrit tout ; des contrôles automatiques vérifient ; l'humain
arbitre ce qui ne se vérifie pas.

**La mémoire.** Elle vit dans `memory/`, versionnée avec le code, dans un
format lisible par script :

| Couche | Contenu |
| --- | --- |
| Faits | ce qui est établi, chacun avec sa preuve |
| Chantier actif | le travail en cours et les prochaines étapes |
| Décisions | une décision par fichier, avec ses raisons |
| Journal | une entrée datée par événement, en ajout seul |
| Backlog | les sujets à traiter, un par fichier |
| Demandes | les décisions qui attendent l'humain, puis sa réponse |

À chaque session, l'agent reçoit l'état du projet, calculé depuis git et la
mémoire (commit, CI, backlog, ce qui attend l'humain), puis le chantier et
les faits.

**Les contrôles, à trois étages.** Une trentaine de contrôles vérifient que
toute référence citée existe, que la documentation suit le code, que les
tests affirment quelque chose et qu'aucun n'est affaibli en silence, que la
mémoire est tenue à jour. Ils s'exécutent pendant le travail de l'agent, au
commit, et en CI :

```mermaid
flowchart LR
    A(["L'agent<br/>travaille"]) --> E1
    E1["<b>1. Pendant le tour</b><br/>hooks de l'agent<br/><br/>refuse une action<br/>irréversible, une référence<br/>inventée, une fin de tour<br/>aux contrôles rouges"] --> E2
    E2["<b>2. Au commit, au push</b><br/>hooks git<br/><br/>juge ce qui part,<br/>trace les hooks de l'agent,<br/>arrête une fuite du privé"] --> E3
    E3["<b>3. Sur GitHub</b><br/>la CI<br/><br/>rejoue tout contre la base,<br/>et l'auto-test du socle"] --> F(["Fusion"])
```

**Les décisions réservées à l'humain.** Une politique, modifiée par
l'humain seul, fixe ce que l'agent décide et ce qu'il demande. Ce qui est
coûteux à défaire, irréversible, ou qui affaiblirait un garde-fou (relâcher
un seuil, supprimer un test) fait l'objet d'une **demande** : un document
qui se lit sans le contexte de la session, avec les options et une
recommandation. L'humain répond dans la conversation ; la réponse est
consignée mot pour mot.

**Le cliquet.** Chaque seuil peut être durci librement, jamais relâché sans
validation. Les fichiers qui encadrent l'agent (politique, hooks, CI) ne
changent qu'avec l'accord de l'humain.

Une session, de bout en bout :

```mermaid
%%{init: {"sequence": {"mirrorActors": false}}}%%
sequenceDiagram
    actor H as L'humain
    participant A as L'agent
    participant S as Le socle
    participant G as La CI
    A->>S: ouvre une session
    S-->>A: l'état du projet, le chantier en cours, les faits
    Note over A: écrit le code, les tests, la doc, la mémoire
    A->>S: termine son tour
    S-->>A: refusé : « F-0003 ne désigne aucune entrée »
    Note over A: corrige la référence
    A->>S: commite
    S-->>A: contrôles rapides : rien à signaler
    A->>G: pousse
    G-->>A: tous les contrôles, et l'auto-test : vert
    Note over A: voudrait relâcher un seuil : ce n'est pas à lui
    A->>H: une demande : la question, les options, sa recommandation
    H-->>A: « valider », consigné mot pour mot
```

## Avec BMAD Method

[BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD) est une méthode
de développement par agents : des workflows qui mènent un projet du brief au
code (PRD, architecture, epics, stories, specs). Elle organise le travail,
mais ne vérifie pas ce que l'agent produit et ne garde pas de mémoire hors
de ses documents. Le socle s'y associe sans modifier ses fichiers :

| BMAD Method planifie | Le socle vérifie et retient |
| --- | --- |
| brief, PRD, architecture, epics, stories, specs, sprint | faits, consignes, journal, backlog, décisions de l'humain |

- Les workflows de BMAD lisent l'état du socle au démarrage et terminent
  par ses contrôles.
- L'approbation d'une spec par l'humain est consignée comme une décision ;
  sans elle, la spec ne quitte pas le brouillon.
- Les travaux que BMAD reporte entrent au backlog du socle.
- Les documents de BMAD sont contrôlés comme le reste du projet.

```mermaid
%%{init: {"sequence": {"mirrorActors": false}}}%%
sequenceDiagram
    actor H as L'humain
    participant A as L'agent, dans un workflow de BMAD
    participant S as Le socle
    H->>A: lance le workflow de construction, avec le besoin
    A->>S: à l'activation, lit l'état du projet
    Note over A: BMAD : rédige la spec
    A->>H: demande l'approbation de la spec
    H-->>A: « j'approuve »
    A->>S: consigne l'approbation mot pour mot, avec la spec
    Note over A: BMAD : code et tests, relecture
    A->>S: fin du workflow : mémoire à jour, contrôles verts
    A->>S: fait entrer au backlog les travaux reportés
```

## Structure

L'installation ajoute à un projet :

```text
.socle/               le moteur, sa politique, ses seuils, son adaptateur, ses hooks git
memory/               la mémoire du projet, vide au départ
AGENTS.md             les instructions de l'agent (CLAUDE.md l'importe)
.claude/settings.json les hooks de Claude Code
.claude/skills/       les procédures rares du socle, que l'agent charge à la demande
.github/              la CI, le balayage de mutation hebdomadaire, CODEOWNERS
```

Le moteur est en Python 3.11+, sans dépendance. Il ne connaît ni le langage
du projet, décrit par un adaptateur, ni l'agent, branché par ses hooks.

Ce dépôt contient le produit (`engine/socle/`, seule partie copiée dans un
projet) et son atelier de fabrication (`tests/`, `bench/`,
`docs/fabrication/`). Il est lui-même équipé du socle : sa mémoire est
l'historique de la fabrication.

## Installation

Prérequis : Python 3.11+ et git ; un projet en Rust, Python, JavaScript ou
TypeScript, Go, Java, Ruby, PHP ou C# (un autre langage se décrit par un
adaptateur) ; Claude Code et GitHub pour les trois étages ; avec BMAD,
Node.js 20.12+ et `uv`.

```sh
git clone --depth 1 --filter=blob:none --sparse https://github.com/theodubus/memory /tmp/socle
git -C /tmp/socle sparse-checkout set engine
cd <projet>
PYTHONPATH=/tmp/socle/engine python3 -m socle install --target . --owner @<propriétaire>
```

| Option | Effet |
| --- | --- |
| `--with-bmad` | installe aussi BMAD Method, à la version éprouvée avec le socle |
| `--adoption` | équipe un projet existant : les contrôles qui échouent passent en avertissement, puis ne peuvent que durcir |
| `--private compagnon` | ajoute une mémoire privée, dans un dépôt privé à part |
| `--review lots` | exige la relecture de l'humain avant toute publication |
| `--language en` | mémoire et messages en anglais |
| `--adapter <nom>` | impose le langage au lieu de le déduire |

L'installeur termine par les étapes suivantes, chacune avec sa commande. La
suite est décrite dans [le guide d'utilisation](engine/socle/HELP.md),
copié dans le projet et affiché par `python3 .socle/socle help`.

## État du projet

Version <!-- valeur:version -->0.1.0<!-- /valeur -->, en développement.
L'étage de l'agent n'existe que pour Claude Code. L'installation passe par
un clone de ce dépôt ; un dépôt de distribution ne contenant que le produit
est prévu pour la première version stable.

## Documentation

| Document | Portée |
| --- | --- |
| Ce README | ce qu'est le socle, son fonctionnement, sa structure, son installation |
| [Le guide d'utilisation](engine/socle/HELP.md) | l'usage d'un projet équipé, étape par étape, et la référence des commandes |
| [Le format de la mémoire](engine/socle/FORMAT.md) | la spécification de la mémoire |
| [La spécification des adaptateurs](engine/socle/adapters/README.md) | comment décrire un langage |

La fabrication du socle est documentée dans [l'atelier](docs/fabrication/README.md).
