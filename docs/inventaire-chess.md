# Inventaire : ce que `chess` contient de générique

Jalon 1 du cadrage. Lecture du dépôt `theodubus/chess` au commit `689ce77`
(fusion de la revue de documentation, 7 oct. 2026), en lecture seule. Les
chemins de `chess` sont écrits `chess:chemin` pour ne pas être pris pour des
chemins de ce dépôt.

La porte de ce jalon est la validation humaine de cet inventaire, en file
dans `D-0001`.

## Ce qui a été mesuré

| Mesure | Valeur | Commande |
| --- | --- | --- |
| Fichiers suivis | 487 | `git ls-files \| wc -l` |
| `chess:CLAUDE.md` | 110 612 octets, 1 206 lignes | `wc -c`, `grep -c ''` |
| `chess:tools/README.md` | 726 061 octets, 9 446 lignes | idem |
| Scripts `chess:tools/*.sh` | 22, dont 8 auto-tests `*-test.sh` | `ls` |
| Vérifications rapides (fmt, clippy, tests debug) | passent, ~3 min dans le conteneur | `cargo fmt --check && cargo clippy … && cargo test --workspace` |

Le carnet de bord, lui, est privé et hors du dépôt : `chess:tools/etat.sh` lit
son adresse dans `chess:.claude/carnet.local`, ignoré par git. Il n'est pas
lisible d'ici. Le cadrage cite « un carnet de 720 Ko » : c'est presque
exactement la taille de `chess:tools/README.md`, qui porte les mesures, les
verdicts et les sections « EN VOL ». Lequel des deux le cadrage désigne est
une question posée dans la demande de validation, pas une correction.

## Générique : repris dans le socle

| Pièce de `chess` | Ce qu'elle fait | Ce qu'elle devient |
| --- | --- | --- |
| `chess:tools/etat.sh`, lancé par `SessionStart` | État dérivé de git au démarrage et après compactage ; renvois dérivés du fichier, sections épisodiques muettes quand absentes, structurelles en erreur | `socle state` et le hook `session-start`. Gardé : tout est dérivé, rien ne bloque le démarrage. Changé : il lit la mémoire au format du socle (backlog, demandes en attente, péremption) au lieu de titres de `README` |
| `chess:.claude/hooks/no-fabricated-sha.sh` | Refuse un SHA de 40 caractères inconnu dont le préfixe de 7 est connu | Repris à l'identique dans le hook `pre-tool-use`, étendu aux références de commit et aux identifiants de mémoire inventés |
| `chess:.claude/hooks/verify-on-stop.sh` | Refuse de finir un tour sur un arbre cassé ; laisse passer après trois échecs | Hook `stop` : contrôles du socle, puis capacités rapides de l'adaptateur si le code a bougé depuis la dernière vérification réussie. Les trois échecs deviennent le point 7 de la politique : on s'arrête, mais en escaladant |
| Trace `chess:.claude/hooks-fired.log` et `chess:tools/verify-hooks.sh` | Prouver que les hooks sont chargés, pas seulement corrects | Trace locale, plus le trailer `Socle-Hooks` que la CI exige sur chaque commit d'agent (`ADR-0005`) : dans `chess`, la trace est ignorée par git et la CI ne la voit pas |
| `chess:tools/verify.sh` | Toutes les étapes, même après un échec ; sortie complète d'un échec ; un seul code de sortie ; `--rapide` | `socle verify`, sur les capacités déclarées par l'adaptateur, plus les contrôles du socle |
| `chess:.github/mutation-baseline.txt` et `chess:.github/mutation-verdict.sh` | Cliquet : casse à la hausse, signale la baisse ; raison écrite de chaque plafond non nul ; un résumé absent casse | `[mutation.caps]` des garde-fous et `socle mutation-verdict` ; `tests/test_mutation.py` rejoue les cas fabriqués de `chess:.github/mutation-verdict-test.sh` |
| `chess:engine/tests/couverture_mutation.rs` | Tout fichier du moteur est dans la matrice et dans le plafond | Contrôle `mutation.couverture`, sur les modules que l'adaptateur déclare ; l'exemption « fichier sans fonction » devient une regex `has_code` |
| `chess:engine/tests/outillage_documente.rs` | Tout dispositif est nommé dans la doc, ensemble parcouru et non énuméré | Contrôle `docs.outillage` |
| `chess:engine/tests/bench_reference.rs` | Un chiffre de la doc confronté au binaire, dans TOUS les fichiers | Contrôle `docs.valeurs` : marqueur dans la doc, source fichier ou commande, avertissement sur une copie non marquée |
| `chess:engine/tests/pieges_fermes.rs` | Chaque piège archivé nomme un dispositif qui existe | Généralisé par les références vivantes (`fichier:`, chemins cités) et par la preuve exigée d'un fait mesuré |
| `chess:tools/etat-test.sh`, `chess:tools/ref-test.sh` et les autres `*-test.sh` | Une branche de refus qui ne sert qu'en cas de catastrophe s'éprouve sur des dépôts fabriqués | Le principe de l'auto-test : `socle selftest` injecte chaque défaut connu dans un clone jetable, avec un `origin` |
| La ligne « branches à faire supprimer par Théo » de `chess:tools/etat.sh`, et la consigne de `chess:CLAUDE.md` de dire à chaque récap ce qui revient à Théo | Les actions que seul l'humain peut faire, calculées quand elles se calculent | Classée d'abord « spécifique », à tort (`J-2026-10-10-M`) : « ce qui revient à l'humain », dans l'état et dans la ligne `Pour toi :` que le hook de fin de tour exige |
| Section « Ce qui compte comme preuve » de `chess:CLAUDE.md` | Une table affirmation → preuve exigée | Le statut « mesuré » et sa `preuve` obligatoire |
| Section « Ce qui tourne tout seul » de `chess:CLAUDE.md` | La table des dispositifs automatiques | La section du socle dans `AGENTS.md`, régénérée par l'installeur |
| Le texte barré `<s>…</s>` dans `chess:CLAUDE.md` | Une affirmation fausse se garde, barrée | Le fait réfuté, barré et conservé |
| Étapes de `chess:.github/workflows/ci.yml` | fmt, clippy, tests debug et release, critères `--ignored`, bench | L'adaptateur Rust maintenu pour fmt, clippy et tests ; le reste en `[[steps]]` propres au projet |

## Spécifique : reste dans `chess`

- La mesure de force : SPRT, arbitres de match, `chess:tools/timing.sh`,
  `chess:tools/plis.sh`, `chess:tools/paires.sh`,
  `chess:tools/mettre-en-commun.sh`, les workflows de match et de force, NNUE.
  Leur patron, lui, est générique : un refus éprouvé sur des cas fabriqués.
- Les deux binaires et l'empreinte de recherche par système.
- Les rustines de `chess:tools/attic/` et leur table d'applicabilité :
  spécifique, mais le principe (une affirmation vérifiable est vérifiée) est
  celui de `docs.valeurs`.
- L'exclusion des branches `codex/…` de `chess:tools/etat.sh` : propre au flux
  de ce dépôt (le socle la permet par `[human] keep_branches`).
- `chess:tools/balayage-vivant.sh` (le cliquet de mutation ne peut pas signaler
  sa propre absence) : générique, mais il dépend de l'API GitHub. Reporté au
  backlog avec le workflow de mutation générique.

## Ce que `chess` n'a pas et que le socle ajoute

- Un format de mémoire lisible par script, en cinq couches, avec un backlog.
- Le contrat des demandes humaines et son lint.
- Un cliquet sur tous les seuils, pas seulement la mutation.
- L'ajout seul du journal et des décisions, vérifié contre la base.
- L'empreinte du moteur.
- Le refus des copies, et la correspondance code ↔ doc : `chess` n'a qu'un
  signal (« N fichiers `.rs`, 0 `.md` »), qui constate sans bloquer.
- Les tests creux, les valeurs attendues, le test de régression rejoué sur
  le commit parent.

## Ce qui en découle pour les budgets

`chess:CLAUDE.md` réinjecté à chaque session fait 110 612 octets, environ
28 000 jetons. Le budget par défaut d'`AGENTS.md` est de 16 000 octets. En
mode adoption, l'installeur fixe le budget au niveau actuel et le cliquet ne
le laisse que baisser.
