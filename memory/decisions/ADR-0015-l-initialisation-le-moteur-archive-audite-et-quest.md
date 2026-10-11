<!-- socle: couche=decisions zone=publique -->
# ADR-0015 — L'initialisation : le moteur archive, audite et questionne ; l'agent comprend

> statut : acceptée · date : 2026-10-10 · source : J-2026-10-10-AC@a4b5de64 · lu : decisions@1b666313

## Contexte

Le jalon 8 (B-0003@d5bb73ab) demande une initialisation depuis trois
entrées cumulables, un document de cadrage, rien, un dépôt existant, sans
rien inventer, avec des questions plafonnées qui ont chacune un défaut, et
une mise à jour qui migre les formats et montre le diff de politique. Théo a
voulu qu'il se fasse sur des copies, pas sur le vrai chess
(D-0005@ea3b7c8d). Le moteur ne comprend pas un texte : extraire les
objectifs d'un document ou le confronter au dépôt est un travail d'agent.

## Décision

- **Le moteur fait ce qui se fait sans juger** (`socle init`) : archiver le
  document tel quel, son empreinte au journal ; auditer le dépôt en lecture
  seule et n'en tirer que des faits « mesurés » dont un fichier est la
  preuve (langage, fonctions de test, CI, README) ; poser les questions de
  départ.
- **Les questions de départ sont une demande au contrat**, chacune avec son
  défaut et ce qu'il change, plafonnées par `init_questions_max` ; l'humain
  répond `defauts` d'un mot, ou donne ses réponses, consignées avec son
  texte exact. Sans réponse, les défauts s'appliquent en « supposé ».
- **L'agent fait le reste**, avec des règles que `socle init` imprime : un
  fait tiré du document est « supposé », le document pour source ; le dépôt
  fait foi pour ce qui existe, le document pour ce qui est voulu ; toute
  divergence devient une question.
- **L'installeur déduit l'adaptateur** du dépôt, et rend la question à
  l'humain quand rien ne le dit.
- **La mise à jour** applique des migrations de format numérotées (le
  verrou note le format ; une migration manquante arrête tout) et montre le
  diff entre la politique du projet et le gabarit, sans l'écrire.

## Conséquences

La qualité d'une initialisation depuis un document dépend de l'agent : les
contrôles garantissent qu'aucun fait n'est « mesuré » sans preuve, pas que
le document a été bien lu. C'est ce que le scénario 6 du banc du jalon 9
mesure. Aucune migration n'existe encore : le format n'a pas changé depuis
la première version.

Pour défaire : `socle init` n'est qu'un point d'entrée ; la mémoire posée
reste au format ordinaire.
