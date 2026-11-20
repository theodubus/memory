# Passation du lot L-0006, le 20 novembre à 13 h 50

La session du 20 novembre a mené le lot L-0006 (les copies protégées et
les skills) jusqu'à ses deux vagues d'implémentation. Elle s'arrête à
75 % de la fenêtre de cinq heures, la semaine à 36 % : la demande de fin
de lot, sa relecture à froid et la revue ne tiennent pas dans ce qui
reste. Théo a choisi de passer le lot à une session sur son autre
compte (au journal, dans les correctifs). Rien de ce qui n'est pas
relu n'est poussé : les dix-huit commits non relus sont rangés ici,
compressés, pour qu'aucun contrôle ne lise un correctif comme un texte
du dépôt. Ce dossier se retire dans le commit qui les intègre.

## Ce qu'il contient

- `l0006-non-relu.patch.gz` : dix-huit commits au format de
  `git format-patch`, pris sur 1cd49b6d, le sommet de la branche
  `ccr-600d2c63-b5a47g` avant ce dossier ; `gunzip -c` puis `git am -3`.
  Dans l'ordre : T-0061 et T-0084 ; T-0009 ; T-0010 ; T-0013 ; T-0110
  (le recul retiré) ; la première vague intégrée ; les
  réponses de Théo à D-0147 et à D-0148, avec les tests de T-0110 ; son
  choix de la passation ; T-0012, T-0017, T-0074,
  T-0075 ; les textes des skills (T-0011, T-0073, T-0014, T-0063,
  T-0015), T-0015 dans `socle-review`, T-0060, T-0069 ; l'entrée de
  cette passation. Le journal du jour, de N à AA, est
  dans le fichier qu'ouvre le correctif de T-0110.
- `l0006-tests-T-0060.patch.gz` : cinq tests de l'ancien texte que
  T-0060 retire, changés mais jamais commités ; `gunzip -c` puis
  `git apply`. Sans eux, la suite échoue sur le dernier correctif ;
  avec eux, le contrôle `tests.attendus` attend la demande qui les
  nomme.

Sur la branche distante, D-0147 et D-0148 paraissent encore en attente :
Théo y a répondu, « Valider D0147 » et « D0148 valider », et leurs
réponses sont dans les correctifs.

## Les cinq tests à nommer

1. `tests/test_skills.py`, `TestLaConduiteDUnLot.test_il_ne_renvoie_pas_a_l_atelier`, changé :
   l'expression des mots de l'atelier interdits dans `socle-batch`,
   `r"\b(?:ADR|[BDFJ])-\d|fabrication|chess|Théo|delegate-lot|Opus|Sonnet|Haiku|Fable"`,
   perd `|Fable` : le skill nomme désormais Fable (D-0119, T-0015).
2. `tests/test_skills.py`, `TestLaRevue.test_une_forme_du_shell_qu_un_agent_n_ecrit_pas_s_ecarte_pour_la_liste`,
   supprimé : il fixait la puce des formes du shell de `socle-review`,
   retirée par la décision d'architecture qui remplace ADR-0085.
3. `tests/test_skills.py`, `TestLaRevue.test_dans_un_projet_equipe_la_forme_se_signale_au_depot_du_socle`,
   supprimé : il fixait le signalement d'une forme au dépôt du socle
   (ADR-0085, remplacée).
4. `tests/test_revue.py`, `TestBarre.test_une_forme_qu_aucun_agent_n_ecrit_ne_bloque_pas_et_va_a_la_liste`,
   supprimé : il fixait la phrase des formes dans la consigne du
   relecteur.
5. `tests/test_revue.py`, la classe `TestLesFormesConnuesDuGuide`,
   supprimée (`test_le_guide_dit_la_regle_et_chaque_forme_cite_sa_note`
   et son aide `formes`) : elle fixait le texte du guide validé par
   D-0120 et la liste des formes, que T-0060 retire. Le modèle de menace
   du hook reste dans le guide, et un test nouveau le fixe.

## La reprise, dans l'ordre

1. Sur la branche de la session neuve, partie de la branche par
   défaut : `git fetch origin ccr-600d2c63-b5a47g`, puis
   `git merge --ff-only FETCH_HEAD` (la branche contient la branche
   par défaut) ; puis les dix-huit correctifs, `gunzip -c` et
   `git am -3`. Les cinq tests ensuite, dans l'arbre, non commités.
   Le dossier se retire dans un commit (`git rm -r`) ;
   `python3 .socle/socle verify --fast` ne passe qu'avec la demande de
   l'étape 2.
2. T-0072, la demande de fin de lot (skill `socle-request`, son
   relecteur à froid sur le plus capable jusqu'à Opus, que dit le skill) : les
   cinq tests ci-dessus, avec leur valeur avant et après, et les copies
   protégées à remettre, que nomme la ligne `copies` de l'état
   (`.claude/skills/socle-batch/SKILL.md`,
   `.claude/skills/socle-request/SKILL.md`,
   `.claude/skills/socle-review/SKILL.md`), chacune avec son empreinte
   nouvelle, l'installeur relancé en mode amont. Poussée seule d'abord ;
   les tests se commitent et se poussent ensuite sous elle (T-0075), la
   CI rouge jusqu'à la réponse.
3. La revue du lot entier depuis la branche par défaut (skill
   `delegate-lot`, puis `socle-review`) : les bloquants corrigés.
4. La pull request ; à la réponse de Théo, les copies remises et
   commitées avec elle ; la CI verte, la fusion par l'agent (D-0092), la
   distribution vérifiée ; le prompt de mise à jour de chess complété de
   tout ce que le lot change pour un projet installé (T-0060 y est
   déjà) ; la clôture du lot : B-0140, B-0185, B-0226, B-0242, B-0276
   et B-0278 semblent prêts à fermer, B-0233, B-0243 et B-0274 à
   vérifier, puis la feuille de route et `socle archive`.
5. Une branche ne se donne à Théo à supprimer qu'après vérification sur
   GitHub (un besoin des correctifs le demande) ; celle-ci le sera après la
   fusion.

Connu, à ne pas corriger dans le lot : l'avertissement
`demandes.reponse-seule` qui se lèvera à tort quand la réponse à la
demande de fin de lot sera poussée après les tests (un besoin et sa tâche,
dans les correctifs).
