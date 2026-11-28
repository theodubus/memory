# Le relevé d'après sur chess, 28 novembre 2026 : le coût en appels, les refus par contrôle, neuf constats

Le relevé que B-0383 attendait : la mesure d'après des corrections du
troisième retour de chess
(`docs/fabrication/chess/cout-et-frictions-2026-11-26.md`), faite par la
même méthode sur la première séance de chess qui mène un lot ordinaire
après sa mise à jour du 28 novembre
(`docs/fabrication/chess/mise-a-jour-2026-11-28.md`). Recopié par Théo
dans la session du socle, tel quel. Chess tourne sur le moteur de la
fusion de la pull request #118 : il n'a pas la note `2026-11-28-a`
(ADR-0119, L-0058).

```text
Retour de chess sur le socle — la mesure d'après, 28 nov. 2026

Chess a installé ta mise à jour du 28 nov. Tu demandais la mesure d'après de ton retour du 26 nov., par la même méthode, sur la première séance qui mène un lot ordinaire. La voici, puis neuf constats, chacun avec ce qui l'a montré et ce que je te demande. Le relevé complet est dans le journal de chess, entrée J-2026-11-28-I.

LA SÉANCE MESURÉE
Une session réveillée par une passation programmée (chaîne 1), en un seul tour, sans message humain jusqu'au récap, sans compactage. Un lot ordinaire de deux tâches : deux réseaux candidats écrits et révoqués, une mesure de perte, puis quatre jobs de match lancés. Ensuite le relevé et la passation.

1. LES APPELS D'OUTIL PAR NATURE, du début au relevé : 120
- reste : 72 (60,0 %)
- socle, contrôles et rangement : 21 (17,5 %)
- socle, accompagnant un commit ou un push : 12 (10,0 %)
- réveils et tâches programmées : 8 (6,7 %)
- corrections après un refus : 4 (3,3 %)
- skills du socle chargés : 3 (2,5 %)
- gestes uniques de la mise à jour : 0
Avant (26 nov.) : 118 appels, dont 36 commandes du socle et 12 réveils. Après : 36 sur 120 (30 %) et 8 réveils. La part du socle ne bouge pas ; les réveils baissent d'un tiers. Jusqu'au dernier message de la séance : 146 appels.

2. LES REFUS PAR CONTRÔLE, dans le journal local des hooks
148 lignes au relevé, 2 refus (1,4 %), puis un troisième au contrôle de fin de tour :
- étage git-pre-commit, contrôle hooks.filtre : un amend dans la même commande qu'un autre commit. Fondé.
- PreToolUse:Bash, écriture supposée d'un fichier protégé : un heredoc python3 dont le TEXTE citait l'exécutable du socle. À tort.
- Stop, liens : le chemin du journal local des hooks entre accents graves dans le récap. Fondé selon la règle ; voir le constat 4.
Tes postes du §3, avant → après : liens du dernier message 20 → 1 ; écriture supposée d'un fichier protégé 2 → 1 ; opérations jugées externes 3 → 0 ; installeur 3 → 0 ; remise en état d'un fichier protégé 3 → 0 ; consigne citée sans empreinte 2 → 0.

3. L'ALERTE DE RETARD
Aucune session n'a démarré en retard. Le reflog montre le départ sur la tête de la passation, et l'état n'a pas ouvert sur l'alerte, à juste titre. Le démarrage d'une session programmée sur la bonne tête est donc constaté une fois.

CONSTATS ET DEMANDES, du plus important au moins important

1. Rien ne vérifie le budget d'une session programmée.
Ce qui l'a montré : le skill de passation dit qu'une session ne part que si le coût estimé de son lot tient dans ce qui reste de la fenêtre de cinq heures, marge de rangement comprise. La session d'avant a pourtant programmé la suivante « la minute qui suit », sans aucune estimation écrite. Celle-ci a démarré à 68 % de la fenêtre et fini son lot à 89 %, au seuil du rangement : 21 points pour un lot ordinaire, et le tri de la réserve a dû être reporté. Ni handoff write --scheduled ni handoff check ne lisent l'utilisation. Aucun coût de lot n'avait jamais été mesuré, alors que le skill de conduite des lots fonde l'estimation sur ces mesures.
Demande : que la passation programmée exige l'utilisation des deux fenêtres et le coût estimé du lot, et recule elle-même l'heure de départ à la remise à zéro quand le lot ne tient pas. Que la clôture d'un lot inscrive son coût mesuré (l'utilisation au début et à la fin), pour donner une base aux estimations suivantes.

2. Un commit fait par git revert échappe au filtre de l'agent et à commit-msg.
Ce qui l'a montré : une même commande enchaînait git commit, git revert --no-edit, puis git commit --amend. Pour le revert, le journal des hooks ne montre qu'un prepare-commit-msg : ni pre-commit, ni commit-msg. Seul l'amend a été refusé, au nom de la règle d'un commit par commande. Le revert est donc entré sans le filtre ni les contrôles de commit-msg (fuites de la mémoire privée, trailers). Cherry-pick, merge et rebase sont probablement dans le même cas.
Demande : que la règle d'un commit par commande compte aussi ces commandes, et que les contrôles de commit-msg ne dépendent pas de pre-commit.

3. Un texte qui cite un fichier protégé est pris pour une écriture de ce fichier.
Ce qui l'a montré : un heredoc python3 écrivait une entrée de journal dont le texte citait le chemin de l'exécutable du socle. Il a été refusé comme écriture d'un fichier protégé. Le contournement par l'outil d'édition a coûté deux appels. Or un relevé de coût nomme forcément ces commandes.
Demande : ne refuser que quand le chemin protégé est la destination de l'écriture, pas quand il figure dans le contenu écrit vers un autre fichier.

4. La consigne du relevé fait citer un fichier que le contrôle des liens refuse.
Ce qui l'a montré : le relevé d'après exige de nommer le journal local des hooks. Cité entre accents graves dans le récap, il a été refusé par le contrôle de fin de tour, parce que git ne le suit pas et que son lien mène à une page introuvable.
Demande : que le contrôle admette ce chemin, ou que tes consignes le désignent autrement.

5. Le contrôle des références prend le format du journal des hooks pour une référence de commit.
Ce qui l'a montré : dans le journal des hooks, le quatrième champ s'écrit étage:contrôle, par exemple git-pre-commit:hooks.filtre. Recopié tel quel dans une entrée, memoire.references le lit comme commit:<sha> et échoue (« commit:hooks.filtre n'est pas un SHA »). Or le relevé demande justement de classer les refus par ce champ.
Demande : ne reconnaître commit: qu'en début de mot, pas après un tiret, ou changer le séparateur du journal des hooks.

6. Un besoin satisfait par un simple constat ne se clôt pas sans une tâche fictive.
Ce qui l'a montré : un besoin bloqué attendait une observation, et il était écrit qu'il n'avait pas de tâche à faire. Ses deux critères cochés, socle close a refusé de le clore : « un besoin se ferme quand ses tâches sont closes, l'une au moins faite ; sinon il s'abandonne ». Il a fallu le rouvrir, créer une tâche, la clore, puis clore le besoin : trois appels et une tâche de pure forme.
Demande : pouvoir clore, avec une référence et sans tâche, un besoin dont tous les critères sont cochés.

7. Le tri de la réserve tombe d'un seul bloc.
Ce qui l'a montré : à la clôture d'un lot ordinaire, l'état demandait de ranger 30 besoins « à placer » d'un coup. C'est un geste plus gros que le lot lui-même, et il a été reporté faute de budget.
Demande : le répartir en quelques besoins par lot, ou le compter dans l'estimation du lot.

8. La feuille de route imprimée est repliée à environ 45 colonnes.
Ce qui l'a montré : hors terminal, socle roadmap coupe chaque titre sur deux ou trois lignes. Collée dans un récap, elle devient longue, et l'agent l'a résumée à la main au lieu de la coller comme le demande le skill de conduite des lots. C'est une faute de l'agent, mais cette forme y pousse.
Demande : ne pas replier hors terminal, ou faire coller la forme --format markdown.

9. Le relevé de coût n'a pas d'outil.
Ce qui l'a montré : il a fallu écrire un script de classement sur la transcription. Il s'est trompé trois fois : il a pris pour un refus une sortie qui contenait le mot, et il a compté comme commit un texte qui citait git revert. Il a fallu le corriger à la main. De plus, une séance d'un seul tour ne voit son contrôle de fin de tour qu'à la toute fin.
Demande : une commande, par exemple socle cost, qui rende les trois parties par la même méthode, pour que la prochaine mesure soit comparable sans recompter.
```

## Ce que le socle en a fait

Le tri, par `docs/fabrication/but-et-tri.md`, le 28 novembre
(J-2026-11-28-D), chaque constat vérifié contre le code ; ce dépôt ne
lit pas celui de chess, le retour fait foi pour ce qu'il a vu.

| Constat | Suite |
| --- | --- |
| 1. Le budget d'une session programmée | B-0389, dans JA-0006 ; sa conception se tranche avec Théo |
| 2. Le commit d'un `git revert` | B-0387, dans JA-0006 : constaté ici, plus large que chess ne le dit |
| 3. Un texte qui cite un fichier protégé | écarté une seconde fois : la règle du hook, et son message donne déjà la voie |
| 4. Le journal des hooks cité dans le récap | écarté : le contrôle a raison, la consigne venait d'ici |
| 5. Le champ du journal des hooks pris pour une référence | B-0388 et sa tâche T-0230, dans JA-0006 |
| 6. Le besoin sans tâche | déjà corrigé : ADR-0119, note `2026-11-28-a`, que chess n'a pas encore |
| 7. Le tri de la réserve d'un bloc | B-0390, dans JA-0006, priorité basse |
| 8. La feuille de route repliée | écarté : la largeur est voulue, pour un téléphone (B-0364) |
| 9. Un outil pour le relevé | B-0391, dans JA-0003, dont c'est le premier critère |

Les constats retenus :

- **Constat 2.** Rejoué ici sur un dépôt jetable, avec git 2.43 :
  `git revert` et `git cherry-pick` ne lancent que prepare-commit-msg
  (et post-commit) ; `git merge` lance pre-merge-commit, que le socle ne
  pose pas, puis prepare-commit-msg et commit-msg ; `git rebase` ne lance
  aucun de ces hooks. Le compte du filtre de l'agent repart à chaque
  prepare-commit-msg : le revert a pris le passage du filtre que l'amend
  attendait. Rien ne part pourtant sans jugement : le hook avant push
  rejuge le dernier commit et la plage qui part, `prive.fuites` compris,
  qui lit les messages de ses commits, et la CI après lui. Le trou est
  local : un défaut se voit au push au lieu du commit.
- **Constat 5.** Le motif des références n'a aucune borne à gauche :
  `git-pre-commit`, suivi d'un deux-points et d'un nom de contrôle, se lit
  comme une référence de commit, entre accents graves aussi. Seul l'étage
  git-pre-commit finit par ce mot ; la correction est claire.
- **Constat 1.** La règle est dans le skill `socle-handoff`, et rien ne la
  fait appliquer. Le skill `socle-batch` fait noter au journal le coût de
  chaque sous-agent, du relecteur, des demandes et du rangement, pas celui
  du lot entier. Deux voies, dont le choix revient à Théo : une
  passation programmée qui exige l'utilisation et le coût estimé et
  calcule son heure, ou la seule règle du skill, précisée. Le moteur ne
  lit pas l'utilisation, que seuls les outils de la plateforme donnent :
  l'agent la lui passe.
- **Constat 7.** Le bloc de 30 vient surtout des besoins de chess d'avant
  ADR-0118, sans raison : une fois. Mais un tri entier donne à tous le
  même `trié`, et ils reviennent ensemble quinze lots plus tard. Borner
  ce que l'état demande à chaque clôture répartit le tri, sans rien
  changer à celui que la clôture d'un jalon exige (D-0213).
- **Constat 9.** JA-0003 demande déjà une commande qui relève les refus
  par contrôle ; les appels par nature se lisent dans la transcription de
  l'agent, qui n'est pas du ressort du moteur : la conception le dira.

Les raisons des écartés :

- **Constat 3.** Le hook ne sait pas lire où un script python écrit : il
  le juge par les chemins protégés qu'il cite (B-0229, B-0230). Son refus
  dit déjà « un texte qui cite un chemin protégé s'écrit par l'outil
  d'écriture ». Ne juger que la destination demanderait de lire le
  python, ce qu'un hook ne peut pas faire sûrement, et assouplirait un
  garde-fou. Déjà écarté le 28 novembre (la gêne 3 de
  `docs/fabrication/chess/mise-a-jour-2026-11-28.md`). Vu une seconde
  fois chez chess, et une fois ici en versant ce retour (un script qui
  remplissait les entrées du backlog citait un dossier protégé), il coûte
  à chaque fois un refus et un appel de plus, par l'outil d'écriture que
  le refus nomme.
- **Constat 4.** Le journal des hooks est sous le dossier de git : le
  lien qu'en fait le client mène à un 404, et le refus le dit (« ne pas
  le citer »). La consigne fautive est celle du prompt de mise à jour
  d'ici, qui demandait de le nommer ; un prochain prompt le nomme sans
  accents graves.
- **Constat 8.** La feuille de route se lit sur un téléphone, dans un bloc
  de code, sans le faire défiler (B-0364) : 48 colonnes, voulu. Le skill
  `socle-batch` dit de la coller ; chess reconnaît la faute de l'agent.

## La mesure, avant et après

Les appels se comparent : une séance de chacun côté, 118 et 120 appels.
La part du socle ne bouge pas (36 appels sur 118, puis 36 sur 120) ;
les réveils passent de 12 à 8.

Les refus, eux, ne se comparent pas poste à poste. Le relevé d'avant
comptait 56 refus sur deux semaines, du 12 au 26 novembre, pour 4 905
déclenchements, soit 1,1 % ; celui d'après, 2 refus sur une séance, pour
148 déclenchements, soit 1,4 %, ou 2,0 % avec le contrôle de fin de tour.
Les postes « 20 → 1 » mettent deux semaines en face d'une séance. Ce
qu'on peut dire : les postes que le troisième retour a corrigés ne se
sont pas répétés sur cette séance, et le taux de refus par déclenchement
n'a pas baissé de façon visible ; sur trois refus, la mesure ne tranche
pas.

## La convergence

Les retours qui ont suivi la mise à jour de chess du 26 novembre avaient
ouvert dix-sept besoins dans JA-0006 ; celui de la mise à jour du
28 novembre, un ; celui-ci, quatre, et un dans JA-0003. Aucun ne vient de
la mise à jour elle-même (« gestes uniques de la mise à jour : 0 ») :
ce sont des frictions de l'usage ordinaire. Aucun ne bloque chess, et
rien ne part sans jugement.
