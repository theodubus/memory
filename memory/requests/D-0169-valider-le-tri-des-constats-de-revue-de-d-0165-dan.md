<!-- socle: couche=demandes zone=publique -->
# D-0169 — Valider le tri des constats de revue de D-0165 dans les textes du produit : trois tests qui lisent la règle, et la copie protégée du skill socle-review de ce dépôt

> date : 2026-11-24

## Décision demandée

Autoriser le changement des valeurs attendues de trois tests, qui lisent la règle de tri des constats de revue, et la remise de la copie protégée du skill `socle-review` de ce dépôt sur son gabarit, pour que le socle que reçoit chaque projet dise le tri que vous avez décidé le 24 novembre.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code tenu par un agent d'IA : il garde la mémoire du projet, donne à l'agent le bon contexte, vérifie son travail par des tests, et vous pose en demandes les décisions qui vous reviennent. Chess, votre jeu d'échecs, le reçoit à ses mises à jour ; ce dépôt s'en sert lui-même.

**Le chantier.** Avant de livrer un lot (des tâches menées ensemble), l'agent le fait relire par un agent sans contexte, le relecteur, qui classe ses constats. La règle d'aujourd'hui envoie au backlog, la liste de ce qui reste à faire, tout constat qui ne bloque pas « s'il peut se produire dans l'usage normal du projet » : un relecteur en trouve toujours, d'où 111 entrées ouvertes par les revues du 14 au 23 novembre. Le 24 novembre, vous avez écrit : « passer 10h sur un cas limite qui arrive rarement, et qu'en pratique n'est qu'une légère gêne pour l'agent qu'il peut gérer lui même c'est non ». Puis vous avez validé des critères de tri, dont ceci : « Les bloquants d'une revue (un critère contredit, une régression, une perte de données) se corrigent dans le lot ; ses autres constats passent ces tests comme le reste », et « un sujet écarté ou abandonné revient s'il est vu en usage réel ».

**La question.** Ces critères valent dans ce dépôt, où le skill `delegate-lot` (la procédure propre à ce dépôt pour mener un lot) les applique déjà. Chaque projet installé n'en reçoit que la règle générale, celle de la revue : elle est écrite, en français et en anglais, dans la consigne que reçoit le relecteur, le skill `socle-review` (la procédure de la revue), les instructions de l'agent (`AGENTS.md`) et le guide (`HELP.md`). Trois tests lisaient l'ancien texte : changer ce qu'un test attend vous revient. Et la copie de ce skill dans ce dépôt (`.claude/skills/`), que seul l'installeur réécrit sur votre accord, ne se remet sur le texte nouveau de son modèle, le gabarit, que si vous le validez.

**Le texte nouveau** (le skill, section « Les constats ») :

> **Pour le backlog** : un constat qui ne bloque pas va au backlog seulement s'il est important et a été vu en usage réel (une session, une CI, un message de l'humain le montre), ou si son effet serait irréversible (une perte de données, un push sur la branche par défaut, une suppression).
>
> **Écarté** : tout autre constat, dont un cas imaginé et jamais vu, une légère gêne que l'agent règle lui-même (ce que rattrape un contrôle, la CI ou une erreur qu'il voit aussitôt), un contournement hors du modèle de menace, et un constat infondé. En cas de doute, il s'écarte. Une ligne du récap dit pourquoi chacun est écarté ; il revient s'il est vu en usage réel.

En anglais :

> **For the backlog**: a finding that does not block goes to the backlog only if it matters and has been seen in real use (a session, a CI run, a message from the human shows it), or if its effect would be irreversible (lost data, a push to the default branch, a deletion).
>
> **Dismissed**: any other finding, including a case imagined and never seen, a slight nuisance the agent handles itself (what a check, the CI or an error it sees at once catches), a bypass outside the threat model, and an unfounded finding. When in doubt, it is dismissed. One line of the recap says why each is dismissed; it comes back if seen in real use.

Un constat imaginé et jamais vu s'écarte donc, quel qu'il soit, sauf si son effet serait irréversible. Les bloquants ne changent pas : ils se corrigent dans le lot. La consigne du relecteur dit la même chose en une phrase ; les instructions de l'agent : « un autre va au backlog s'il est important et vu en usage réel, ou d'effet irréversible ; sinon il s'écarte, et revient s'il est vu ».

**Les trois tests**, chacun avec ce qu'il attend avant, puis après :

1. `test_la_consigne_donne_la_barre_et_les_trois_classes` (`tests/test_revue.py`), la consigne du relecteur. Avant : « un constat qui ne bloque pas, s'il peut se produire dans l'usage normal du projet, ou si rien ne rattrape ensuite son effet » et « un constat exotique ». Après : « un constat qui ne bloque pas, seulement s'il est important et a été vu en usage réel », « ou si son effet serait irréversible », « tout autre constat, dont un cas imaginé et jamais vu » et « en cas de doute, il s'écarte, et revient s'il est vu en usage réel ».
2. `test_poses_dans_un_projet_ils_ne_disent_ni_la_procedure_ni_la_liste` (`tests/test_revue.py`, sa table `CLASSES`), la consigne dans un projet neuf, en français et en anglais. Avant : « un constat exotique (un geste rare, une forme qu'on n'écrit que pour contourner, un cas jamais reproduit) dont l'effet est rattrapé ». Après : « tout autre constat, dont un cas imaginé et jamais vu, une légère gêne que l'agent règle lui-même », et son anglais.
3. `test_les_constats_le_dossier_et_le_modele_de_menace_d_une_seule_maniere` (`tests/test_skills.py`), le skill et les instructions, en français et en anglais. Avant : les phrases de l'ancienne règle. Après : celles du texte nouveau ci-dessus.

Aucun test n'est supprimé ; les autres phrases qu'ils lisent ne changent pas.

## Éléments cités

Plus bas : après @, l'empreinte de la version lue ; `sha256:`, celle du fichier que l'installeur posera.

- .claude/skills/socle-review/SKILL.md sha256:32d7983efbc74305
- D-0165@d8aaca8b — votre règle du 24 novembre, citée plus haut : pas de temps pour un cas limite rare, légère gêne que l'agent gère.
- D-0167@4a24a192 — votre validation du 24 novembre des critères de tri, dont la part citée plus haut.
- D-0168@f095a79d — la demande voisine, posée le même jour, qui trie le backlog ouvert par ces critères.
- ADR-0108@dd9f13ee — la décision écrite par l'agent qui remplace le tri d'avant par celui-ci.
- ADR-0073@1e48220c — la décision du 13 novembre qui posait le tri d'avant.
- B-0342@088e016b — le besoin : le tri des revues remplit le backlog de cas limites.
- T-0172@a72c6daa — la tâche qui écrit ce tri dans le produit.

## Où regarder

- [Le skill `socle-review` aujourd'hui](https://github.com/theodubus/memory/blob/73bc7489b157118192dd1579206bded5e376c0d0/engine/socle/templates/skills/socle-review/SKILL.md) : sa section « Les constats », que le texte nouveau ci-dessus remplace ; le reste du skill ne change pas.

## Options

- **Valider** : les trois tests attendent le texte nouveau ; l'installeur remet la copie protégée ; le tout part dans ce lot, avec une note de version, et chess le reçoit à sa mise à jour. Effort : fait, en attente de votre réponse. Risque : faible, du texte. Réversible : revenir au texte d'avant.
- **Refuser** : le socle garde l'ancien tri pour chaque projet, et la copie de ce dépôt aussi ; ici, le skill `delegate-lot` continue d'appliquer vos critères, qui priment.

## Conséquences

Si vous validez : le changement est commité et poussé dans ce lot, avec votre réponse. Si vous refusez : il est défait, T-0172 se clôt sur votre réponse. Sans réponse : rien ne part ; le lot avance sur ses autres tâches. Les entrées déjà ouvertes par les revues ne dépendent pas de cette demande : la demande voisine, D-0168, les juge.

## Recommandation

Valider : c'est votre décision du 24 novembre, dite dans les textes que reçoit chaque projet.

Vérifié : les trois tests passent sur le texte nouveau ; les autres tests de la revue et des skills aussi.

Supposé : qu'un relecteur applique « important » comme vous l'entendez, un ajout ou un bug qui compte, pas un cas limite ; la revue de ce lot en sera le premier essai, et son récap vous dira ce qu'elle a écarté.

## Réponses possibles

- `valider` — les trois tests changent comme dit plus haut, la copie protégée est remise, et le tri nouveau part dans ce lot.
- `refuser` — le changement est défait ; T-0172 se clôt sur votre réponse.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
