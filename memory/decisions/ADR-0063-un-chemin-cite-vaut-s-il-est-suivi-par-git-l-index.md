<!-- socle: couche=decisions zone=publique -->
# ADR-0063 — Un chemin cité vaut s'il est suivi par git, l'index compris

> statut : acceptée · date : 2026-11-11 · source : B-0166@23990de1, J-2026-11-11-F@0a9633c8 · lu : decisions@138e3c40

## Contexte

Une entrée de journal citait, entre accents graves, le dossier des
worktrees de l'agent : présent dans le conteneur, ignoré par une règle de
`.git/info/exclude`, absent de tout clone. La fin de tour, le hook avant
commit et le hook avant push l'ont accepté ; la CI, sur un clone neuf, l'a
dit inexistant (J-2026-11-11-F@0a9633c8). Deux trous : sur l'arbre de
travail, le contrôle des références prenait pour existant tout fichier du
disque, suivi ou non ; et partout, un chemin ignoré par git valait, que la
règle soit dans un `.gitignore` suivi ou seulement locale. Le contrôle des
liens donnés à l'humain, en fin de tour, jugeait aussi contre le disque.

## Décision

1. Un chemin cité, lié ou référencé (`fichier:`) vaut s'il est suivi par
   git, l'index compris : un fichier ajouté (`git add`) dans le commit qui
   le cite passe. Le hook avant commit juge déjà l'arbre de l'index, et la
   CI le commit.
2. Un chemin ignoré ne vaut que par une règle d'un `.gitignore` de la
   version jugée : l'index sur l'arbre de travail et au commit, le commit
   en CI. Une règle locale (`.git/info/exclude`, `core.excludesFile`), ou
   écrite dans un `.gitignore` sans `git add`, manque à un clone neuf et ne
   compte pas : présent sur le disque, le chemin est refusé par un message
   qui le dit ignoré par git, jusqu'à ce que la règle soit dans l'index. Un
   dossier non suivi cité sans barre finale est refusé, avec un message qui
   la demande : sans elle, git ne le reconnaît pour un dossier que s'il est
   sur le disque, et le jugement changerait dans le clone neuf. Un chemin
   d'un dépôt git imbriqué non suivi (un worktree d'agent, un clone) est
   refusé par un message qui le dit : `git add` n'en ferait qu'un lien de
   sous-module.
3. Le cas pesé : un fichier neuf, pas encore ajouté à l'index, qu'aucune
   règle n'ignore, cité par la mémoire. Sur l'arbre de travail (fin de
   tour, `verify`), il est **averti**, pas refusé : le message dit de
   l'ajouter. Le refuser bloquerait l'installeur, dont la vérification
   finale tourne avant le premier commit, et un tour qui écrit puis cite
   un fichier avant de le commiter ; et rien ne s'échappe : le commit, qui
   juge l'index, le refuse s'il ne l'ajoute pas, et la CI juge le commit.
   Le même avertissement vaut pour `fichier:` et `cmd:`. Un dossier
   ignoré, lui, ne sera jamais commité : refusé dès l'arbre de
   travail. Dans un dépôt sans commit, celui qu'on vient d'équiper, tout
   fichier non ignoré vaut : le premier commit juge son index.
4. Les liens d'un message de fin de tour suivent la même règle : un chemin
   présent sur le disque et suivi, ou livré par le prochain `git add`,
   passe ; un chemin que git ignore, un chemin d'un dépôt imbriqué, et un
   fichier suivi mais supprimé du disque sont refusés.
5. Inchangé : un chemin cité par une couche gelée vaut s'il a existé dans
   l'historique (ADR-0027@d32b4ef9) ; un chemin protégé cité par une
   demande n'a pas à exister ; sur une branche jetable, un fichier qu'elle
   ajoute est averti (ADR-0055@e49f4839) ; hors d'un dépôt git, le disque
   fait foi.

## Conséquences

L'écart entre le conteneur et la CI se ferme pour les chemins cités : ce
qui passe la fin de tour en erreur passe le clone neuf. Un défaut injecté
(`chemin-cite-hors-depot`) et un témoin (un fichier neuf cité, ajouté par
le même commit) l'éprouvent. Se défait en rendant à `_citables` et
`_ignore` leur lecture du disque.
