<!-- socle: couche=decisions zone=publique -->
# ADR-0065 — L'agent remet un fichier protégé à son état du dernier commit

> statut : acceptée · date : 2026-11-11 · validation : D-0098@8911447c · source : B-0165@900ed86f, J-2026-11-09-B@2ffde9bb · lu : decisions@1e5dd78e

## Contexte

Le hook de l'agent refusait toute écriture du shell dans un fichier
protégé, la remise d'un fichier à son état du dernier commit comprise,
qu'il réservait à l'humain. En session cloud, l'humain n'a pas la main sur
le conteneur : un fichier protégé changé par erreur, l'installeur lancé
sur le projet par exemple, bloquait la session (le 9 novembre). Théo a
validé, par D-0098, que l'agent remette lui-même un tel fichier dans l'état
du dernier commit.

## Décision

Le hook de l'agent (`remise_en_etat`) laisse passer, chaque chemin écrit en
toutes lettres et désignant un fichier, jamais un dossier :

- `git restore --source=HEAD -- <fichiers>`, avec au plus `--staged` et
  `--worktree`, et `git checkout HEAD -- <fichiers>`, pour un fichier
  présent dans le dernier commit ;
- `rm <fichiers>` (au plus `-f`, `-v`) pour un fichier apparu sous un
  chemin protégé que git ne suit pas, ni dans l'index ni dans `HEAD`.

Sauf les réglages de Claude Code (`.claude/settings.json` et son jumeau
local), que l'humain garde pour lui (sa réponse, mot pour mot :
« Exclure ») : toute écriture, remise comprise, reste sous leur refus
dédié.

Restent refusés : un autre commit que `HEAD`, avec ou sans `--`
(`git checkout HEAD~1 <fichier>`), l'index comme source (`git restore
<fichier>`, `git checkout -- <fichier>`), un dossier ou tout l'arbre, un
motif, une variable ou une substitution du shell, des chemins lus dans un
fichier (`--pathspec-from-file`), une option globale de git (`-C`), une
affectation de variable ou un préfixe devant la commande (`GIT_DIR=…`,
`env`), un `export` dans la même commande, et un fichier suivi supprimé
par `rm`. La remise ne dispense que des fichiers qu'elle remet : ses
redirections et ses autres chemins se jugent comme toute écriture.

Est épargné, et le refus le dit, un fichier que cite, lui ou un dossier
qui le contient, une demande dont ce qu'elle approuve n'est pas commité :
en attente, ou validée quand sa réponse n'est pas dans `HEAD` ou que
l'empreinte qu'elle cite est celle du fichier présent. Le refus d'écriture
protégée et l'erreur de `protege.fichiers` donnent la forme qui passe.

## Conséquences

Le risque accepté : effacer une modification que l'humain aurait faite
lui-même dans l'arbre de travail, sans la commiter ni la soumettre par une
demande. En session cloud, il n'en fait pas ; sur un poste, la remise se
voit dans la conversation. La politique reste celle de l'humain : rien
d'autre que l'état commité ne s'écrit par l'agent. Pour défaire : retirer
l'appel à `remise_en_etat` dans le hook ; les tests de `tests/test_garde.py`
et l'auto-test diront ce qui change.
