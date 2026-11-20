<!-- socle: couche=decisions zone=publique -->
# ADR-0097 — Trois substitutions qui rendent la branche courante se développent en elle dans un git push, quand la commande ne change ni de dossier, ni de dépôt, ni de branche avant lui

> statut : acceptée · date : 2026-11-19 · source : B-0254@cbffb1b9, T-0106@4860ab74, T-0006@90239e33, D-0140@3c12ff2c, ADR-0082@beb85978, ADR-0072@1a8b5c2d · lu : decisions@883b3c27

## Contexte

T-0006@90239e33 fait refuser un `git push` dont un argument ne se
développe pas, une substitution comprise, comme ADR-0072@1a8b5c2d refuse
un chemin inconnu : sans la branche, le hook ne sait pas si le push vise
la branche par défaut, ce que rien ne rattrape ensuite. Mais `git push -u
origin "$(git branch --show-current)"`, qu'un agent écrit couramment pour
pousser sa branche de travail, en était refusé (B-0254@cbffb1b9). Le hook
lit déjà la branche courante pour un push qui ne nomme pas sa
destination. Théo a validé D-0140@3c12ff2c : ces formes passent depuis
une branche de travail, et la substitution ne se résout pas quand la même
commande change de branche ou de dépôt avant le push.

## Décision

- **Trois substitutions, et elles seules.** `$(git branch
  --show-current)`, `$(git rev-parse --abbrev-ref HEAD)` et `$(git
  symbolic-ref --short HEAD)`, entre `$(…)` ou entre accents graves, les
  blancs libres entre leurs mots (`BRANCHE_COURANTE`,
  `engine/socle/hooks.py`), dans un argument du push ou dans la valeur
  d'une variable qu'il lit (`B=$(…); git push origin "$B"`), sont
  remplacées par la branche courante avant que l'argv se développe ;
  le push se juge alors comme si elle était écrite en toutes lettres
  (`_avec_la_branche`). Toute autre substitution reste illisible.
- **Où se lit la branche.** Dans le dossier où part la commande (le
  dossier courant de l'agent, à défaut la racine), là où la substitution
  s'exécute, par `git rev-parse --abbrev-ref HEAD`. Un HEAD détaché, ou un
  nom qui porte un caractère que le shell lirait (hors de lettres,
  chiffres, `.`, `/`, `+`, `@`, `-`, `_`), ne se résout pas.
- **Quand elle ne se lit pas sûrement** (`branche_substituee`). Le push
  ou une commande qui le précède dans le même texte part d'un autre
  dossier que celui de départ (un `cd`, un `pushd` ailleurs ; un `cd` vers
  le même dossier, écrit en toutes lettres, ne change rien) ; le push
  vise un autre dépôt (`-C` vers un autre dossier, `--git-dir`,
  `--work-tree`, une variable `GIT_DIR`, `GIT_WORK_TREE`,
  `GIT_COMMON_DIR`) ; une commande qui le précède peut changer de
  branche (`git checkout`, `git switch`, `git rebase`, `git bisect`, `git
  branch -m`, `git symbolic-ref` qui écrit, une sous-commande de git
  illisible, `gh pr checkout` : `_change_de_branche`). La substitution
  reste alors illisible, et le push refusé.

## Modèle de menace

Celui du hook, ADR-0082@beb85978 : les erreurs d'un agent coopératif ;
pour ce que rien ne rattrape, un push vers la branche par défaut, il
refuse aussi ce qu'il ne sait pas lire. La branche que rend la
substitution se lit sûrement quand rien, dans la commande, ne change le
dossier, le dépôt ou la branche avant elle : le hook la lit au même
endroit que le shell, juste avant. Ce qu'un programme autre que git, un
script, change de la branche avant le push ne se voit pas : une forme
qu'un agent n'écrit pas dans son travail, inscrite à la liste des formes
connues du guide (2026-11-19-t). Une commande qui suit le push dans le
texte, ou qui tourne en même temps que lui (un pipeline, une tâche de
fond), ne compte pas.

## Conséquences

- `git push -u origin "$(git branch --show-current)"` passe depuis une
  branche de travail, et se refuse depuis la branche par défaut comme un
  push vers elle ; `git add -A && git commit … && git push -u origin
  "$(git branch --show-current)"` passe.
- `git checkout main && git push origin "$(git branch --show-current)"`,
  et la même après `cd` ailleurs ou `git -C` vers un autre dossier,
  restent refusés comme un argument illisible ; le message du refus dit
  quand la substitution vaut la branche courante.
- Un appel à git de plus par push qui porte l'une de ces substitutions.
- Pour défaire : retirer `branche_substituee` de `refus_bash` ; toute
  substitution redevient illisible, comme avant T-0106.
