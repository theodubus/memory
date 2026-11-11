# Les prompts de l'installation du socle sur chess

Deux prompts, à coller dans la session de chess, qui tourne sur un autre
compte et ne lit pas ce dépôt. Ils portent les six décisions de Théo du
11 novembre (D-0100) et ce que l'essai à blanc a appris
(`docs/fabrication/chess/essai-a-blanc-2026-11-11.md`). Le premier installe ;
il commence comme un essai, et ne pousse rien avant que sa porte ait passé.
Le second, dans une session neuve une fois l'installation fusionnée, pose la
feuille de route (D-0094).

## 1. Installer

````text
Installe le socle sur ce dépôt, pour de bon, en mode adoption. Tu es la session qui installe ; le travail continuera ensuite dans une session neuve.

Le socle a été corrigé depuis ton essai à blanc du 11 novembre : ses deux constats bloquants et plusieurs gênes sont réglés dans la version publiée. Cette installation commence donc comme un essai : rien n'est poussé avant que l'étape 5 ait passé. Au premier constat bloquant, arrête-toi, ne pousse rien et rends-moi compte.

N'ajoute aucun dépôt à la session : le dépôt public du socle se clone, c'est tout.

## Mes décisions, déjà prises (Théo, 11 novembre)

Consigne-les dans la mémoire du projet une fois le socle posé, avec ce texte comme citation. Ne les rouvre pas ; pose une demande pour tout ce qu'elles ne couvrent pas.

1. L'adaptateur : celui de chess, propre au projet, donné à l'installeur en fichier. Je le validerai en le lisant dans la pull request.
2. Le dossier ui/ est déclaré tiers : aucun contrôle du socle ne le juge, et les commits des autres agents qui ne touchent que lui n'ont pas à porter la trace des hooks.
3. L'agent fusionne lui-même ses pull requests à CI verte, comme aujourd'hui sur chess. J'ajoute moi-même la ligne de politique qui le permet.
4. Le fichier d'instructions (CLAUDE.md) garde sa marge de budget à l'installation. Le premier sujet de chess sera de déplacer le carnet de bord vers la mémoire : CLAUDE.md ne gardera que les règles de travail.
5. Le balayage de mutation de chess (mutation.yml) est gardé tel quel. Celui du socle n'est pas posé pour l'instant.
6. Les branches de réseaux (reseau/…) et celles des autres agents sont à garder : elles ne doivent jamais être proposées à la suppression.

## Étapes

0. Départ : arbre propre, à jour de main. Crée ta branche de travail. Note le commit de départ.

1. Clone le socle et lis ce qui a changé :
   git clone --depth 1 https://github.com/theodubus/socle /tmp/socle
   Lis la section « Installation » de /tmp/socle/README.md et le contrat des adaptateurs, /tmp/socle/socle/adapters/README.md.

2. Écris l'adaptateur de chess dans un fichier hors du dépôt, /tmp/chess.toml :
   - pars de l'adaptateur Rust maintenu, /tmp/socle/socle/adapters/rust.toml, qui est à jour ;
   - ajoute ce qui est propre à chess, d'après l'adaptateur préparé en octobre, collé à la fin de ce message : les sources, la capacité de régression et les étapes [[steps]]. Vérifie chaque étape contre l'état actuel du dépôt (tools/verify.sh, le job « Moteur » de ci.yml) : avec --fast, le socle doit lancer ce que lance tools/verify.sh --rapide ; sans --fast, ce que lance le job « Moteur » ;
   - déclare la capacité de mutation absente, avec pour remplacement le balayage de chess (.github/workflows/mutation.yml), décision 5 : le socle ne pose alors pas le sien ;
   - ne décris rien de ui/ : décision 2.

3. Installe :
   PYTHONPATH=/tmp/socle python3 -m socle install --target . --adoption --adapter /tmp/chess.toml --owner @theodubus --human Théo
   - L'installeur juge l'adaptateur avant d'écrire quoi que ce soit. S'il le refuse, corrige le fichier et relance.
   - Dès que .claude/settings.json est écrit, les hooks du socle te jugent : un fichier protégé ne se corrige plus à la main. Pour revenir en arrière, commite sur ta branche, change de branche, puis relance l'installeur avec les bonnes options ; jamais fichier par fichier.
   - L'installeur doit dire que le JavaScript de ui/ ne reçoit pas d'adaptateur, et poser le budget de CLAUDE.md avec une marge d'un dixième. Si ce n'est pas le cas, c'est un constat bloquant.

4. Suis les étapes « Et maintenant » de l'installeur, dans l'ordre, puis applique mes décisions :
   - ui/ tiers (décision 2) : [thirdparty] paths = ["ui/**"] dans les garde-fous, par la procédure que le guide donne pour une session sans terminal (python3 .socle/socle help) ;
   - la politique (décisions 3 et 6) : tu ne peux pas l'écrire. Prépare-moi les lignes exactes, que j'ajouterai moi-même sur la branche depuis GitHub : dans [irreversible], la liste tools sans la fusion de pull request ; dans [human], keep_branches avec les branches de réseaux et celles des autres agents, dans la syntaxe que le moteur accepte ;
   - init --repo : laisse l'audit poser ses faits. Les workflows doivent tenir en un seul fait ; s'il y en a un par workflow, c'est un constat.

5. La porte, avant tout push. Tout doit passer :
   - python3 .socle/socle verify --fast
   - python3 .socle/socle ci
   - tools/verify.sh --rapide, celui de chess
   Donne-moi les durées. Si l'un échoue : arrête-toi, ne pousse rien, rends compte avec la sortie exacte.

6. Commite, pousse, ouvre la pull request. Sa description dit ce que l'installation ajoute, et reprend ce qui me revient.

7. Rends-moi compte, court :
   - ce qui me revient, dans l'ordre : les lignes de politique à ajouter (texte exact, et lien vers le fichier sur la branche), les fichiers protégés à approuver, l'adaptateur à lire, la pull request à fusionner, la branche par défaut à protéger ;
   - les contradictions entre la section du socle et le texte de chess dans CLAUDE.md (qui fusionne, socle state et tools/etat.sh, socle verify et tools/verify.sh, le titre en double) : corrige dans le texte de chess celles que mes décisions tranchent, liste les autres ;
   - ce qui tourne en double à chaque fin de tour (les hooks de chess et ceux du socle lancent chacun les tests) : mesure-le et propose, sans rien retirer ;
   - les avertissements d'adoption, tels quels ;
   - tout écart à ce prompt.

N'ouvre pas la feuille de route dans cette session : elle se pose dans la session suivante, avec moi.

## L'adaptateur préparé en octobre, pour l'étape 2

# Adaptateur PROPOSÉ pour chess — à valider par Théo à l'installation.
#
# L'adaptateur Rust maintenu (moteur/socle/adaptateurs/rust.toml), plus les
# étapes propres à chess, reprises une à une de chess:tools/verify.sh et de
# chess:.github/workflows/ci.yml. Avec lui, `socle verify` exécute ce que la CI
# de chess exécute (porte du jalon 3, voir docs/fabrication/chess/README.md).

language = "rust"
name = "Rust (cargo) — chess"
maintained = false
sources = ["engine/src/**/*.rs", "tools/src/**/*.rs", "tools/nnue-train/src/**/*.rs"]

ci_setup = """
      - name: Toolchain Rust
        run: |
          rustup show active-toolchain
          rustc --version && cargo --version
"""

[capabilities.format]
command = "cargo fmt --all -- --check"
fast = true

[capabilities.lint]
command = "cargo clippy --all-targets --all-features -- -D warnings"
fast = true

[capabilities.build]
absent = "couverte par `lint` : clippy compile toutes les cibles, tests compris"
replacement = "capacité `lint`"

[capabilities.tests]
command = "cargo test --workspace"
fast = true

[capabilities.mutation]
# Comme chess:.github/workflows/mutation.yml : un fichier par job, `--profile
# mutants` (release sans LTO), `tools/` exclu à dessein.
tool = "cargo-mutants"
command = "cargo mutants --file {module} --profile mutants -j 2"
modules = ["engine/src/*.rs"]
has_code = '\bfn\b'
parser = "cargo-mutants"

[capabilities.coverage]
absent = "signal secondaire ; chess juge par la mutation et par le SPRT"
replacement = "capacité `mutation`"

[capabilities.regression]
command = "cargo test --release {test_args}"
test_arg = "--test {stem}"
test_paths = ["engine/tests/*.rs"]

[tests]
paths = ["engine/tests/*.rs", "engine/src/**/*.rs", "tools/src/**/*.rs"]
function = '^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?(?:unsafe\s+)?fn\s+(\w+)'
attribute = '^\s*#\['
comment = '^\s*//'
marker_attribute = '#\[(?:\w+::)*test\b'
block = "braces"
assertion = '\b(?:assert|assert_eq|assert_ne|debug_assert\w*|panic|unreachable|assert_matches)!|#\[should_panic'
ignore = '#\[ignore\b'
ignore_reason = '#\[ignore\s*=\s*"[^"]{3,}"\s*\]'
tautology = [
  'assert(?:_eq)?!\(\s*([^,()]+(?:\([^()]*\))?)\s*(?:,|==)\s*\1\s*[,)]',
  'assert!\(\s*true\s*\)',
]

# Étapes propres à chess, dans l'ordre de chess:tools/verify.sh.
[[steps]]
name = "verdict de mutation (auto-test)"
command = ".github/mutation-verdict-test.sh"
fast = true

[[steps]]
name = "références de mesure"
command = "tools/ref-test.sh"
fast = true

[[steps]]
name = "mise en commun"
command = "tools/mettre-en-commun-test.sh"
fast = true

[[steps]]
name = "paires"
command = "tools/paires-test.sh"
fast = true

[[steps]]
name = "plis appariés"
command = "tools/plis-test.sh"
fast = true

[[steps]]
name = "balayage vivant"
command = "tools/balayage-vivant-test.sh"
fast = true

[[steps]]
name = "état calculé, branches"
command = "tools/etat-test.sh"
fast = true

[[steps]]
name = "deux binaires, la comparaison"
command = "tools/binaires-test.sh"
fast = true

[[steps]]
name = "tests (release)"
command = "cargo test --workspace --release"

[[steps]]
name = "critères d'acceptation"
command = "cargo test --workspace --release -- --ignored"
timeout = 5400

[[steps]]
name = "bench"
command = "cargo run --release --bin shallowred -- bench 4"

[[steps]]
name = "deux binaires, le même arbre"
command = "tools/binaires.sh dist"
timeout = 5400

# Dans chess:tools/verify.sh complet, pas dans sa CI : l'auto-test de ses
# propres hooks, qui restent en place à côté de ceux du socle.
[[steps]]
name = "hooks de chess"
command = "tools/verify-hooks.sh"
````

## 2. Dans une session neuve, une fois l'installation fusionnée

````text
Le socle est installé sur ce dépôt. Deux choses dans cette session, dans cet ordre, avec moi.

1. La feuille de route.
   - Lis l'état que le socle t'a donné au démarrage, puis la feuille de route actuelle : tools/etat.sh et le carnet de bord dans CLAUDE.md.
   - Avant d'en écrire une ligne, relis-la d'un œil critique et rends-moi ton avis : ce qui est daté ou déjà fait, ce qui manque, l'ordre que tu changerais et pourquoi, les étapes dont la fin n'est pas mesurable, les risques que je ne vois pas. Pose tes questions ouvertes en une demande (python3 .socle/socle new request --questions) et attends mes réponses.
   - Ensuite seulement, pose-la dans le backlog : un sujet par étape, ordonnés par « après », rangés en jalons, avec une priorité et un « Fait quand » mesurable. Rien d'autre ne fait foi ensuite : tools/etat.sh ne garde que ce que socle state ne calcule pas.

2. Le premier sujet : déplacer le carnet de bord de CLAUDE.md vers la mémoire.
   - CLAUDE.md ne garde que les règles de travail. Un fait mesuré va dans la mémoire canonique avec sa preuve, une décision dans une ADR, l'histoire dans le journal, ce qui reste à faire dans le backlog.
   - Par lots, le budget de CLAUDE.md baissé à chaque lot. Attention aux identifiants : le carnet numérote ses entrées comme le journal du socle.
   - Propose-moi le découpage avant de commencer.
````
