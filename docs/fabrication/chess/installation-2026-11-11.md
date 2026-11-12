# Installation du socle sur chess, 11 novembre 2026 : l'arrêt à l'étape 3

Le compte rendu de l'agent de la session de chess, recopié par Théo dans la
session du socle, tel quel, au numéro de version près. La session suivait le
premier prompt de `docs/fabrication/chess/prompt-installation.md`, et s'est
arrêtée sur une condition de son étape 3 que l'installeur ne pouvait pas
tenir : son message sur un langage en sous-dossier n'existe qu'en détection
automatique. L'erreur était dans le prompt ; l'installation, elle, était
conforme.

```text
## Installation réelle du socle sur chess — arrêt à l'étape 3, sur un constat bloquant au sens du prompt

Contexte. Socle b6f6696 (publié depuis 3bdf9ca), chess à 53ae7a7 (= main), session cloud Claude Code, branche de travail claude/project-documentation-review-denp0n. Rien n'est commité ni poussé : l'installation est dans l'arbre de travail.

### Le constat

Le prompt dit : « L'installeur doit dire que le JavaScript de ui/ ne reçoit pas d'adaptateur […]. Si ce n'est pas le cas, c'est un constat bloquant. »

- Ce qui manque. Avec --adapter /tmp/chess.toml, la sortie de l'installeur ne contient aucune ligne sur le JavaScript de ui/. Elle dit seulement « adaptateur : chess ».
- La cause, lue dans installer.py. sous_dossiers_sans_adaptateur n'est appelé que sous if detectes:, donc seulement quand l'installeur détecte lui-même les langages. Avec un adaptateur donné en fichier, il ne détecte rien et se tait. Le README dit d'ailleurs « En automatique ».
- L'effet sur ce qui est posé : aucun. Pas de dossier .socle/adapters/, et .github/workflows/socle.yml n'a que l'étape « Toolchain Rust » avant le socle, sans npm ci.

L'autre condition de l'étape 3 est tenue : « budget de CLAUDE.md, gardé comme source : 153000 octets pour 138716, sa taille plus un dixième, arrondie au millier supérieur ».

### Ce qui a passé

- Étape 0. Arbre propre, à jour de main.
- Étape 2. L'adaptateur tient le contrat (ecarts_au_contrat rend une liste vide). Ses onze étapes sans compilation passent dans un clone neuf, HOME vide et sans réglage git, comme sur un runner.
- Étape 3. Installeur : code 0 en 23 s, audit « TOUT PASSE », 107 fichiers protégés posés.
  - Le balayage de mutation du socle n'est pas posé (capacité déclarée absente).
  - CLAUDE.md est gardé comme source (64 fichiers le nomment), section du socle ajoutée.
  - L'installeur signale le double état au démarrage (tools/etat.sh).
  - Adoption : tests.creux et memoire.references en avertissement, les quatre mêmes constats qu'à l'essai (deux chemins morts dans tools/README.md, deux assertions de déterminisme).
- Contrôles de l'étage agent sur l'arbre non commité : code 0.
- Lu sans le lancer : l'audit de init --repo regroupe les workflows en un seul fait (B-0170).

### L'adaptateur donné : écarts à celui d'octobre

Base : rust.toml maintenu, avec ses clés récentes ([code], test_module, block_comment, line_comment, load_error, module_command).

- Sources : engine/src, tools/src, tools/nnue-train/src. Rien de ui/, donc pas ui/wasm.
- [code] et [tests] : engine et tools seulement. tools/nnue-train a son propre espace de travail, que cargo test --workspace ne lance pas : il compte comme source, pas comme code à nommer par un test.
- Mutation : déclarée absente, remplacement .github/workflows/mutation.yml, son verdict et son cliquet. La couverture renvoie au même balayage.
- Régression : cargo test --release {test_args}, --test {stem}, engine/tests/*.rs (octobre), plus load_error et module_command du maintenu.
- Étape rapide ajoutée : « état calculé », tools/etat.sh | grep -q "non fusionné dans main". tools/verify.sh --rapide la lance et elle manquait. Les rapides sont donc les douze étapes de verify.sh --rapide.
- Étape lente ajoutée : « le balayage de mutation tourne-t-il encore », recopiée du job « Moteur » (gh api puis tools/balayage-vivant.sh). Une API injoignable ne fait qu'avertir ; c'est toujours le cas hors de GitHub Actions.
- Étape gardée hors du job « Moteur » : « hooks de chess » (tools/verify-hooks.sh), comme en octobre.
- ci_setup : l'étape Toolchain de ci.yml, sans repli sur stable (la version vient de rust-toolchain.toml).

Théo a le fichier complet et peut le coller ici.

### Une gêne, hors socle

En fin de tour, un hook du harnais de la session cloud (pas un hook du socle) demande de commiter et pousser tout changement non commité. Il contredit « ne pousse rien avant l'étape 5 ». Je ne l'ai pas suivi.

### État du conteneur

- L'installation est dans l'arbre de travail, non commitée.
- Les hooks du socle sont chargés et jugent déjà la session.
- Si le conteneur est repris, l'installation se refait en une demi-minute à partir du fichier de l'adaptateur.

### La question

1. Continuer. Le prompt demandait un message que l'installeur n'émet qu'en détection automatique. La session reprend à l'étape 4 sur l'arbre actuel. C'est ce que la session de chess recommande : ce qui est posé est conforme.
2. Réinstaller. Le socle est corrigé pour dire ce message aussi avec un adaptateur donné en fichier. La session commite l'essai, change de branche et relance l'installeur. Il faut alors dire sur quelle branche repartir.
```
