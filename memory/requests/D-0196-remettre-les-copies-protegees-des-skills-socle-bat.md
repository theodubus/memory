<!-- socle: couche=demandes zone=publique -->
# D-0196 — Remettre les copies protégées des skills socle-batch, socle-handoff, socle-request et socle-review de ce dépôt sur leurs gabarits que L-0039 a changés, et changer les tests qui lisent leurs textes

> date : 2026-11-25

## Décision demandée

Autoriser l'installeur à remettre, dans ce dépôt, les copies des quatre skills que le lot a récrits, et autoriser le changement des sept tests qui lisent leur ancien texte.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code confié à un agent d'IA : il garde la mémoire du projet, vérifie le travail de l'agent et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Chess, votre jeu d'échecs, recevra ces changements à sa prochaine mise à jour.

**Le chantier.** Le lot en cours applique trois de vos décisions du 25 novembre : la page des règles de l'organisation proportionnée ; votre accord donné avant le lot qui change un test le couvre désormais ; une session neuve reprend sur toute demande de reprendre. Les tâches sont faites et relues sans constat bloquant.

**La question.** Un skill est une procédure que l'agent charge quand elle sert. Le socle en garde le modèle, le gabarit ; l'installeur en pose une copie dans `.claude/skills/`, où l'agent de ce dépôt la lit. La politique, que vous seul modifiez, protège ces copies : l'installeur ne les réécrit que sur votre accord. Changer la valeur qu'un test attend, ou supprimer un test, demande aussi votre accord, qui nomme le test.

**Ce que changent les copies** : les règles de la page, et la passation écrite dans la mémoire, que « reprends » reprend. Le ménage retire trois règles qui n'ont rien protégé en usage : un seul sous-agent au-delà de 75 % de la semaine, le compactage à la fin de chaque lot, deux rappels que les instructions disent déjà.

**Les tests**, dans `tests/test_skills.py` sauf le dernier :

- `test_il_dit_la_consommation_le_changement_de_session_et_l_apres_fusion` : « La session est l'unité de budget » au lieu d'« Un lot par session », sans « 75 % » ;
- `test_il_dit_quand_compacter_et_quel_modele_pour_quel_travail` : le compactage, seulement si vous gardez la session au-delà du seuil ;
- `test_une_petite_tache_s_implemente_dans_la_session_qui_orchestre`, supprimé, remplacé par `test_un_sous_agent_implemente_quand_il_paie` ;
- `test_resserre_sous_son_plafond_il_garde_ses_regles` : un sous-agent arrêté se reprend depuis sa copie isolée, au lieu de ne pas se reprendre ;
- `test_le_moment_ses_seuils_et_les_bornes` : le coût du lot au départ d'une session programmée, au lieu du seuil de 15 % ;
- `test_changer_de_session_range_puis_renvoie_a_socle_handoff` : « sinon, elle change de session » au lieu de la phrase du compactage retirée ;
- `test_le_skill_de_l_atelier_fait_fusionner_la_branche_de_passation_et_suit_le_circuit_court` (`tests/test_suite_du_projet.py`) : « L'orchestrateur implémente, sauf quand un sous-agent paie ».

Trois d'entre eux (la consommation, le moment, changer de session) sont aussi des tests de la reprise que votre réponse du 25 novembre couvre ; ce qu'ils changent pour la page, cette demande le nomme. Un test nouveau vérifie chaque section de la page dans les skills, les instructions et le guide.

## Éléments cités

Plus bas : `L-`, un lot ; `T-`, une tâche ; `D-`, une demande ou une décision ; après @, l'empreinte de la version lue ; `sha256:`, celle du fichier que l'installeur posera.

- .claude/skills/socle-batch/SKILL.md sha256:b0dc4f064421ee0d
- .claude/skills/socle-handoff/SKILL.md sha256:dc6f763d7749ad38
- .claude/skills/socle-request/SKILL.md sha256:936a81807930b6ca
- .claude/skills/socle-review/SKILL.md sha256:2b367282daa81747
- L-0039@7483c5d1 — le lot en cours, que cette demande permet de clore.
- T-0183@9780d82b — la tâche qui applique la page à ces skills, aux instructions et au guide.
- D-0195@2890f470 — votre validation de la page des règles, le 25 novembre.
- D-0190@cd1cd57d — votre validation de la reprise, avec sa réserve, qui couvre déjà les tests de la passation.

## Où regarder

- [La page validée](https://github.com/theodubus/memory/blob/75250ef782592bbedbab7e9f5b90549307c486b2/docs/fabrication/organisation-proportionnee.md) : ce que les skills doivent dire.
- [`socle-batch`](https://github.com/theodubus/memory/blob/75250ef782592bbedbab7e9f5b90549307c486b2/engine/socle/templates/skills/socle-batch/SKILL.md) : « Qui implémente » et « La consommation ».
- [`socle-review`](https://github.com/theodubus/memory/blob/75250ef782592bbedbab7e9f5b90549307c486b2/engine/socle/templates/skills/socle-review/SKILL.md) : « Quand ».
- [`socle-request`](https://github.com/theodubus/memory/blob/75250ef782592bbedbab7e9f5b90549307c486b2/engine/socle/templates/skills/socle-request/SKILL.md) : l'étape 3, « Une conception à trancher ».
- [`socle-handoff`](https://github.com/theodubus/memory/blob/75250ef782592bbedbab7e9f5b90549307c486b2/engine/socle/templates/skills/socle-handoff/SKILL.md) : « Écrire la passation », « La session neuve ».

## Options

- **Valider** : les copies remises, les tests commités avec votre réponse. Effort : une commande. Risque : faible, du texte relu. Réversible.
- **Refuser** : les copies et les tests restent les anciens ; l'agent suit encore l'ancienne passation, que le moteur ne connaît plus, et la CI reste rouge. Effort : récrire le lot. Réversible.

## Conséquences

Si vous validez : l'agent clôt le lot et fusionne la pull request, CI verte ; la fusion publie le moteur. Si vous refusez : le lot attend vos changements. Sans réponse : la pull request attend, rouge.

## Recommandation

Valider : ce sont les textes de la page que vous avez validée et de votre réserve sur la reprise.

Vérifié : les empreintes sont celles des gabarits français relus ; avec les tests changés, la suite entière passe (1 507 tests), et l'auto-test du moteur aussi.

Supposé : rien.

## Réponses possibles

- `valider` — l'installeur remet les quatre copies ; les tests changés se commitent avec votre réponse.
- `refuser` — les copies et les tests restent les anciens ; le lot attend.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
