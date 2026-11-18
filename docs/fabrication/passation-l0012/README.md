# Passation du lot L-0012

Sept commits du 18 novembre, faits dans la session ouverte à 9 h 36 UTC,
qui suivent 47e4bba, la tête poussée de la branche : la fenêtre de cinq
heures a passé 60 % avant la troisième passe de la revue du lot, et le
skill du lot ne lance plus de sous-agent au-delà. La série entière passe
`verify --fast` (étapes rapides : 160,5 s). Rien n'en est poussé : la
correction de la passe 2 n'est pas relue, et elle récrit une décision
de la série, qu'un push figerait. Ce dossier se retire au commit qui
l'intègre.

1. T-0045, par un sous-agent : la durée de chaque étape et leur total,
   le seuil `[verify] fast_max_seconds` (300 s), sa clé au cliquet,
   l'avertissement en fin de passage, sur la ligne des étapes déjà
   passées et dans l'état, deux défauts injectés, le guide, la note de
   version 2026-11-18-a, le point 15 du prompt de chess ; une ADR
   nouvelle (un passage en échec ne garde pas sa durée) et un besoin
   voisin au backlog. T-0045 et B-0258 clos.
2. T-0044 et B-0257 clos : la troisième CI verte de suite, l'exécution
   652 sur 47e4bba.
3. Le recul de la passe 1 dans l'entrée du lot ; T-0068 close sur le
   relevé de `verify` complet (272 s, tout vert).
4. La passe 2 de la revue ouverte, depuis 8a7053c.
5. Ses deux bloquants : un passage complet lancé par la fin de tour ou
   l'envoi tait l'avertissement ; `nan` contourne le cliquet du seuil.
6. Leur correction, par un sous-agent, **pas relue** : l'envoi dit
   l'avertissement sur sa sortie d'erreur ; la fin de tour, qui ne bloque
   pas pour lui, le dit en message à l'humain ; le cliquet refuse une
   valeur `nan` sur toute clé ; deux défauts injectés ; le modèle de
   menace de B-0258, la conséquence de l'ADR, les commentaires de la clé,
   le guide, la note et le point 15 récrits ; un besoin voisin au
   backlog. Le journal passe à un septième fichier de novembre.
7. Le recul de la passe 2, décision « continuer », et l'entrée de
   journal de cette passation.

## La suite

1. Sur la branche de la session, partie de celle-ci :
   `git am -3 docs/fabrication/passation-l0012/*.patch`, puis un commit
   qui retire ce dossier et récrit le chantier actif.
2. La passe 3 de la revue, sur la correction seule (commits 6 et 7) :
   `python3 .socle/socle review --batch L-0012 --since <le commit 5 appliqué>` ;
   le relecteur éprouve chaque sortie des deux hooks jusqu'à ce que
   l'agent ou l'humain en reçoit, et chaque valeur non finie du cliquet.
3. Ses bloquants corrigés, le lot se clôt (son recul écrit, L-0012
   `fait`, `socle archive`), se pousse, et sa pull request se fusionne à
   la CI verte. Puis L-0014, de son propre dossier de passation.

## À l'intégration

- `git am` change les SHA de la série. Ces mentions les citent, à
  récrire avant le push, chacune par le SHA du commit appliqué : le
  commit 1 (d2d1b68 avant `git am`), dans l'entrée du journal qui clôt
  T-0044 et dans celle de la correction ; le commit 3 (abed8ed), dans la
  ligne `Commits` de la passe 2 de L-0012 et dans le recul de la passe
  2 ; le commit 5 (9cd15fd), dans l'entrée du journal de la correction ;
  le commit 6 (7e4dda1), dans le recul de la passe 2. 398e645, le commit
  du sous-agent de T-0045 avant son intégration, n'a jamais été sur la
  branche : sa mention reste.
- La série prend les lettres B à E du journal du 18 novembre et la note
  de version 2026-11-18-a ; celle de L-0014 prend des lettres du 17 et
  des notes 2026-11-17 : elles ne se recouvrent pas.
