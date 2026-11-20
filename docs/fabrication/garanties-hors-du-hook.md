# Ce qui rattrape, hors du hook de l'agent, un push forcé et une suppression

Relevé du 20 novembre 2026 (T-0023, besoin B-0262). Le hook de l'agent
lit chaque commande du shell avant qu'elle agisse ; il est borné aux formes
qu'un agent écrit (D-0120) et terminé (ADR-0098). Une forme qu'il lit de
travers laisse donc passer trois effets que rien, dans le socle, ne
rattrape ensuite : un push forcé sur la branche par défaut, la suppression
du projet avec son `.git`, et celle d'un dossier qui le contient. Ce relevé
dit, pour chacun, quelle couche qui ne lit pas le shell le rattrape, dans
ce dépôt et dans un projet équipé, chess, et ce qui reste sans garantie.

Ce dépôt est mesuré depuis une session cloud de Claude Code. Chess ne se
lit pas d'ici (la session n'a accès qu'à ce dépôt) : ce qu'on en sait vient
des comptes rendus de son installation et de sa mise à jour, dans
`docs/fabrication/chess/`, et du fait que ses sessions sont, elles aussi,
des sessions cloud.

## En bref

| Effet | Ce dépôt | Chess | Ce qui manque |
| --- | --- | --- | --- |
| Push forcé sur `main` | l'ensemble de règles de GitHub, en partie : la CI exigée est mesurée, le refus du push forcé et de la suppression ne l'est pas | de même : la CI exigée, le reste inconnu | B-0317 (T-0119) |
| Suppression du projet | le hook de fin de tour de l'environnement cloud, en partie : il refuse de conclure un tour non poussé, sauf un tour qu'un hook de fin de tour a déjà relancé, ou une branche jamais poussée | de même (supposé : la même sorte d'environnement) | B-0321 ; B-0318, hors de l'environnement cloud |
| Suppression d'un dossier qui le contient | le conteneur jetable, qui ne contient que le clone ; aucun bac à sable de l'outil shell | de même (supposé) | B-0318, hors de l'environnement cloud |

## Le push forcé sur la branche par défaut

**Ce qui le rattraperait.** Seul GitHub, côté serveur : un ensemble de
règles sur la branche par défaut qui refuse le push forcé (la règle
`non_fast_forward`, « Block force pushes ») et sa suppression (`deletion`,
« Restrict deletions »). Les hooks git du socle ne refusent pas un push
forcé : le hook avant push juge la plage qui part, pas sa forme. La CI du
socle tourne après le push, sur `main` : elle dirait la faute, sans rien
remettre.

**Mesuré dans ce dépôt.** `main` est protégée (l'outil GitHub de la
session la liste `protected: true`), et son ensemble de règles exige la
CI du socle avant toute fusion (la ligne « branche » de `socle state` ;
F-0009). Une CI exigée par un ensemble de règles refuse aussi qu'on pousse
sur `main` un commit dont la CI n'a pas réussi, pour qui n'est pas dans sa
liste de contournement (documentation de GitHub, non éprouvé ici) : un
push forcé d'un commit neuf serait refusé ; un push forcé d'un commit déjà
vert, plus ancien de `main` ou tête d'une autre branche (celle de l'agent,
dont la CI a tourné), ne le serait pas par cette seule règle.

**Non mesuré.** Si l'ensemble de règles a `non_fast_forward` et
`deletion`. `socle state` lit cet ensemble de règles, mais n'y cherche que
la CI et la revue des propriétaires du code ; la session n'a pas d'autre
accès à cette page de l'API. L'environnement cloud dit à l'agent de ne
pousser que sur sa branche : c'est une consigne de ses instructions ; s'il
l'applique aussi côté serveur n'a pas été éprouvé, puisqu'il faudrait
tenter le push qu'elle interdit.

**Chess.** La CI du socle y est exigée avant fusion depuis son
installation (`docs/fabrication/chess/installation-2026-11-12.md`) ; le
reste de son ensemble de règles n'est pas connu.

**Ce qui manque.** L'état devrait dire, comme il dit la CI exigée, si la
branche par défaut refuse le push forcé et la suppression, et le guide
devrait les faire refuser à l'installation : B-0317, et sa tâche T-0119.
Une fois faite, la mesure vient d'elle-même, ici et dans chess, à la
première session.

## La suppression du projet

**Mesuré dans ce dépôt.** L'environnement cloud pose son propre hook de
fin de tour (`~/.claude/stop-hook-git-check.sh`, déclaré dans
`~/.claude/launcher-settings.json`, deux fichiers que ses permissions
interdisent à l'agent de modifier). Il refuse de conclure un tour tant
qu'un changement n'est pas commité, qu'un fichier non suivi reste, ou
qu'un commit de la branche n'est pas poussé. Supprimé en cours de tour,
le projet ne perd alors que le travail de ce tour, et ce que git ne
pousse pas : `.git/socle/` (la trace des hooks, et depuis T-0018 le
dernier commit poussé de chaque branche), les remises (`git stash`), les
branches locales et les copies isolées des sous-agents. Le hook de
l'environnement ne s'en plaint pas : sans dépôt sous lui, il laisse
conclure.

Deux trous, lus dans le script. Il laisse conclure, sans rien vérifier,
tout arrêt d'un tour qu'un hook de fin de tour a déjà relancé (le champ
`stop_hook_active` de son entrée) : le hook de fin de tour du socle en
relance souvent un, quand le récap n'a pas ses deux lignes ou que
`verify --fast` échoue, et un commit fait pendant cette relance peut
finir le tour sans être poussé. Et il compare la branche à
`origin/<branche>`, ou à défaut à `origin/HEAD` : une branche que
l'origine n'a jamais reçue, dans un clone sans `origin/HEAD` (celui de
cette session n'en a pas), n'a aucun commit non poussé à ses yeux.
B-0321 : le hook de fin de tour du socle le dirait, en session cloud.

**Chess.** Ses sessions sont des sessions cloud : la même couche y vaut
(supposé, sur la même sorte d'environnement).

**Hors de l'environnement cloud.** Dans une session locale de Claude
Code, ce hook n'existe pas (il vient des réglages du lanceur cloud) ; rien
ne fait pousser le travail à la fin de chaque réponse, et le hook de fin
de tour du socle ne vérifie que les contrôles. Non mesuré d'ici : B-0318.

## La suppression d'un dossier qui contient le projet

**Mesuré dans ce dépôt.** L'outil shell de l'agent n'a pas de bac à
sable : ni `.claude/settings.json` du projet ni des réglages de
l'utilisateur ou de l'organisation n'en déclarent, et un fichier écrit
dans `/home/user`, au-dessus du projet, l'est, l'agent étant `root`. Ce qui
borne l'effet est le conteneur de la session : jetable, il ne contient
que le clone (`/home/user` n'a que `memory`). Supprimer un dossier qui
contient le projet n'y perd donc rien de plus que supprimer le projet, la
couche précédente le rattrapant de même.

**Chess.** De même (supposé).

**Hors de l'environnement cloud.** Sur le poste de l'humain, un dossier
au-dessus du projet contient ses autres fichiers, et rien d'autre que le
hook de l'agent ne borne leur suppression : ni le socle, qui ne propose
pas le bac à sable de l'outil shell de Claude Code, ni un conteneur.
B-0318 l'étudie : proposer ce bac à sable, ou accepter le risque et le
dire.

## Ce qui reste sans garantie

- Le push forcé d'un commit déjà vert sur `main`, tant que l'ensemble de
  règles n'a pas `non_fast_forward` : non mesuré, B-0317.
- En session cloud, le travail d'un tour relancé par un hook de fin de
  tour, ou d'une branche que l'origine n'a jamais reçue : B-0321.
- Hors de l'environnement cloud, le travail non poussé et les fichiers
  hors du projet : B-0318.
- Partout, ce que git ne pousse pas (`.git/socle/`, les remises, les
  copies isolées) : un risque accepté, ces fichiers étant locaux par
  nature.
