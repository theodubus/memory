# Le socle, côté humain

Le socle fiabilise la mémoire, la documentation et les tests d'un projet
qu'un agent de code entretient. L'agent écrit ; des contrôles automatiques
attrapent ses erreurs pendant son travail, au commit et en CI ; toi, tu ne
tranches que ce qu'aucun contrôle ne peut trancher.

Les commandes se lancent à la racine du projet :
`python3 .socle/socle <commande>`. Ce guide s'affiche par
`python3 .socle/socle aide`.

## Ce que tu fais

### 1. Installer, mettre à jour

```sh
PYTHONPATH=<clone du socle>/moteur python3 -m socle install --target . --owner @toi
```

L'adaptateur (le langage du projet et ses outils) se déduit du dépôt ;
`--adapter <nom>` le force. Options : `--private compagnon` ou
`--private chiffre` (une mémoire privée), `--review lots` ou
`--review chaque-push` (relire ce qui part avant publication),
`--language en` (une mémoire en anglais), `--adoption` (un projet existant
dont des contrôles échouent : ils passent en avertissement, et ne pourront
que durcir).

La commande finit par « Et maintenant » : tes étapes suivantes, dans
l'ordre, chacune avec sa commande. Une mise à jour relance la même commande
depuis le clone à jour du socle.

### 2. Décrire le projet

```sh
python3 .socle/socle init --cadrage <document> --depot
```

Le document est archivé tel quel ; `--depot` relève ce que le dépôt
contient déjà (outils, tests, CI). L'agent te pose ensuite quelques
questions de départ, chacune avec son défaut.

### 3. Répondre aux demandes de l'agent

Quand une décision te revient (assouplir un garde-fou, changer la valeur
attendue d'un test, une décision coûteuse à défaire, une action
irréversible), l'agent écrit une demande qui se suffit à elle-même, et t'en
donne le lien. Tu réponds dans la conversation, par une des réponses
possibles écrites à sa fin ; l'agent consigne ta réponse avec ton texte
exact. `contexte-insuffisant` la lui renvoie, et il la réécrit.

Seul dans ton terminal :
`python3 .socle/socle answer D-NNNN <réponse> --text "<ton texte>"`.

### 4. Approuver tes propres changements protégés

La politique, les garde-fous, l'adaptateur, les hooks, la CI et le moteur
sont protégés : les changer sans validation fait échouer le commit. Quand
c'est toi qui les changes (une mise à jour du socle, ta politique) :

```sh
python3 .socle/socle approve --text "<raison>"
```

liste les fichiers protégés changés, puis les approuve sur confirmation, en
écrivant une demande validée (D-NNNN) à commiter avec eux. L'agent ne peut
pas lancer cette commande ; il te citera ce numéro à son tour suivant.

### 5. Relire avant publication, si tu l'as choisi

Avec `review` dans la section `[private]` de la politique, rien ne part vers
le dépôt public sans ton accord : l'agent te montre ce qui part, et tu
réponds dans la conversation. Seul dans ton terminal :
`python3 .socle/socle relu --by <toi>`.

### 6. Commiter toi-même

Les mêmes contrôles s'appliquent à tes commits. Une fonction publique
ajoutée ou modifiée est nommée par un test, ou dispensée dans le message du
commit, `Dispense-test: f — <raison>` : le hook te prévient au commit, la CI
refuse sans. Un correctif (sujet `fix:`, ou trailer `Corrige: B-NNNN`)
apporte un test qui échoue sur le commit parent.

## Ce que tu lis

- `python3 .socle/socle state` : où en est le projet, calculé à chaque
  fois, jamais recopié : commit, CI, backlog, demandes en attente, et ce qui
  te revient.
- La fin de chaque intervention de l'agent qui a agi : « Pour toi : », ce
  qui te revient, puis « Ensuite : », la suite.
- La mémoire, dans `memory/` : les faits et leur preuve, le chantier actif,
  les décisions, le journal, le backlog, les demandes.

## Ce qui ne dépend que de toi

- La politique d'autonomie, `.socle/policy.toml` : ce que l'agent décide
  seul, et ce qu'il te demande.
- Assouplir un garde-fou, dans `.socle/guardrails.toml` ; durcir est libre,
  pour l'agent aussi.
- Les actions irréversibles ou externes : pousser sur la branche par
  défaut, publier, supprimer à distance, dépenser. Le hook les refuse à
  l'agent ; il les met au backlog avec `pour : humain`, et l'état te les
  liste.
