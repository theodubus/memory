<!-- socle: couche=demandes zone=publique -->
# D-0203 — Valider le format 4 du verrou du moteur et quatre valeurs attendues que la couche des consignes change

> date : 2026-11-25

## Décision demandée

Valider deux suites mécaniques de la spécification des consignes que vous avez validée : le verrou du moteur de ce dépôt qui note le format 4 de la mémoire, et quatre valeurs attendues de tests que les parts nouvelles du démarrage changent.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code confié à un agent d'IA : il garde la mémoire du projet (le dossier `memory/`), vérifie le travail de l'agent et vous pose en demandes les décisions qui vous reviennent.

**Le chantier.** Le 25 novembre, vous avez validé la spécification de la couche des consignes : vos consignes durables quittent le chantier actif pour un fichier à elles, `directives.md`, chacune avec son identifiant, votre texte exact et une ligne de résumé que le démarrage injecte. Le moteur, le texte que reçoit un projet et la migration des 24 consignes de ce dépôt sont faits, et leurs tests passent ; il reste à les commiter, puis la relecture et la fusion.

**La question.** Deux changements que la spécification entraîne ne sont nommés nulle part : la règle du dépôt veut votre validation pour un fichier protégé et pour une valeur attendue de test.

Le détail :

1. **Le verrou du moteur**, `.socle/engine.lock`, un fichier protégé que l'installeur écrit : la spécification fait passer le format de la mémoire de 3 à 4. L'installeur, relancé dans ce dépôt pour remettre les copies des skills, y écrit `format = 4`, et rien d'autre ne change. Le moteur ne lit pas ce numéro : il dit seulement à quel format la mémoire d'un projet a été posée.
2. **Quatre valeurs attendues.** La sortie du démarrage est bornée à 9 500 octets, partagée entre ses groupes. La spécification change les parts : état 25 %, chantier actif 18 % (au lieu de 40), consignes 25 % (nouvelles), faits 20 % (au lieu de 22), décisions 12 % (au lieu de 13). Quatre tests lisaient l'ancien partage :
   - dans `tests/test_demarrage.py`, `test_le_chantier_actif_au_dela_de_sa_part_se_coupe_seul_et_dit_son_chemin` : la ligne de coupe dit « une part de 3800 » ; après, « une part de 1710 » (18 % de 9 500) ;
   - `test_les_faits_au_dela_de_leur_part_se_coupent_sans_toucher_aux_decisions` : « une part de 2090 » ; après, « une part de 1900 » (20 %) ;
   - `test_la_coupe_de_l_etat_atteint_les_lignes_du_hook_en_dernier_et_dit_ou_les_lire` : il vérifie que le chantier actif garde sa part quand l'état déborde, en cherchant sa dernière ligne, « Étape 40 » ; son chantier de 40 lignes (2 611 octets) dépasse le budget nouveau de 1 600 octets. Après : le test se donne un chantier de 24 lignes (1 577 octets), dans son budget, et cherche « Étape 24 » ;
   - dans `tests/test_format_3.py`, `test_une_installation_au_format_3` : le verrou posé par l'installeur contient « format = 3 » ; après, « format = 4 ».

Un cinquième test, `test_quand_tout_depasse_chaque_partie_garde_sa_part`, ne change que son décor, complété de consignes.

## Éléments cités

Après @, l'empreinte de la version lue.

- D-0201@04cda4ed — votre validation de la spécification de la couche des consignes, le 25 novembre, qui fixe les parts et le format 4.
- B-0161@041fdcae — le besoin : une couche des consignes, remise à l'agent au démarrage.
- L-0042@de48e2b9 — le lot du chantier : la spécification, le moteur, le texte que reçoit un projet, la migration de ce dépôt.
- T-0188@e61fa3f4 — la tâche du moteur, qui porte ces changements.
- .socle/engine.lock sha256:9808bf4efec73b65

## Où regarder

- [La spécification](https://github.com/theodubus/memory/blob/303922ea1b5cd921abc842b5cab19d1fa544b05c/docs/fabrication/consignes-specification.md#le-démarrage), section « Le démarrage » : les parts nouvelles ; « Ce que reçoit un projet » : le format 4.
- Les tests avant le changement : [les trois de `tests/test_demarrage.py`](https://github.com/theodubus/memory/blob/303922ea1b5cd921abc842b5cab19d1fa544b05c/tests/test_demarrage.py#L252-L384) et [celui de `tests/test_format_3.py`](https://github.com/theodubus/memory/blob/303922ea1b5cd921abc842b5cab19d1fa544b05c/tests/test_format_3.py#L135-L143). Vérifier que chaque valeur nouvelle est celle que la spécification donne.

## Options

- **Valider** (recommandé). Effort : aucun de plus, les changements sont faits et leurs tests passent. Risque faible : chaque valeur se calcule des parts que vous avez validées. Réversible : une valeur se remet comme elle s'est changée.
- **Refuser**. Le format reste à 3 dans le moteur et la spécification se corrige sur ce point ; les parts, déjà validées, ne peuvent pas laisser ces tests à leurs valeurs : il faudrait revenir sur la spécification.

## Conséquences

Si vous validez : le moteur, le texte et la migration se commitent avec ces changements, passent la relecture et la CI, puis la pull request se fusionne. Si vous refusez : le lot attend que la spécification soit reprise sur ce que vous dites. Sans réponse : rien ne se commite de ce lot, et le lot suivant, la suppression des branches de l'agent, avance en attendant.

## Recommandation

Valider. Vérifié : avec ces valeurs, `tests/test_demarrage.py`, `tests/test_format_3.py`, `tests/test_skills.py` et les tests de la couche passent, 133 tests ; l'empreinte du verrou est celle que donne `socle check`. Supposé : rien.

## Réponses possibles

- `valider` — le verrou au format 4 et les quatre valeurs attendues ci-dessus : le lot se commite et se fait relire.
- `refuser` — le lot attend une spécification reprise sur ce que vous dites.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
