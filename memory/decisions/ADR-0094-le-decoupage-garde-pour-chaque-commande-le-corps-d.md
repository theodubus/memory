<!-- socle: couche=decisions zone=publique -->
# ADR-0094 — Le découpage garde pour chaque commande le corps du heredoc que reçoit son entrée, et le script que python y lit se juge comme celui d'un python -c

> statut : acceptée · date : 2026-11-19 · source : B-0229@a79f304e, T-0001@814f6839, ADR-0082@beb85978, ADR-0072@1a8b5c2d · lu : decisions@6f7d194f

## Contexte

Le découpage (`engine/socle/commands.py`) retire le corps des heredocs
avant de couper le texte en mots (`sans_heredocs`) : un document, pas une
commande. Le hook ne savait donc pas ce que reçoit l'entrée d'une
commande, et le script que python lit sur la sienne (`python3 - <<'EOF'`),
une forme qu'un agent écrit pour une transformation de plusieurs lignes,
écrivait un fichier protégé ou supprimait le projet sans être jugé
(B-0229@a79f304e). ADR-0082@beb85978 la fait garder.

## Décision

- **Un champ de la commande.** `Commande.entree` porte le corps du heredoc
  que reçoit son entrée, tel qu'écrit, sans rien développer, ses
  tabulations de tête retirées pour `<<-` comme le shell les retire ;
  `None` sans heredoc. La dernière redirection de l'entrée l'emporte : un
  `<` ou un `<<<` qui suit le heredoc la vide. Le découpage garde les
  corps dans l'ordre du texte avec le mot qui les ferme, et le mot qui
  suit un `<<` prend le premier corps de son nom qui reste ; un heredoc
  vu dans une substitution ou une chaîne consomme le sien, pour que le
  `$(cat <<'EOF' … EOF)` d'un message de commit ne donne pas son corps au
  heredoc suivant de même nom.
- **Le jugement.** `_script_python` (`engine/socle/hooks.py`) rend ce
  corps, pour un `python` lancé sans `-c`, `-m` ni script, ou avec `-`
  pour script, comme il rend le script d'un `python -c` : il se juge par
  les chemins protégés qu'il cite en toutes lettres (`_cites`) et par ce
  qu'il supprime (`_supprimes_par_python`). Un heredoc donné à un autre
  programme ne change pas de jugement ; un script lu d'un fichier, par
  son chemin ou par `<`, reste hors de portée.
- **Un long corps.** Un mot cité sans barre oblique ni point de tête ne
  compte que s'il nomme un fichier protégé entier : `_cites` ne parcourt
  plus pour lui les fichiers suivis, ce qui garde un long heredoc sous le
  délai du hook, sans changer ce qu'il refuse.

## Conséquences

- Le heredoc d'une substitution (`$(python3 - <<'EOF' … EOF)`) ne donne
  pas son corps à la commande qu'elle lance : le découpage relit le texte
  de la substitution sans ses corps, comme avant. Avec le heredoc donné à
  un autre interpréteur (`bash <<'EOF'`), une forme qu'un agent n'écrit
  pas dans son travail, il entre dans la liste des formes connues que le
  hook ne juge pas (note de version 2026-11-19-p).
- Pour défaire : retirer `Commande.entree` et la branche de
  `_script_python` qui le lit ; le corps redevient du texte.
