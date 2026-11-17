# Passation du lot L-0014

Cinq commits de sous-agents, faits le 17 novembre dans la session ouverte
à 12 h 20, pas encore relus : la fenêtre de cinq heures a passé 80 %
avant leur intégration. Les deux séries partent de 1ac3bb7, la tête
poussée de la branche ; chacune passe `verify --fast` seule. Ce dossier
se retire au commit qui les intègre.

1. `1-t0051-t0053/` : T-0051 (l'ancien numéro dans le hook et dans
   `socle url`, avec son défaut injecté), T-0052 (les trois pertes de la
   migration, le titre de T-0012), T-0053 (les derniers « sujet »).
2. `2-t0057-t0058/` : T-0057 (`socle roadmap`), T-0058 (ses
   déclencheurs) ; la série ouvre une tâche nouvelle du besoin B-0274,
   la section du socle d'AGENTS.md à recopier après T-0060, faute de
   place sous le budget de ce fichier.

## La suite

Intégrer les deux séries, puis T-0050 et T-0049, la revue du lot, et
une seule demande à Théo : les valeurs attendues des tests que change
T-0050, les mots qu'il a validés (D-0120), les copies protégées. D-0130
est validée et ses gestes fusionnés ici : L-0012 reprend, dans l'ordre
que dit J-2026-11-17-L.

## À l'intégration

- `git am -3` de la série 1, puis de la série 2 : leurs identifiants se
  recouvrent. Le journal : les entrées du 17 novembre de lettre L et M
  dans les deux séries, de lettre N dans la première, et la branche a
  déjà sa lettre L ; toutes se renumérotent, avec les mentions qui les
  citent (tâches closes, notes). Les notes de version : 2026-11-17-b et 2026-11-17-c
  dans les deux, 2026-11-17-d dans la première.
- Des conflits sont probables dans `engine/socle/messages_en.py`,
  `engine/socle/selftest.py`, `engine/socle/FORMAT.md` et
  `docs/fabrication/architecture.md`.

## Ce que les comptes rendus laissent ouvert

- Les valeurs de `--by` restent `lot|need`, celles de la spécification
  validée (D-0127) ; ADR-0027 dirait `batch`. À dire à Théo, sans le
  changer seul.
- Les copies protégées en retard sur leur gabarit, à rafraîchir par
  l'installeur sous la demande du lot. Empreintes nouvelles relevées par
  le sous-agent, à recalculer après T-0050 (qui change aussi le skill
  `socle-review`, et peut-être `socle-batch`) : le workflow `socle.yml`,
  `sha256:10da7cbe8c62e719` (avec un retard plus ancien, B-0218) ; le
  skill `socle-batch`, `sha256:1fd976d515435ddb`, à 7990 octets sur un
  plafond de 8000.
- Le hook refuse un ancien numéro dans un texte neuf avec sa propre
  raison, sauf sur une ligne qui nomme aussi l'identifiant actuel, ou
  dans un fichier qui le citait déjà : un choix du sous-agent, à juger
  à la revue.
