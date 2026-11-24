# Le tri du backlog ouvert, 24 novembre 2026

Le tri que demande T-0173 : chaque besoin et chaque tâche ouverts, relus
un à un contre `docs/fabrication/but-et-tri.md`, que Théo a validé le 24
novembre (D-0167), et contre D-0165 (« passer 10h sur un cas limite qui
arrive rarement, et qu'en pratique n'est qu'une légère gêne pour l'agent
qu'il peut gérer lui même c'est non »). Une entrée reste si elle passe
les trois tests du document (à quoi elle sert, sa preuve, son coût), et
sort dès qu'une exclusion s'applique (X1 à X6). En cas de doute, elle
sort : une entrée fermée revient si elle est vue en usage réel.

Rien n'est encore fermé : ce document est le récap que Théo a demandé
avant tout abandon (D-0167), soumis par la demande qui le cite.

## Le compte

| | Ouverts | Restent | Se ferment |
| --- | --- | --- | --- |
| Besoins | 59 | 20 | 39, dont B-0274, satisfait |
| Tâches | 68 | 19 | 49, avec leur besoin |
| Besoins ouverts du jalon JA-0005 | 39 | 13 | 26 |
| Lots ouverts | 14 | 4 | 10, vidés |

Ce qui reste du jalon en cours tient en quatre lots : celui-ci (L-0035),
la session longue (L-0010), le récap et l'état (L-0024), l'adaptateur
kotlin (L-0032).

## Ce qui reste

Chaque entrée, avec le point du but qu'elle sert et sa preuve.

### Dans le jalon en cours, JA-0005

- **B-0341** (T-0171) — l'auto-test du socle échoue au hasard dans la CI
  de chess. Marche pour de vrai ; vu dans la CI de chess le 23 novembre.
- **B-0342** (T-0172) — le tri des constats de revue met au backlog des
  cas limites rares. Décision humaine ; demandé par Théo (D-0165).
- **B-0343** (T-0173) — ce tri. Demandé par Théo (D-0166, D-0167).
- **B-0156** (T-0039, T-0079) — une session longue sans en ouvrir une
  neuve à la main. Contexte ; demandé par Théo le 10 novembre.
- **B-0259** (T-0041, T-0080, T-0081) — la session neuve qui s'ouvre
  seule à la levée de la limite. Contexte, décision humaine ; demandé
  par Théo, la sonde E2 en cours.
- **B-0303** (T-0134) — une tâche qui contredit un test le nomme dès sa
  création, et sa demande se pose avant le lot. Contexte ; vu deux fois
  (deux lots arrêtés en leur milieu), retenu par Théo (D-0141).
- **B-0335** (T-0162) — une tâche ouverte par une revue qu'aucun lot ne
  prend en forme un. Contexte ; vu par la revue de cap 3, retenu par
  Théo (D-0158) ; c'est ce qui laisse un jalon sans fin visible.
- **B-0311** (T-0125, T-0126) — le récap redonne à Théo une branche à
  supprimer que GitHub n'a plus. Décision humaine ; sa plainte du 20
  novembre, la quatrième.
- **B-0292** (T-0101) — l'état dit une branche gardée par une branche de
  travail que l'origine n'a plus : la supprimer perdrait ses commits.
  Vérification ; effet irréversible ; une correction de quelques lignes.
- **B-0334** (T-0161) — après la fusion, la ligne CI de l'état dit
  l'exécution d'un commit d'avant : l'attente de la CI ne finit jamais.
  Contexte ; vu en session le 23 novembre.
- **B-0317** (T-0119) — l'état ne dit pas si GitHub refuse le push
  forcé sur la branche par défaut, et le guide ne le fait pas régler.
  Vérification ; effet irréversible, seul rempart d'une session dont les
  hooks ne sont pas chargés.
- **B-0275** (T-0059) — une dispense écrite avant les lignes de
  signature est ignorée, et le refus redemande ce que l'agent a écrit.
  Contexte ; vu le 17 novembre, et Claude Code signe chaque commit.
- **B-0147** (T-0151, T-0152) — sur un projet Compose Multiplatform ou
  Android, les tests du projet sont sautés sans erreur. Marche pour de
  vrai ; vu sur le prototype du pilote le 10 novembre.

### Après le jalon en cours

- **B-0323** — la mise à jour de chess d'un coup (JA-0006). Demandé par
  Théo (D-0151).
- **B-0161** — une couche des consignes de l'humain, remise au
  démarrage. Mémoire ; le chantier actif est plein, validé par Théo
  (D-0093, proposition 3).
- **B-0101** — la planification à la manière du socle. Ce qui vient
  ensuite ; demandé par Théo (D-0051, D-0090).
- **B-0158** — l'architecture en un paragraphe par module, sous un
  budget. Contexte ; 41,7 Ko mesurés, validé par Théo (D-0093,
  proposition 4).
- **B-0310** (T-0163) — la revue de cap dans le produit. Décision
  humaine ; retenue par Théo après ses trois essais (D-0145).
- **B-0188** — peser des issues GitHub comme boîte de réception des
  retours des projets. Décision humaine ; demandé par Théo, non
  prioritaire ; ce matin encore, il a recopié à la main la demande de
  chess.
- **B-0104** — le pilote neuf, en pause. L'usage réel ; en cours.

## Ce qui se ferme

Chaque besoin se ferme avec ses tâches, et l'exclusion qui s'applique.

### X1 — ne compte que si l'agent cherche à contourner le socle

- **B-0282** (T-0142) — écrire 0 comme borne du démarrage la relève en
  silence.
- **B-0283** (T-0143) — un seuil absent des garde-fous s'écrit plus haut
  sans demande.
- **B-0313** (T-0117) — le titre d'une décision, écrit par l'agent,
  autorise un test que le texte de l'humain ne nomme pas.
- **B-0318** (T-0149, T-0150) — en session locale, rien que le hook ne
  borne un `rm -rf` d'un dossier parent : seule une forme de commande
  que le hook ne lit pas y échappe ; la mesure demandait l'ordinateur de
  Théo.

### X2 — imaginé par un relecteur, jamais vu, rattrapé ou bénin

- **B-0012** — une copie non marquée d'une valeur de la doc n'est qu'un
  avertissement ; l'avertissement le dit déjà.
- **B-0271** (T-0153, T-0154) — des commentaires du moteur citent des
  identifiants de ce dépôt ; l'agent d'un projet ne lit pas ces
  commentaires.
- **B-0326** (T-0155) — deux messages imprimés chez un projet citent un
  identifiant de ce dépôt ; jamais vu gêner l'agent de chess.
- **B-0284** (T-0146, T-0147) — une fin de tour plus longue que le délai
  de son hook serait coupée sans le dire ; déduit des réglages, jamais
  vu, et `verify --fast` comme le hook avant envoi le disent encore.
- **B-0287** (T-0092) — un bloc de code ouvert par `~~~` qui contient
  ```` ``` ```` fausse la lecture des liens ; jamais vu.
- **B-0314** (T-0118) — `socle next-id` ne saute pas les identifiants
  des autres branches ; `socle new`, que les instructions font employer,
  calcule juste, et le contrôle des collisions rattrape le reste.
- **B-0315** (T-0128) — `socle renumber` après un cherry-pick, sur une
  ligne retouchée depuis le push.
- **B-0316** (T-0139, T-0140) — le dossier de revue d'un lot dont une
  part a été fusionnée avant sa revue.
- **B-0329** (T-0156, T-0157) — deux formulations de l'installeur à la
  mise à jour.
- **B-0337** (T-0166, T-0168) — deux points du skill de la reprise : sans
  `list_events`, un réveil pourrait se lire comme un message de
  l'humain ; le lien vers la liste des tâches programmées, que Théo n'y
  a pas vue. Au pire, l'humain écrit « reprends » ou « arrête ».
- **B-0338** (T-0167) — une fausse alerte de l'installeur, hooks git
  dits débranchés, à la mise à jour dans un conteneur redémarré.
- **B-0339** (T-0169) — trois cas de l'attente à heure bornée du skill
  de la reprise.

### X3 — peaufine la machinerie sans gêne constatée

- **B-0109** — un paquet PyPI ; le clone du dépôt public suffit.
- **B-0174** — un adaptateur lancé dans un sous-dossier ; depuis
  ADR-0066, l'installeur dit au projet ses deux issues, sans gêne vue.
- **B-0172** (T-0027, T-0077, le lot L-0022) — remplacer le balayage de
  mutation de chess par celui du socle ; celui de chess marche.
- **B-0285** (T-0144, T-0145) — la règle du prochain jalon et des lots
  sans ordre ; l'état et la suite nomment aujourd'hui le même jalon.
- **B-0295** (T-0130, T-0131) — la règle de consommation de
  `socle-batch` récrite sans ambiguïté.
- **B-0296** (T-0148) — la longueur des lignes de l'essentiel des
  échecs.
- **B-0298** (T-0138) — l'étape 2 du skill de revue ; son étape 3 dit
  déjà d'écrire le dossier dans un fichier.
- **B-0333** (T-0160) — un message de `socle consumption`.

### X4 — ne concerne que ce dépôt

- **B-0218** (T-0136, T-0141, T-0165) — les copies protégées de ce
  dépôt en retard sur leurs gabarits : l'état le signale déjà (T-0009) ;
  le skill `delegate-lot` dit de les remettre à la clôture du lot qui
  change le gabarit.
- **B-0281** (T-0066, T-0067) — le lanceur parallèle des tests de ce
  dépôt.
- **B-0294** (T-0137) — le dossier de revue court en mode amont, qui
  n'existe qu'ici.
- **B-0319** (T-0135) — la section du socle de l'`AGENTS.md` de ce dépôt
  et son budget.

### X6 — de la mesure dont aucune décision ne dépend

- **B-0332** (T-0159) — trois mutations de bord de la mesure de la
  consommation.
- **B-0340** (T-0170) — le compte des messages tapés pendant une limite.

### D-0165 — une légère gêne que l'agent règle lui-même

- **B-0272** (T-0129) — l'entrée qu'ouvre un sous-agent cite un index
  que le hook avant envoi refuse ; l'agent la fait relire, d'un commit.
- **B-0300** (T-0132, T-0133) — après la fusion, en session cloud, la
  branche repartie se pousse et recrée la branche distante ; l'agent ne
  la déplace pas, la session qui fusionne n'en menant plus d'autre.
- **B-0312** (T-0116) — un avertissement à tort au push d'une réponse,
  vu sur le projet d'essai ; le push part.

### Attendus d'un fait qui n'arrive pas : ils reviennent s'il arrive

- **B-0048** (T-0008, T-0071) — une action externe que Théo a validée
  reste refusée par le hook. Aucun refus nouveau depuis le 22 octobre ;
  « revient s'il est vu » remplace l'attente de D-0026 et de D-0153.
- **B-0179** — la CI posée qui échouait sur le pilote sans fichier
  Gradle : corrigée et publiée le 12 novembre ; son dernier critère
  attend une reprise du pilote que rien ne date. Si sa CI échoue encore,
  il revient.
- **B-0192** (T-0032) — la classe d'un test dans la clé d'un constat
  toléré : aucun projet n'en a eu besoin, ce que son critère prévoit
  pour se clore.

### Faits ou remplacés

- **B-0274** (T-0089, T-0090, T-0100) — la vue de la suite : faite par
  T-0057, T-0058, T-0085, T-0088 et T-0091 (le terminal, la
  conversation, la page de la CI) ; ses trois tâches restantes, nées
  d'une revue, peaufinent la sortie (X3).
- **B-0055** — un agent maître qui confie chaque tâche à un sous-agent :
  fait pour l'essentiel par le skill `socle-batch` (un orchestrateur, un
  sous-agent par tâche dans sa copie, son modèle, un relecteur sans
  contexte, les contrôles sur le travail rendu) ; reste une règle de
  choix du modèle mesurée au banc (X6), que Théo tranche aujourd'hui
  (Opus partout, D-0095).
- **B-0162** — reformuler la proposition 7 de D-0093 (séparer le noyau
  de la méthode) à partir de ce à quoi sert le socle : D-0167 le dit
  désormais ; séparer le noyau sans projet qui le demande serait X3.

## Ce qui en découle

- Les lots vidés se ferment : L-0022, L-0025 à L-0031, L-0033, L-0034.
- L-0010 reçoit T-0134 et T-0162, qui changent le même gabarit que lui
  (`socle-batch`), et perd T-0165.
- L-0024 reçoit T-0119 et T-0059, et perd T-0092 : le récap, l'état et
  les refus.
- JA-0005 ne garde que ses treize besoins ouverts ; JA-0006 que B-0323 ;
  JA-0004 perd B-0162.
- Chaque entrée fermée cite la décision qui consigne la réponse de Théo
  et sa raison ci-dessus.
