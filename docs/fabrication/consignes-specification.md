# La couche des consignes : spécification

Soumise à Théo le 25 novembre 2026, avant son code. Elle répond à B-0161,
sur l'intention qu'il a validée le même jour (D-0200) : chaque consigne a
un identifiant, son texte exact, une ligne de résumé et un statut, en
vigueur ou levée, que seule sa parole lève ; le démarrage donne la ligne
de résumé de chaque consigne en vigueur ; l'agent lit le texte exact quand
il s'appuie sur une consigne, ce que le produit doit assurer. C'est un
changement du produit : chess le reçoit à sa mise à jour.

## Ce qu'elle fait

Aujourd'hui, une consigne durable de l'humain (une règle, une préférence,
une interdiction, qui vaut au-delà du tour) s'écrit au chantier actif si
elle touche le travail en cours, sinon au journal, avec son texte exact.
Ici, les 25 consignes du chantier actif en font 87 % (3 693 octets sur
3 700) : chaque mise à jour du chantier oblige à les resserrer, et le
texte exact n'est qu'au journal, que le démarrage n'injecte pas.

Désormais, elles ont leur couche, directives.md, sous `memory/`. Le chantier
actif ne garde que le travail en cours. Le démarrage injecte la ligne de
résumé de chaque consigne en vigueur ; le texte exact se lit par
`socle show C-NNNN`, et toute citation d'une consigne prouve qu'il a été
lu.

## La couche

Un fichier, comme la mémoire canonique : directives.md, sous `memory/`, en-tête
`<!-- socle: couche=consignes zone=publique -->` ; dans la zone privée,
directives.md de la zone privée, ses identifiants préfixés de `P`
(`PC-` et quatre chiffres). Le nom du fichier est anglais, comme les autres ; la couche
garde son nom interne.

```markdown
## C-0003 — La roadmap demandée se donne au format court

> statut : en vigueur · source : J-2026-11-25-T · date : 2026-11-25

> « … le texte exact de l'humain, mot pour mot … »
```

- **L'identifiant**, `C-` et quatre chiffres, se calcule :
  `socle new directive "résumé"` pose le squelette, comme pour les autres
  couches.
- **La ligne de résumé** est le titre : ce que l'agent lit à chaque
  démarrage. Elle tient en 120 octets au plus ; au-delà, le contrôle de
  format la refuse.
- **Le texte exact** est le corps : une citation au moins (une ligne qui
  commence par `>`, après la ligne de métadonnées), mot pour mot, telle
  que l'humain l'a écrite. Une consigne qui en réunit plusieurs les cite
  toutes. Une ligne de contexte peut suivre.
- **`source`**, obligatoire : l'entrée du journal (`J-`) ou la demande
  (`D-`) où la parole de l'humain est consignée.
- **Le statut** : `en vigueur` ou `levée`. `levée` exige
  `levée-par : D-NNNN`, une demande à laquelle l'humain a répondu
  `valider`, en séance comme en file : la parole de l'humain qui la lève,
  consignée comme celle qui valide un fait.

Ajout seul, comme les décisions : une consigne publiée ne change que par
sa ligne de métadonnées (le statut, `levée-par`) et par sa ligne de
résumé, que l'agent peut récrire si elle trahit le texte ; le texte exact
ne change jamais. Une consigne que l'humain modifie est une consigne
nouvelle, et la parole qui la modifie lève l'ancienne. `socle archive`
range les consignes levées dans le journal, comme les faits archivés :
leur identifiant reste résolu.

## Le démarrage

La sortie du démarrage (`socle state`, bornée à 9 500 octets) gagne un
groupe, `consignes`, placé juste après le chantier actif :

```text
--- memory/directives.md : 25 consigne(s) en vigueur, par leur ligne de résumé ; avant de s'appuyer sur une, de l'appliquer à un cas que sa ligne ne tranche pas ou de la citer, son texte exact : `python3 .socle/socle show C-NNNN` ---
C-0001 — Opus partout depuis le 12 novembre
C-0002 — La roadmap demandée se donne au format court
…
```

Les levées n'y sont pas. Les parts de la borne deviennent : état 25 %,
chantier actif 18 %, consignes 25 %, faits 20 %, décisions 12 % (au lieu
de 25, 40, 0, 22 et 13). Ce qu'un groupe laisse de sa part va, comme
aujourd'hui, à ceux qui dépassent la leur ; un groupe coupé le dit sur
la ligne `!! coupé`, avec où lire le reste. Le budget du chantier actif
du gabarit des garde-fous suit sa part (1 600 octets) ; celui des
consignes, d'abord celui de la mémoire canonique (16 000), est de
24 000 octets depuis le 26 novembre (D-0220) : une consigne ne se lève
que sur la parole de l'humain, et le fichier ne fait que croître, alors
que le démarrage n'en charge que les lignes de résumé, sous sa part. Un
projet installé garde sa valeur à la mise à jour ; la reprendre assouplit
son garde-fou, et se demande donc à son humain. Un projet dont le
budget du chantier actif dépasse sa part en est averti, par l'état et à
la mise à jour, comme aujourd'hui (`alerte_budget_actif`).

## Ce qui fait lire le texte exact

1. **L'en-tête du groupe**, plus haut, le dit à chaque démarrage.
2. **La lecture prouvée**, étendue : une citation d'une consigne ajoutée
   dans n'importe quel fichier de la mémoire, le journal et le chantier
   actif compris, porte son empreinte (`C-NNNN@xxxxxxxx`), celle de la
   version actuelle, que seul `socle show C-NNNN` imprime. Sans elle, ou
   périmée, ou inventée, le contrôle de la lecture prouvée la refuse.
   Ailleurs, la règle ne change pas.
3. **Les instructions du projet** (la section du socle d'`AGENTS.md`) :
   « Une consigne de l'humain [...] s'écrit dans les consignes
   (`socle new directive`), avec son texte exact, et au journal ; avant
   de s'appuyer sur une consigne, son texte exact se lit. »

Le test que demande B-0161 : l'auto-test du moteur injecte une entrée du
journal qui cite une consigne sans empreinte, puis avec une empreinte
périmée ; le contrôle les refuse, et laisse passer le témoin sain, qui
porte l'empreinte actuelle.

## Les contrôles

Sur le modèle de la mémoire canonique, chacun avec son défaut injecté et
son témoin sain :

- le format : l'identifiant, le statut, `source` qui mène à une entrée
  existante, une citation au moins dans le corps, la ligne de résumé dans
  sa borne ;
- `levée` sans `levée-par`, ou vers une demande sans réponse `valider` de
  l'humain : refusé ;
- le texte exact changé, ou une consigne retirée sans être archivée :
  refusé, comme une décision réécrite ;
- la lecture prouvée d'une citation de consigne, plus haut.

Le hook de l'agent ne change pas (ADR-0098).

## Ce que reçoit un projet

- L'installeur pose le fichier directives.md de `memory/`, vide sous son en-tête, à
  l'installation et à la mise à jour, s'il manque ; le gabarit des
  garde-fous, son budget et le budget baissé du chantier actif ; le
  format de la mémoire passe à 4 (`.socle/engine.lock`).
- `FORMAT.md` décrit la couche ; le guide (`HELP.md`) dit où va une
  consigne et comment elle se lève ; le gabarit d'`AGENTS.md` change sa
  règle des consignes et sa table des couches, sous son budget ; les
  skills qui parlent des consignes (`socle-request`, pour une levée en
  séance) le disent.
- La note de version, en français et en anglais, dit le changement et la
  migration : les consignes du chantier actif passent dans la couche, une
  par une, avec leur texte exact relu au journal ; rien ne se fait sans
  l'agent, qui la mène à la mise à jour (pour chess, le prompt de sa mise
  à jour le dit, T-0186).

Ici, la migration se fait dans le même lot : les 25 consignes du
chantier actif, chacune avec son texte exact relu dans l'entrée du
journal qu'elle cite.

## Modèle de menace

La couche ne pose pas de garde-fou nouveau contre l'agent : elle déplace
des consignes, et ajoute deux contrôles de la mémoire. Ce qu'ils arrêtent :

- **une consigne levée sans la parole de l'humain** : `levée` exige une
  demande qu'il a validée, dont la réponse est un fichier protégé ;
- **un texte exact réécrit**, qui ferait dire à l'humain ce qu'il n'a pas
  dit : le corps d'une consigne publiée ne change pas ;
- **une consigne citée sans être lue** : l'empreinte d'une citation
  nouvelle.

Ce qu'ils laissent passer :

- **une consigne jamais écrite** : rien ne voit qu'une parole de
  l'humain, dans la conversation, n'a pas été consignée ; c'est le cas
  d'aujourd'hui, que la règle d'`AGENTS.md` couvre seule ;
- **un texte exact faux dès l'écriture** : la citation de la conversation
  ne se vérifie pas ; la source au journal et la relecture du diff par
  l'humain en sont la seule garde, comme pour une réponse consignée en
  séance ;
- **une ligne de résumé qui trahit le texte**, récrite par l'agent : le
  diff la montre, le texte exact reste à côté ;
- **une consigne appliquée sans être citée** : l'empreinte ne prouve la
  lecture que d'une consigne citée ; l'en-tête du démarrage la demande
  pour le reste.

## Ce qui reste hors du champ

- Les consignes de l'agent à lui-même : elles restent des décisions.
- La levée automatique d'une consigne datée (« jusqu'à vendredi ») : sa
  ligne le dit, et l'humain la lève.
