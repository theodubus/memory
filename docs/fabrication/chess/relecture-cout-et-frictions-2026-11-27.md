# Relecture critique du troisième retour de chess, 27 novembre 2026

Le retour relu : `docs/fabrication/chess/cout-et-frictions-2026-11-26.md`
(B-0367). Sa relecture se fait gêne par gêne, sans critère fixe (D-0217) :
ce que la gêne coûte à chess, ce que le code du moteur en confirme, ce que
sa correction coûterait, et les trois tests de
`docs/fabrication/but-et-tri.md` (à quoi elle sert, sa preuve, son coût en
proportion). Chaque gêne reçoit une recommandation : un besoin de JA-0006,
la réserve avec sa raison, ou écartée d'une raison. Théo arbitre dans la
demande qui suit cette relecture. B-0365 et B-0370 s'y jugent aussi
(D-0232, D-0234).

## La mesure et les principes

Le retour mesure le coût du socle en appels d'outil, et non en octets
injectés : dans une conversation longue, chaque appel relit tout le
contexte (582 000 jetons en médiane le 26 novembre). Sur 118 appels d'une
séance, 36 lancent une commande du socle et 12 servent aux réveils de
reprise ; la part de cérémonie atteint 40 % au plus, sans borne basse.
C'est une séance, un lot de deux tâches : un ordre de grandeur, pas une
mesure stable.

- **Le compte des appels par nature** (§1.1) et **les 56 refus classés**
  (§3) vont à JA-0003, comme son contenu et comme la mesure avant et après
  ces corrections (D-0233). Ils ne s'arbitrent pas ici.
- **Le critère de réussite proposé** (a à d) ne devient pas un critère
  fixe (D-0217) ; la mesure de JA-0003 le remplace.
- **P3** (le coût fixe d'une tâche à la mesure de la tâche) recoupe le
  test « Contexte » du tri : il sert de grille, sans décision propre.
  **P4** (refuser à tort un fichier protégé est acceptable si la voie
  légitime est bon marché et qu'un contrôle en aval rattrape) est déjà la
  règle du hook (ADR-0072) ; il sert ici à juger §3.2 et §3.4.

## Les gênes

### §2 — La cérémonie d'une petite tâche

- **Chez chess** : environ huit gestes de mémoire pour deux lignes de
  travail ; un commit refusé de plus le 26 au soir, pour une entrée close
  non rangée.
- **Dans le code** : confirmé. `memoire.backlog`
  (`engine/socle/checks_memory.py`) refuse une entrée close sans `ref`, et
  une entrée close restée parmi les ouvertes ; aucune commande ne clôt une
  tâche (`socle --help`).
- **2.1 et 2.2** : une commande `socle close T-NNNN` pose le statut, la
  référence et le rangement, sans cocher ; la référence peut désigner le
  commit qui clôt, que le contrôle retrouve par l'historique du fichier.
  Environ 150 lignes, tests compris ; la forme de la référence est à
  spécifier. Tri : « Contexte » (cinq appels de moins par tâche), vu en
  usage réel, coût proportionné, chaque tâche le paie.
  **Recommandation : un besoin de JA-0006.**
- **2.3** (le hook avant commit range lui-même) : la commande de 2.2 le
  couvre, et ferait écrire l'index par un hook qui ne fait que juger.
  **Écartée.**
- **2.4** (un seuil sous lequel une tâche n'a pas de lot à elle) : chess
  la donne « à examiner ». **Réserve** : la mesure de JA-0003 dira si un
  lot d'une seule tâche pèse.

### §3.1 — Les liens du dernier message, 20 refus

- **Chez chess** : le premier poste des refus ; chaque refus coûte un tour
  de plus et un second message, et l'humain s'en est plaint (« Pourquoi tu
  répètes 2 fois le récap de fin ? »).
- **Dans le code** : confirmé, et la cause du récap répété est plus
  précise que le retour ne le dit. `links.problemes` répond « aucun chemin
  de ce nom dans le dépôt » sans chercher le fichier suivi que désigne un
  nom nu. Puis la fin de tour (`engine/socle/hooks.py`) juge le récap sur
  le seul dernier message : le message qui corrige les liens doit redonner
  tout le récap, faute de quoi il est jugé sans récap.
- **Correction** : le refus donne le chemin complet quand le nom nu
  désigne un seul fichier suivi, et « sans accents graves » sinon ; un
  message qui ne fait que corriger les liens d'un récap refusé pour eux
  seuls n'a pas à le redire ; la section installée dit la règle en une
  phrase positive. Environ 80 lignes, tests et témoin compris ; le hook de
  l'agent ne s'ouvre que sur une preuve (ADR-0098), et celle-ci en est
  une. Tri : « Décision humaine » (un message de moins à lire, une plainte
  de l'humain), vu en usage réel, le premier poste.
  **Recommandation : un besoin de JA-0006, le premier par son poids.** La
  vérification d'un brouillon (troisième proposition) ne s'envisage que si
  la mesure de JA-0003 montre que cela ne suffit pas.

### §3.2, §3.5 et §3.8 — Trois refus qui savent leur correction

- **§3.2** (2 refus) : un heredoc de python qui cite `.socle/socle` dans
  un texte est refusé, sans rien écrire. Confirmé : `_cites`
  (`engine/socle/hooks.py`) juge tout chemin protégé cité par un écrivain
  que le hook ne lit pas. Ne refuser que l'écriture demanderait d'analyser
  le script, pour un cas rare, une voie légitime bon marché et un contrôle
  en aval (P4). **Le hook reste tel quel** ; son message dit en plus qu'un
  texte qui cite un chemin protégé s'écrit par l'outil d'écriture.
- **§3.5** (une faute, trois refus) : le premier refus donne déjà les
  formes de remise en état ; il ne dit pas que `rm` vaut pour un fichier
  que git ne suit pas, ce que dit le second. **Une ligne au message.**
- **§3.8** (2 refus) : une consigne citée sans son empreinte, dans le
  commit qui la crée. Confirmé : le message de `memoire.lectures` renvoie
  à `socle show` sans donner l'empreinte, que le contrôle connaît.
  Correction : le refus donne l'empreinte, et une consigne née dans la
  même plage passe sans elle.
- Ensemble, environ 40 lignes. Tri : « Contexte » (le refus dit la
  correction), vu en usage réel, coût d'une ligne par refus.
  **Recommandation : un besoin de JA-0006.**

### §3.3, §3.4 et §3.7 — Les autres refus

- **§3.3** (2 refus) : un push sur `main` d'un dépôt jetable, dans un
  dossier temporaire, est refusé. Confirmé : `_git_irreversible` juge la
  branche sans regarder le dépôt visé. Juger la cible (le dossier, `-C`,
  l'adresse du distant) est faisable, dans le hook de l'agent. **Réserve** :
  deux refus en deux semaines, et une voie existe, une autre branche que
  `main` dans le dépôt jetable ; il revient s'il est revu.
- **§3.4** (3 refus) : deux sont acceptables selon P4 ; le troisième n'a
  pas sa commande entière. **Écartée** ; il revient s'il est revu avec sa
  commande.
- **§3.7** (3 refus non classés de `hooks.filtre`) : sans donnée.
  **Écartée.**
- **§3.6** et **§9** : les refus que chess demande de garder restent tels
  quels.

### §4 — Un titre de commit pris pour un correctif

- **Chez chess** : un commit de documentation titré « Correction : … » a
  dû être déplacé sur une autre branche.
- **Dans le code** : confirmé. `FIX_DEFAUT`
  (`engine/socle/checks_tests.py`) lit `correction` comme un correctif ;
  depuis B-0359, un correctif qui ne touche que la mémoire n'est plus jugé,
  mais un correctif qui ne touche que la documentation reste refusé, hors
  de tout adaptateur.
- **Correction** : un correctif qui ne touche que la documentation, la
  mémoire et le dossier du socle n'est pas jugé, comme la mémoire seule.
  Le préfixe français reste lu : l'agent écrit ses titres en français
  (ADR-0027). Environ 15 lignes, test et témoin compris. Tri :
  « Vérification » (un refus à tort), vu en usage réel.
  **Recommandation : un besoin de JA-0006.**

### §5 — Les réveils de reprise

- **Chez chess** : 12 appels sur 118, environ 10 % du coût de la séance,
  pour un filet qui n'a pas servi. Mesuré ici aussi : le premier tour de
  cette session en a lancé cinq avant tout travail, et deux de plus le
  retireront à la fin.
- **Dans le code** : confirmé par le skill `socle-resume` : armer au début
  de chaque tour qui agit, retirer à la fin.
- **Correction** : les réveils restent d'un tour à l'autre et ne se
  déplacent que quand leur heure change. Un réveil sans objet coûte une
  vérification de deux ou trois appels et une ligne à l'humain, que la
  vérification au réveil rend sans danger. Quand `list_events` manque,
  l'heure se lit dans `get_session`, qui ne donne que la fenêtre nommée
  (vu dans cette session aussi). Texte du skill et tests qui le lisent,
  environ 40 lignes. Tri : « Contexte » (environ 10 % des appels), vu en
  usage réel. **Recommandation : un besoin de JA-0006.**
- **N'armer que pour un tour long** : la proposition précédente en prend
  l'essentiel, et « long » ne se juge pas d'avance. **Écartée.**

### §6 — La passe de revue écrite avant le retour du relecteur

- **Chez chess** : en session cloud, le hook de fin de tour de
  l'environnement exige de pousser la passe que `socle review` vient
  d'écrire ; le lot part avant sa revue, et la note « lot déjà poussé »
  s'applique à tort.
- **Dans le code** : confirmé. `ecrire_passe` (`engine/socle/review.py`)
  écrit la passe à la production du dossier.
- **Correction** : écrire la passe au retour, par une commande qui
  consigne en même temps ses bloquants. Environ 100 lignes. Tri :
  « Vérification », vu en usage réel ; mais rien ne fusionne avant la
  revue, et rien ne se perd : la gêne est une note fausse et un push
  précoce. **Réserve** : elle revient si elle fausse une fusion ou une
  revue.

### §7 — Une session neuve démarre sur une tête en retard sur sa passation

- **Chez chess** : le 26 au soir, une session programmée a démarré sur un
  commit vieux de trois heures ; ses instructions, ses skills et ses hooks
  venaient de lui. Il a fallu une session sonde.
- **Vu ici aussi, le 27 novembre** : cette session est partie de `main`
  (57fed449) quand la passation portait b7082609 ; l'état injecté donnait
  un chantier actif périmé, sans dire l'écart, que seule la garde a montré.
  Entre les deux, rien que la mémoire.
- **7.1 et 7.2** : quand une passation attend et que la tête locale est un
  ancêtre strict de sa référence, l'état le dit en tête, avec les fichiers
  d'instructions, de skills et de hooks qui changent entre les deux ; le
  skill de passation fait lire ce diff avant tout travail. Environ 60
  lignes, test compris, sans rien écrire. Tri : « Contexte », vu deux fois
  en usage réel. **Recommandation : un besoin de JA-0006.**
- **7.3** (avancer la branche dans le hook de démarrage) : son effet n'est
  pas vérifié (Claude Code lit-il les instructions après ce hook ?), et il
  ferait écrire un hook qui ne fait que lire. **Réserve** : 7.1 dira si
  l'écart persiste.
- **7.4** (le signaler à la plateforme) : hors du socle. **Écartée** du
  backlog ; Théo peut le signaler s'il le souhaite.

### §8 — Où ranger la parole de l'humain

- **Chez chess** : deux paroles rangées en consignes le 26 novembre, une
  décision de projet et une attente ; une consigne s'injecte à chaque
  démarrage et ne se lève que par la parole de l'humain, quand une attente
  rangée en besoin bloqué se lève en fermant l'entrée.
- **Dans le code** : confirmé ; la section installée ne connaît que la
  consigne.
- **Correction** : la section installée et le skill `socle-request`
  distinguent trois natures : une règle de travail de l'agent va dans les
  consignes, une décision de projet en décision, une attente en besoin
  bloqué. Texte, note de version, environ 20 lignes. Tri : « Mémoire »
  (une parole mal rangée se fausse), vu en usage réel.
  **Recommandation : un besoin de JA-0006.**

## B-0365 et B-0370

- **B-0365** (la réserve que rien ne trie, D-0213) : sa règle ajoute un
  geste à la naissance d'un besoin hors jalon (sa raison), un tri à la
  clôture d'un jalon, et un signal après quinze lots que l'état calcule.
  Face au coût mesuré, elle ne pèse que si la raison coûte un appel ou un
  refus de plus. **Recommandation : la garder dans JA-0006, après les
  corrections ci-dessus**, à cette condition : la raison se donne à
  `socle new need`, le contrôle ne fait que rattraper un oubli, et le
  signal se calcule.
- **B-0370** (une demande qui ne nomme ni la clé ni le test fait répondre
  l'humain deux fois) : vu une fois dans l'atelier (D-0220, puis D-0221),
  pour une réponse de plus. Le contrat des demandes le dit déjà. Rare et
  bénin, il ne vaut qu'une ligne (`docs/fabrication/but-et-tri.md`,
  test 3) : celle du contrat que `socle new request` imprime à l'écriture
  de la demande, au moment où elle sert. **Recommandation : B-0370 se
  satisfait par cette ligne, ses critères récrits ainsi ; le signal avant
  le push s'écarte.**

## Ce que la recommandation donne à JA-0006

Sept besoins nouveaux, dans cet ordre, par lots qui touchent les mêmes
fichiers :

1. les refus et l'état (`engine/socle/hooks.py`, `engine/socle/links.py`,
   les contrôles, l'état) : §7.1, §3.1, les trois refus de §3.2, §3.5 et
   §3.8, §4 ;
2. la clôture d'une tâche en un geste : §2.1 et §2.2 ;
3. les textes du produit : §5, §8 et la ligne de B-0370 ;
4. puis B-0365 et B-0368, avant le prompt de mise à jour de chess.

En réserve, chacun avec sa raison : §2.4, §3.3, §6, §7.3. Écartées :
§2.3, le changement du hook de §3.2, §3.4, §3.7, le réveil réservé aux
tours longs, §7.4.
