# Essai à blanc du socle sur chess, 11 novembre 2026

Le compte rendu de l'agent de la session de chess, recopié par Théo dans la
session du socle, tel quel, au numéro de version près. L'essai a installé la version publiée du socle
sur une branche locale de chess, sans rien pousser, puis a remis le dépôt
dans son état de départ.

```text
## Compte rendu de l'essai à blanc — socle publié sur theodubus/chess

Contexte. Socle 1d96f26, chess à 53ae7a7 (= main), branche locale essai-socle, session cloud Claude Code (CLAUDE_CODE_REMOTE=true), Python 3.11.17, Node 22.22.0, Rust 1.98.1 épinglé, 4 processeurs.

| étape | code | durée |
| install --adoption --adapter auto | 0, « TOUT PASSE » | 12 s |
| init --repo (14 faits, D-0001 à 5 questions) | 0 | 0,3 s |
| commit local (trailers Socle-Agent, Socle-Hooks posés) | 0 | 10 s |
| verify --fast | 1 | 194 s |
| ci | 1 | 252 s |
| hook pre-push, simulé sur son entrée standard, rien poussé | 1 | 225 s |

L'auto-test passe : 134 cas sur 134. Les tests et le tools/verify.sh --rapide de chess passent encore, socle posé.

### 1. Bloquant

1.1 — L'adaptateur JavaScript est détecté à cause de ui/ et lancé à la racine.
- Le JavaScript de chess vit entièrement sous ui/, avec son package.json, son CLAUDE.md et sa CI (ui.yml). La racine n'a pas de package.json.
- npx vitest run à la racine : 88 fichiers de test en échec sur 95 (Cannot find package 'chess.js'…). C'est le seul contrôle rouge de verify --fast, de ci et du pre-push.
- npm ci à la racine rend 1 (EUSAGE, pas de package-lock.json). Le socle.yml posé le lance à l'étape « Dépendances » : la CI échouerait avant d'atteindre socle ci.
- L'installeur a pourtant rendu 0 et « TOUT PASSE » : son audit lance check --stage ci, pas les capacités.
- Une session qui installerait pour de bon ne pourrait ni pousser ni corriger : socle.yml et l'adaptateur sont protégés.
- Effets de bord : npx télécharge un vitest qui n'est pas celui que ui/package.json épingle, et crée node_modules/.vitest-cache à la racine (37 Mo).
- Non testé : --adapter rust. Les trois capacités Rust ont passé, donc verify --fast devrait passer (inférence, confiance moyenne).

1.2 — Les hooks de l'agent se chargent dans la session qui installe, et refusent la remise en état.
- Le guide dit que la session qui installe tourne sans les hooks. Ici, PreToolUse a tiré dès l'appel d'outil suivant, 16 s après l'écriture de .claude/settings.json (trace à mon identifiant de session).
- À l'étape 5, le hook a refusé deux commandes : la restauration de .claude/settings.json par le shell, puis git rm --cached .socle.
- Seul un retour par git switch vers la branche d'origine est passé. Le hook s'est alors déchargé aussitôt.
- Risque non rencontré : si le harnais avait gardé le hook chargé après la disparition de .socle/socle, python3 .socle/socle hook … aurait rendu 2 (fichier introuvable), ce qui bloque chaque appel d'outil et la fin de tour.
- Le prompt d'essai devrait dire : revenir par changement de branche, jamais fichier par fichier.

### 2. Gênant, sans m'arrêter

À trancher par Théo avant l'installation réelle :
- La fusion est refusée à l'agent. Le hook, simulé sur mcp__github__merge_pull_request, répond deny : « une demande validée ne la débloque pas ». Sur chess, l'agent fusionne lui-même ses PR à CI verte, par consigne permanente de Théo. Seul [irreversible] tools de policy.toml, réservé à l'humain, le lève.
- Le budget de CLAUDE.md n'a que 66 octets de marge : 138 934 octets pour 139 000, et il ne peut que baisser. Chess y ajoute du texte à presque chaque verdict ; le premier ajout casserait memoire.budgets.
- ui/ et les autres agents. D'autres sessions (branches codex/…, ccr-…) travaillent sous ui/ sans connaître le socle. Le job « Socle » jugerait leurs PR, par exemple hooks.trace sur leurs commits co-signés Claude. Non testé ; [thirdparty] paths = ["ui/**"] est peut-être la réponse.
- Deux états au démarrage, signalé par l'installeur : tools/etat.sh (7 097 octets, il porte la feuille de route validée) et socle state.

Le reste :
- Coût par tour. Deux hooks Stop relanceraient chacun cargo test --workspace (~3 min) quand du code change, et le pre-push une troisième fois.
- Mutation en double. Chess a déjà mutation.yml : un job par fichier, --profile mutants, plafonds mesurés avec leurs raisons dans .github/mutation-baseline.txt.
  - socle-mutation.yml balaie les dix modules dans un seul job de 350 min, sans ce profil. search.rs seul prend 145 à 180 min chez chess : dépassement probable (inférence, confiance moyenne, non lancé).
  - Les dix plafonds partent « à mesurer » ; --mutation-caps n'était pas dans le prompt, et le fichier de chess n'est pas en TOML.
- Faits d'audit. 11 des 14 faits sont « Une CI GitHub existe : X.yml », dont 7 ne sont pas des CI (6 outils de mesure en workflow_dispatch, 1 balayage planifié). Ils sont relus à chaque session.
- Branches de données. L'état propose d'examiner reseau/n20d ; les reseau/… sont des dépôts de réseaux, jamais fusionnés. keep_branches est à remplir à l'installation.
- gh n'est pas authentifié en session cloud (GitHub passe par les outils MCP) : l'état affiche « CI : non disponible ». Il affiche aussi « CI du socle NON exigée » ; je n'ai pas vérifié comment il le sait sans gh.
- tests.attendus. Changer une valeur de la table de confrontation du réseau embarqué donne un avertissement à l'étage agent, pas un échec. Chess le fait à chaque réseau candidat. L'étage CI n'a pas été testé.
- Identifiants de journal. L'installeur ouvre J-2026-11-11-A ; le carnet actuel de chess numérote ses entrées de la même façon. Collision possible le jour de l'import.
- Avertissements d'adoption, justes tous les quatre : deux chemins morts dans tools/README.md (lignes 4074 et 17887), deux assertions de déterminisme vues comme tautologiques (search.rs:4290, tools/src/bin/spsa.rs:461).

### 3. Ce que l'installeur a fait de CLAUDE.md

- Il l'a gardé comme source, sans le renommer : 64 fichiers du projet le nomment. Pas d'AGENTS.md.
- Il a ajouté sa section en fin de fichier, entre ses marqueurs : +173 lignes, 125 736 → 138 934 octets, aucune ligne existante modifiée. ui/CLAUDE.md n'est pas touché.
- Il a posé le budget à 139 000 octets.
- Les tests de chess qui lisent la documentation passent avec la section.
- Contradictions avec le texte de chess, à régler à la migration : « l'humain fusionne » contre l'agent qui fusionne ; socle state contre tools/etat.sh ; socle verify --fast contre tools/verify.sh ; un second titre « Ce qui tourne tout seul ».

### 4. Étapes de la CI de chess que l'adaptateur automatique ne lance pas

L'adaptateur Rust lance cargo fmt --check, cargo clippy et cargo test --workspace, soit les trois premières étapes de ci.yml. Il ne lance pas :
- ci.yml, job « Moteur » : .github/mutation-verdict-test.sh ; tools/balayage-vivant-test.sh et tools/balayage-vivant.sh ; cargo test --workspace --release ; cargo test --workspace --release -- --ignored (perft, tournoi, référence du banc, rustines) ; bench 4 ; tools/binaires-test.sh et tools/binaires.sh dist.
- ci.yml, autres jobs : les binaires sous Windows, Mac Intel et Apple Silicon ; « le même arbre sur chaque système » ; clippy sur la dernière stable.
- Autres workflows au push : nnue-train.yml (compile tools/nnue-train, espace de travail à part), pages.yml (build wasm et sa vérification), ui.yml (npm ci, lint, typecheck, tests, build, dans ui/).
- tools/verify.sh, en local : ref-test.sh, mettre-en-commun-test.sh, paires-test.sh, plis-test.sh, etat-test.sh, et verify-hooks.sh en mode complet.

Rien n'est perdu sur GitHub, l'installeur laisse ces workflows en place. La perte est locale : le Stop et le pre-push du socle ne couvrent que les trois étapes cargo.

### 5. Durée de verify

| commande | durée | code |
| socle verify --fast | 194 s | 1 |
| dont cargo test --workspace (debug, cache chaud, mesuré à part) | 180 s | 0 |
| dont npx vitest run | 7,6 s | 1 |
| dont fmt et clippy (cache chaud) | 0,5 s | 0 |
| socle ci | 252 s | 1 |
| tools/verify.sh --rapide de chess, même conteneur | 176 s | 0 |

verify sans --fast n'a pas été lancé ; toutes les capacités posées sont marquées fast.

### 6. Taille de l'état (socle state)

103 lignes, 4 934 octets, calculé en 2,3 s, mémoire encore vide : état dérivé 25 lignes et 1 803 octets ; active.md 14 lignes et 248 octets ; canonical.md (les 14 faits d'audit) 64 lignes et 2 883 octets.

### 7. Remise en état

- Retour par git switch, puis suppression de la branche locale, de core.hooksPath, de .git/socle/, des restes de .socle/, du node_modules/ de la racine et de /tmp/socle.
- Contrôle : empreintes des 713 fichiers identiques à la photographie de départ, hors la trace des hooks propres à chess.
- Restent hors du dépôt : le cache npx (41 Mo sous ~/.npm/_npx) et le commit d'essai, inatteignable dans le conteneur.
```
