<!-- socle: couche=demandes zone=publique -->
# D-0201 — Valider la spécification de la couche des consignes : un fichier à elles, chacune son identifiant, son texte exact, sa ligne de résumé et son statut, la lecture du texte exact prouvée par son empreinte

> date : 2026-11-25

## Décision demandée

Valider la spécification de la couche des consignes, avant son code : où vivent vos consignes durables, ce que l'agent en reçoit au démarrage, et ce qui l'oblige à lire leur texte exact.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code confié à un agent d'IA : il garde la mémoire du projet (le dossier `memory/`), vérifie le travail de l'agent et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Chess, votre jeu d'échecs, le reçoit à sa mise à jour.

**Le chantier.** Vos consignes durables (une règle, une préférence, une interdiction qui vaut au-delà d'un tour) vivent dans le chantier actif, le fichier que l'agent reçoit en entier à chaque démarrage : 25 consignes, 87 % de son budget. Le 25 novembre, vous avez placé ce chantier avant la mise à jour de chess, puis validé son intention : une couche à elles, chaque consigne avec un identifiant, votre texte exact, une ligne de résumé et un statut, en vigueur ou levée, que seule votre parole lève ; au démarrage, la ligne de résumé ; le texte exact lu quand il sert.

**La question.** La forme de la mémoire change pour tous les projets, et chess la recevra : ce qui est coûteux à défaire une fois livré. Avant le code, valider la forme et les contrôles.

Ce que dit la spécification :

- **Le fichier.** Un fichier de la mémoire, `directives.md`, où chaque consigne porte un identifiant (`C-0003`), sa ligne de résumé en titre (120 octets au plus), votre texte exact cité mot pour mot, sa source (l'entrée du journal ou la demande où votre parole est consignée) et son statut. Votre texte ne change jamais ; l'agent peut récrire une ligne de résumé qui le trahit, et le diff le montre.
- **La levée.** Une consigne ne passe « levée » que par une demande que vous avez validée, en séance comme en file : comme un fait « validé » aujourd'hui.
- **Le démarrage.** L'agent reçoit la ligne de résumé de chaque consigne en vigueur, avec l'instruction de lire le texte exact avant de s'appuyer sur une, de l'appliquer à un cas que sa ligne ne tranche pas ou de la citer. Le chantier actif ne garde que le travail en cours ; son budget baisse de 3 700 à 1 600 octets, ses consignes parties.
- **La lecture prouvée.** Toute citation nouvelle d'une consigne dans la mémoire, journal compris, porte son empreinte (`C-0003@xxxxxxxx`), que seule la commande qui imprime le texte exact donne : sans elle, le contrôle refuse.
- **Ici**, les 25 consignes du chantier actif passent dans la couche dans le même lot, chacune avec votre texte relu au journal ; pour chess, l'agent les migre à sa mise à jour.

## Éléments cités

Après @, l'empreinte de la version lue.

- B-0161@b360dfe5 — le besoin : une couche des consignes, remise à l'agent au démarrage.
- D-0200@9d0d4824 — votre validation de l'intention, le 25 novembre, avec la ligne de résumé.
- D-0198@74687954 — votre décision du 25 novembre : ce chantier passe avant la mise à jour de chess.
- T-0187@7150c6e6 — la tâche qui vous soumet cette spécification ; votre réponse la clôt.
- L-0042@de48e2b9 — le lot du chantier : la spécification, le moteur, le texte que reçoit un projet, la migration de ce dépôt.

## Où regarder

- [La spécification](https://github.com/theodubus/memory/blob/c814e4f2c42bb47f4637a1e4f8daa7c8ecffd18e/docs/fabrication/consignes-specification.md) : « La couche », « Le démarrage », « Ce qui fait lire le texte exact » et « Modèle de menace » (ce que les contrôles arrêtent et laissent passer). Vérifier que la levée par une demande validée et la ligne de résumé récrivable vous conviennent.

## Options

- **La spécification telle qu'écrite** (recommandée). Effort : un agent auxiliaire pour le moteur, 3 à 4 points de la semaine (un point : 1 % de votre limite d'usage hebdomadaire), puis le texte et la migration par l'agent. Risque faible : un fichier de plus, et deux contrôles de la mémoire ; le hook de l'agent ne change pas. Réversible avant la mise à jour de chess ; après, par une migration inverse.
- **Avec vos changements** (répondre `refuser`, en disant ce qui change). Une réécriture et une demande nouvelle ; d'ici là, les consignes restent au chantier actif.

## Conséquences

Si vous validez : T-0187 se ferme, le moteur, le texte et la migration se font dans ce lot ; `valider` autorise aussi les valeurs attendues que la baisse du budget du chantier actif change : dans `tests/test_demarrage.py`, `test_une_borne_baissee_garde_les_demandes_et_ce_qui_revient_a_l_humain`, `test_le_chantier_actif_dans_son_budget_n_est_jamais_coupe_quoi_que_pesent_les_autres` et `test_une_mise_a_jour_signale_un_budget_du_chantier_actif_au_dela_de_sa_part` ; dans `tests/test_banc.py`, l'aide `relever`, qui lit ce budget dans le gabarit. Si vous refusez : la spécification se réécrit sur ce que vous dites. Sans réponse : rien ne change, et le lot attend.

## Recommandation

La spécification telle qu'écrite. Vérifié : la taille des consignes d'ici, la borne du démarrage et ses parts, les tests qui lisent le budget du chantier actif. Supposé : que 25 lignes de résumé de 120 octets au plus tiennent dans la part des consignes ; les tests du moteur le vérifieront.

## Réponses possibles

- `valider` — la spécification telle qu'écrite : le moteur, le texte et la migration se font dans ce lot.
- `refuser` — la spécification se réécrit sur ce que vous dites, et revient en demande.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
