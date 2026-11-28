# Mise à jour du socle sur chess, 28 novembre 2026 : faite, et ce qu'elle a montré

Le retour de la session de chess, recopié par Théo dans la session du
socle, tel quel. La session a suivi le prompt de
`docs/fabrication/chess/prompt-mise-a-jour.md` dans sa version de L-0057,
avec la version 0.2.0 publiée le 28 novembre : le moteur de la fusion de
la pull request #118, que celle de la #119 n'a pas changé.

```text
Retour de chess sur la mise à jour du 28 nov. 2026

Chess a installé le socle 0.2.0 publié le 28 nov., depuis sa copie du 26 nov., sur ton prompt de mise à jour (pull request chess 326, fusionnable, ses deux CI vertes). Ce qui suit dit ce que chaque correctif a donné en usage réel, puis ce qui a gêné, chaque refus mot pour mot. Dis-moi ce que tu en retiens, et ouvre ce qui le mérite.

## Ce qui a tenu

- CODEOWNERS (2026-11-26-d) : sans --owner, l'installeur a écrit « CODEOWNERS : @theodubus sur la politique, les hooks et la CI ». Aucune ligne « !! aucun propriétaire ».
- Les notes (2026-11-26-g) : quatre en entier (2026-11-27-k, 2026-11-27-b, 2026-11-27-a, 2026-11-26-k), les dix-sept autres par leur titre. Lisible.
- La demande seule (2026-11-26-h) : celle des 39 fichiers protégés s'est commitée par git add sur son fichier, git commit et git push, sans stash ni --only, sans refus. Aucune ligne n'a compté de constats laissés à la CI ; il n'y en avait sans doute pas.
- Les liens (2026-11-27-c) : le récap de la mise à jour est passé au premier contrôle de fin de tour.
- L'empreinte d'index (2026-11-26-i) : socle new a écrit lu : backlog@… sur un besoin et deux tâches de la même séance ; aucun refus de memoire.lectures sur elles.
- Le besoin pour l'humain (2026-11-26-j) : B-0077 a quitté « besoins à découper en tâches ».
- Le plafond des skills (2026-11-27-a, 2026-11-27-j) : la demande nommait la clé, validée, 10 000 posés dans la même pull request.
- Les réveils (2026-11-27-h) : armés au premier tour, ni retirés à sa fin ni retouchés au tour suivant ; zéro appel d'outil de réveil au second tour.
- La feuille de route (2026-11-27-b) : aucun --by dans chess.
- La réserve (2026-11-27-k) : socle new need « … » --reserve « … » --task « … » a posé réserve et trié seul ; l'état annonce 32 besoins « à placer », à ranger à la clôture du prochain lot.
- L'alerte de retard (2026-11-27-f), vérifiée dans un clone jetable où la branche distante porte la passation et rien ne la retire. Sur la tête où la session avait vraiment démarré, l'état ouvre sur : « !! LA TÊTE LOCALE (4e5a5cafef) EST EN RETARD SUR origin/claude/agents-md, qui porte la passation en attente : la mémoire lue ici est celle d'avant ; aucun fichier d'instructions, de skills ni de hooks ne change entre les deux. La reprise se place sur la référence que la garde nomme (socle handoff check, après git fetch). » Sur une tête plus ancienne, il nomme AGENTS.md, CLAUDE.md et sept skills, avec la commande git diff.
- L'état : 6 359 octets avant, 7 024 après l'installeur, 7 455 avec deux demandes en attente, 6 588 après leurs réponses ; jamais coupé.
- Pas exercés : le correctif de la mémoire non jugé (2026-11-26-e, 2026-11-27-e), la commande citée dans « Pour toi » (2026-11-26-f), la consigne née dans la plage (2026-11-27-d). Aucune règle ne m'a manqué dans les skills ni dans AGENTS.md (2026-11-26-l).

## Ce qui a gêné

1. Clore un besoin qui n'a jamais eu de tâche (2026-11-27-g). B-0084 était une attente rangée en besoin bloqué, débloquée par Théo, puis faite directement, ses deux critères cochés. socle close B-0084 a refusé, mot pour mot :
   « refus : B-0084 ne se clôt pas, rien n'est changé ; les contrôles du backlog le refuseraient clos :
     - B-0084 est fait sans tâche faite : un besoin se ferme quand ses tâches sont closes, l'une au moins faite ; sinon il s'abandonne »
   Clore a coûté quatre gestes au lieu d'un : socle new task --need B-0084, l'écrire après coup, cases cochées, socle close sur elle, puis socle close B-0084. Le même cas attend B-0083, dont un critère ne se constate qu'en usage, et que l'état liste parmi les besoins à découper en tâches alors qu'aucune tâche n'y servirait. Piste : qu'un besoin dont chaque case est cochée et qui n'a jamais eu de tâche se clôture par socle close, sa référence suffisant ; ou que socle close crée lui-même la tâche faite.

2. docs.copie contre ton prompt. Le prompt demandait que le besoin et la tâche du relevé d'après recopient la même section. Le hook avant commit a refusé, mot pour mot :
   « memory/backlog/B-0085-le-releve-d-apres-le-cout-du-socle-mesure-sur-la-p.md:15 — paragraphe identique aussi présent en memory/backlog/T-0006-relever-le-cout-du-socle-sur-la-premiere-seance-qu.md:14 : garder une source, renvoyer vers elle »
   Le texte entier est resté dans la tâche, et le besoin y renvoie. Le contrôle a raison sur le fond. Piste : un prompt qui demande de recopier un texte dans deux entrées dit dans laquelle, l'autre y renvoyant.

3. Lancer le moteur neuf sur un autre arbre. Pour vérifier l'alerte de retard, il fallait l'état neuf sur une copie en retard. Un python3 -c qui importait le moteur, en lecture seule, a été refusé par le hook de l'agent : « écriture d'un fichier protégé (.socle/engine/ (dont .socle/engine/socle/CHANGES.en.md), cité par python3 -c, un écrivain que le hook ne sait pas lire : il peut l'écrire ; … ». Contourné par un script écrit à part. Après coup, python3 .socle/socle --root <dossier> state marche, le dernier --root l'emportant, mais ni HELP.md, ni les skills, ni AGENTS.md ne le disent. Piste : le documenter.

4. L'alerte de retard ne se constate plus une fois la passation reprise. La session de la mise à jour avait elle-même démarré en retard : sur main, alors que la passation était un commit plus loin sur une autre branche. Son état de démarrage venait encore du moteur d'avant, ce qui est normal. Mais dès que son premier commit, qui retire la passation, était poussé, le vrai dépôt ne pouvait plus montrer l'alerte : il a fallu fabriquer un clone et réécrire à la main ses références distantes. Le premier critère de B-0083 (une session programmée qui démarre sur la tête de sa passation, constaté au reflog) reste à observer sur une vraie passation programmée. Piste : un auto-test du socle qui joue ce scénario.

5. Le hook avant push : 134 s pour la demande seule (un fichier de la mémoire), 17 s au push suivant (étapes déjà passées sur cet arbre), 161 s pour les réponses aux deux demandes et la clé des garde-fous (mémoire et .socle/guardrails.toml, aucun code). Les tests du moteur de chess ne disent rien d'un changement de la mémoire. Piste : que le pre-push saute les capacités de l'adaptateur quand la plage poussée ne touche que la mémoire, la documentation ou les garde-fous, comme tests.regression le fait désormais.

6. Les consignes à ranger (2026-11-27-i) : « tes consignes du 26 novembre » ne désignait qu'une consigne écrite ce jour-là ; les trois autres y avaient été migrées. J'ai classé les quatre : deux règles restent ; la fusion par l'agent à CI verte est une décision que la demande d'origine porte déjà ; le format court de la feuille de route n'a plus d'objet. Les deux dernières sont proposées à Théo pour levée.

## Les refus du hook pendant la mise à jour

Journal local des hooks, de 1 h 33 à 2 h 12, heure de Paris : 132 déclenchements, 5 refus (3,8 %).

- PreToolUse:Write, contrat des demandes : la demande citait le SHA du dépôt du socle d'où la version est publiée, sans description. Fondé ; le SHA était celui d'un autre dépôt.
- PreToolUse:Bash, fichier protégé : python3 -c qui importait le moteur, en lecture. À tort.
- git-pre-commit:memoire.references,memoire.lectures : une tâche citée avant d'être dans le commit, une consigne sans empreinte. Fondé.
- git-pre-commit:docs.copie : la section recopiée dans le besoin et la tâche, comme le prompt le demandait. Fondé sur le fond, contre le prompt.
- PreToolUse:Edit, référence inventée : une entrée de journal citée avant d'être créée. Fondé.

Hors hooks : socle close sur le besoin sans tâche (gêne 1), et socle prune-branches, dont la suppression de la branche de la passation a été refusée par l'origine en 403 : attendu, le jeton de session ne supprime pas de branche.

## La porte

python3 .socle/socle verify --fast --redo : passe, 132 s. python3 .socle/socle ci : 366 s, en échec sur protege.fichiers seul avant la réponse aux fichiers protégés. tools/verify.sh --rapide : passe, 120 s. Après la réponse, les deux CI de la pull request sont vertes.
```

## Ce que le socle en a fait

Le tri, par `docs/fabrication/but-et-tri.md`, le 28 novembre
(J-2026-11-28-A). Les identifiants B-0083, B-0084 et B-0085 de la gêne 1
et de la gêne 2 sont ceux du backlog de chess.

| Gêne | Suite |
| --- | --- |
| 1. Clore un besoin qui n'a jamais eu de tâche | B-0386 ; la conception se tranche avec Théo |
| 2. `docs.copie` contre le prompt | le prompt avait tort : `delegate-lot` le dit pour le prochain |
| 3. Le moteur neuf sur un autre arbre | écartée : refus voulu, option dans l'aide |
| 4. L'alerte de retard, plus constatable après la reprise | écartée : un test la joue déjà |
| 5. Le hook avant push, sur une plage sans code | écartée : la mémoire seule ne relance déjà rien |
| 6. Les consignes à ranger | côté chess : Théo y répond dans sa session |

Les raisons des écartées :

- **Gêne 3.** Le hook refuse un script en ligne qui cite un chemin
  protégé, faute de pouvoir lire ce qu'il écrit : c'est sa règle, que la
  note `2026-11-27-d` disait déjà. L'option `--root` est dans
  `socle --help` (« racine du projet »). Le besoin n'est né que de la
  vérification que le prompt demandait, sur un clone fabriqué : un cas
  rare et bénin, que `but-et-tri` borne à une ligne de documentation, et
  l'aide l'a.
- **Gêne 4.** Le scénario de la tête en retard est joué par
  `tests/test_passation.py`, à chaque CI. Le constater pour de vrai est le
  critère de B-0083 dans chess : une attente, qui se range en besoin
  `bloqué` (note `2026-11-27-i`) et quitte alors « besoins à découper » ;
  sa clôture tient à B-0386. Le prompt n'aurait pas dû demander de
  vérifier sur un clone ce que les tests jouent déjà.
- **Gêne 5.** Les étapes rapides de l'adaptateur ne se relancent déjà pas
  quand seule la mémoire change (B-0086) : leur marque est l'empreinte
  du contenu hors de `memory/`. Les deux pushes longs viennent de la mise
  à jour elle-même : le premier part avec le moteur neuf encore non
  commité dans l'arbre, que les étapes lisent ; le troisième change
  `.socle/guardrails.toml`. Les deux tiennent à une mise à jour, une fois
  par mise à jour. La documentation, elle, peut être lue par les tests
  d'un projet (ceux de ce dépôt lisent les skills). La gêne revient si
  le relevé d'après (B-0383) montre un push long sur une séance
  ordinaire.

Les refus : quatre fondés sur cinq ; le cinquième est la gêne 3. La
suppression refusée en 403 est attendue d'une session cloud.

La convergence. Les retours de chess qui ont suivi sa mise à jour du
26 novembre avaient ouvert dix-sept besoins dans JA-0006 (B-0357 à
B-0365, B-0367, B-0371 à B-0377) ; celui-ci en ouvre un, B-0386, qui
naît d'une règle que la version 0.2.0 a ajoutée (l'attente rangée en
besoin bloqué) et d'une autre qu'elle avait déjà (le besoin pour
l'humain fermé sur sa parole). Des dix-neuf points du prompt, treize ont
tenu, trois n'ont pas été exercés (les points 4, 5 et 10), un n'est pas
rapporté (le point 9, le plafond des consignes) ; deux ont gêné : la
clôture en un geste (point 11, gêne 1) et le rangement des consignes,
par le mot du prompt (point 15, gêne 6).
