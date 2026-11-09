<!-- socle: couche=backlog zone=publique -->
# B-0141 — Le relecteur sans contexte agit dans le dépôt : une commande mal dirigée y a lancé l'installeur, et le hook l'a laissé faire

> statut : ouvert · origine : J-2026-11-09-B · lu : backlog@1324e2bb

Pendant la revue adversariale de l'adaptateur `kotlin` (J-2026-11-09-B),
le relecteur, un sous-agent sans contexte, voulait éprouver l'installeur
dans un dossier jetable ; une commande qui n'avait pas changé de dossier l'a
lancé sur ce dépôt, en mode projet. Le hook avant outil laisse l'agent
relancer l'installeur, la voie prévue pour rafraîchir les copies protégées,
sans juger sa cible ni son mode : le verrou du moteur, le workflow de CI et
CODEOWNERS ont changé, un workflow de mutation est apparu, et les hooks ont
jugé avec une copie figée du moteur. Le contrôle des fichiers protégés a
arrêté le commit ; le hook a ensuite refusé la remise en état, qu'il
réserve à l'humain, et Théo l'a autorisée.

Pistes, chacune touchant un fichier protégé ou le hook, donc une demande :
- le dossier de `socle review` et le skill `socle-review` disent au
  relecteur de n'écrire que dans un dossier temporaire qu'il crée ;
- le hook refuse à l'agent l'installeur sur la racine du projet dans un
  autre mode que celui de son verrou ;
- la remise d'un fichier protégé à son état commité devient permise à
  l'agent, au risque d'effacer un changement que l'humain n'a pas encore
  commité.

Fait quand :
- [ ] un relecteur ne peut plus changer un fichier protégé du dépôt sans que le hook le refuse, ou la raison de ne pas l'empêcher est écrite, et un test le montre
