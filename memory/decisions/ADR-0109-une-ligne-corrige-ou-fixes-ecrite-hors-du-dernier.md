<!-- socle: couche=decisions zone=publique -->
# ADR-0109 — Une ligne Corrige ou Fixes écrite hors du dernier paragraphe du message fait du commit un correctif, que tests.regression vérifie

> statut : acceptée · date : 2026-11-24 · source : B-0348@5fdbe77b, T-0178@9874cb7f, T-0059@2d1bec04, J-2026-11-24-AN@ff4c701d, ADR-0054@b9a67784 · lu : decisions@6edcf74f

## Contexte

Un correctif livre un test qui échoue sur le commit parent, que
`tests.regression` rejoue en CI ; le hook git `commit-msg` avertit dès le
commit d'un correctif qui n'apporte aucun test. Les deux reconnaissent un
correctif par `est_correctif` (`engine/socle/checks_tests.py`) : un sujet
qui suit `[regression] fix_subject`, ou un trailer `Corrige` ou `Fixes`.
Ce trailer ne se lisait que dans le dernier paragraphe du message, comme
git lit les trailers. Une ligne `Corrige: T-NNNN` écrite dans un
paragraphe à part, avant les lignes d'attribution, ne faisait pas du
commit un correctif : la vérification de son test était sautée sans rien
dire (B-0348@5fdbe77b, relevé par la revue de L-0024@2ffc722a,
J-2026-11-24-AN@ff4c701d).

Mesuré sur ce dépôt le 2026-11-24 : sur 1 058 commits, 27 portent une
telle ligne hors du dernier paragraphe, toutes avec une référence (`B-` ou
`T-`) pour valeur, aucune de la prose ; pour 10, dont le sujet n'est pas
`fix:` et sans `Corrige:` dans le bloc final, la vérification n'a pas
tourné.

B-0348 donnait deux pistes : lire aussi cette ligne comme un correctif,
ou avertir au hook `commit-msg` qu'elle ne compte pas. La première est
retenue (T-0178@9874cb7f) : elle fait ce que l'auteur voulait dire, au
lieu d'un avertissement qui laisserait le commit sans vérification si
l'agent l'ignore. T-0059@2d1bec04 a introduit `trailers_hors_bloc` pour
les dispenses égarées, que les refus nomment sans les faire valoir : une
dispense relâche un contrôle et ne doit valoir qu'à sa place ; un
`Corrige:` le durcit, et vaut partout.

## Décision

1. `est_correctif` tient un commit pour un correctif quand une ligne
   `Corrige:` ou `Fixes:` est écrite hors du dernier paragraphe de son
   message, sous les noms que le moteur reconnaît déjà dans les deux
   langues (`language.TRAILERS`), lue par `trailers_hors_bloc` : un
   paragraphe à part, ou les lignes d'un message d'un seul paragraphe
   après son sujet. Le sujet n'est jamais lu comme une telle ligne ;
   `fix_subject` le juge comme avant.
2. Le bloc final se lit sous les mêmes noms, par `language.trailers` :
   les deux lectures reconnaissent les mêmes formes. Pour le bloc final,
   rien ne change (`Corrige` et `Fixes`, sans égard à la casse).
3. `tests.regression` juge un tel commit comme tout correctif ; le hook
   git `commit-msg`, qui passe par `est_correctif`, l'avertit de même dès
   le commit.
4. Le défaut injecté (`correctif-egare-sans-test`) et son témoin sain
   sont dans `engine/socle/selftest.py`.

## Modèle de menace

Ce que l'agent pourrait faire pour échapper au contrôle : déclarer un
correctif, par `Corrige: T-NNNN`, sans livrer de test qui échoue sur le
parent, en écrivant la ligne là où git ne la lit pas, par mégarde (un
paragraphe à part, avant les lignes d'attribution, comme dans les 27
commits mesurés) ou exprès.

Fermé : une ligne en forme de trailer `Corrige:` ou `Fixes:`, en
début de ligne, n'importe où après le sujet du message. Le commit est un
correctif, et `tests.regression` exige son test, au commit (en
avertissement) comme en CI (en refus).

Laissé ouvert, et pourquoi c'est accepté :

- **Un correctif qui ne se déclare pas** : ni `fix:` en sujet, ni
  `Corrige:` ou `Fixes:`. Le contrôle ne juge que les correctifs
  déclarés ; reconnaître un correctif à son code, sans déclaration, est
  hors de portée d'un contrôle sans langage. La règle des instructions
  (« un correctif livre un test qui échoue sur le commit parent ») et la
  revue d'un lot restent les barrières.
- **Une forme que le moteur ne reconnaît pas** : `Corrige T-NNNN` sans
  deux-points, `Fix:` au singulier, une ligne indentée ou dans une
  citation. Les lire ferait un correctif de toute prose qui dit
  « corrige » ; seules les formes d'un trailer comptent, comme dans le
  bloc final.
- **Un commit de fusion** : `tests.regression` ne juge que les commits à
  un seul parent, comme avant.

Le changement n'ouvre rien : il ne fait que juger davantage de commits.
Son coût est un faux positif, une ligne de prose qui commence par
`Corrige:` ou `Fixes:` et fait d'un commit qui ne corrige rien un
correctif à prouver ; la mesure n'en trouve aucun, et l'issue est de
reformuler la ligne.

## Conséquences

Un correctif dont le `Corrige:` est mal placé est vérifié au lieu d'être
sauté. Les commits déjà sur la branche par défaut ne sont pas rejugés :
`tests.regression` ne juge que la plage d'une pull request ou d'un envoi.
Un projet installé n'a rien à faire. La défaire : retirer la lecture de
`trailers_hors_bloc` dans `est_correctif`, ses tests dans
`tests/test_regression.py` et `tests/test_hooks.py`, et les deux cas de
`engine/socle/selftest.py`.
