<!-- socle: couche=demandes zone=publique -->
# D-0203 — Valider le format 4 du verrou du moteur et les valeurs attendues que la couche des consignes change

> date : 2026-11-25

## Décision demandée

Valider les suites mécaniques de la spécification des consignes que vous avez validée : le verrou du moteur de ce dépôt au format 4 de la mémoire, et les valeurs attendues de tests que les parts nouvelles du démarrage changent.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code confié à un agent d'IA : il garde la mémoire du projet (le dossier `memory/`), vérifie le travail de l'agent et vous pose en demandes les décisions qui vous reviennent.

**Le chantier.** Le 25 novembre, vous avez validé la spécification de la couche des consignes : vos consignes durables quittent le chantier actif pour un fichier à elles, `directives.md`, chacune avec son identifiant, votre texte exact et une ligne de résumé que le démarrage injecte. Le moteur, le texte que reçoit un projet et la migration des 24 consignes de ce dépôt sont faits, et leurs tests passent ; restent le commit, la relecture et la fusion.

**La question.** La règle du dépôt veut votre validation pour un fichier protégé et pour une valeur attendue de test : certains changements ne sont nommés nulle part, d'autres ne sont plus couverts.

1. **Le verrou du moteur**, `.socle/engine.lock`, un fichier protégé que l'installeur écrit : la spécification fait passer le format de la mémoire de 3 à 4, et l'installeur, relancé ici pour remettre les copies des skills, y écrit `format = 4`, rien d'autre.
2. **Quatre valeurs nouvelles.** La sortie du démarrage est bornée à 9 500 octets, partagée entre ses groupes ; la spécification en change les parts : état 25 %, chantier actif 18 % (au lieu de 40), consignes 25 %, faits 20 % (au lieu de 22), décisions 12 %. Dans `tests/test_demarrage.py` :
   - `test_le_chantier_actif_au_dela_de_sa_part_se_coupe_seul_et_dit_son_chemin` : « une part de 3800 » devient « une part de 1710 » ;
   - `test_les_faits_au_dela_de_leur_part_se_coupent_sans_toucher_aux_decisions` : « une part de 2090 » devient « une part de 1900 » ;
   - `test_la_coupe_de_l_etat_atteint_les_lignes_du_hook_en_dernier_et_dit_ou_les_lire` vérifie que le chantier actif garde sa part en cherchant sa dernière ligne, « Étape 40 » ; ce chantier de 2 611 octets dépasse le budget nouveau de 1 600. Il se donne un chantier de 24 lignes (1 577 octets) et cherche « Étape 24 ».

   Dans `tests/test_format_3.py`, `test_une_installation_au_format_3` : « format = 3 » devient « format = 4 ».
3. **Quatre valeurs déjà validées** avec la spécification, la baisse du budget du chantier actif de 3 700 à 1 600 octets : dans `tests/test_demarrage.py`, `test_une_borne_baissee_garde_les_demandes_et_ce_qui_revient_a_l_humain`, `test_le_chantier_actif_dans_son_budget_n_est_jamais_coupe_quoi_que_pesent_les_autres` et `test_une_mise_a_jour_signale_un_budget_du_chantier_actif_au_dela_de_sa_part` ; dans `tests/test_banc.py`, l'aide `relever`. La spécification fusionnée sur la branche principale, votre validation ne les couvre plus, faute d'une tâche ouverte qui la cite : elles reviennent ici, inchangées.

## Éléments cités

Après @, l'empreinte de la version lue.

- D-0201@04cda4ed — votre validation de la spécification de la couche des consignes, le 25 novembre, qui fixe les parts, le budget et le format 4.
- B-0161@041fdcae — le besoin : une couche des consignes, remise à l'agent au démarrage.
- L-0042@de48e2b9 — le lot du chantier : la spécification, le moteur, le texte que reçoit un projet, la migration de ce dépôt.
- T-0188@e61fa3f4 — la tâche du moteur, qui porte ces changements.
- .socle/engine.lock sha256:9808bf4efec73b65

## Où regarder

- [La spécification](https://github.com/theodubus/memory/blob/303922ea1b5cd921abc842b5cab19d1fa544b05c/docs/fabrication/consignes-specification.md#le-démarrage), « Le démarrage » : les parts et le budget ; « Ce que reçoit un projet » : le format 4.
- Les tests avant le changement : [`tests/test_demarrage.py`](https://github.com/theodubus/memory/blob/303922ea1b5cd921abc842b5cab19d1fa544b05c/tests/test_demarrage.py#L252-L520) et [`tests/test_format_3.py`](https://github.com/theodubus/memory/blob/303922ea1b5cd921abc842b5cab19d1fa544b05c/tests/test_format_3.py#L135-L143). Vérifier que chaque valeur nouvelle est celle que la spécification donne.

## Options

- **Valider** (recommandé). Effort : aucun de plus, tout est fait et passe. Risque faible : chaque valeur se calcule de ce que vous avez validé. Réversible : une valeur se remet comme elle s'est changée.
- **Refuser**. Le format reste à 3 et la spécification se corrige ; les parts, déjà validées, ne peuvent pas laisser ces tests à leurs valeurs sans revenir sur elle.

## Conséquences

Si vous validez : le lot se commite avec ces changements, passe la relecture et la CI, puis sa pull request se fusionne. Si vous refusez : le lot attend que la spécification soit reprise sur ce que vous dites. Sans réponse : rien de ce lot ne part, et le lot suivant, la suppression des branches de l'agent, avance en attendant.

## Recommandation

Valider. Vérifié : avec ces valeurs, les tests du démarrage, du format, des skills et de la couche passent, 133 tests ; l'empreinte du verrou est celle que donne `socle check`. Supposé : rien.

## Réponses possibles

- `valider` — le verrou au format 4 et les valeurs attendues ci-dessus : le lot se commite et se fait relire.
- `refuser` — le lot attend une spécification reprise sur ce que vous dites.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
