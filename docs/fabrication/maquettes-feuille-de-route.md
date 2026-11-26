# Feuille de route : trois maquettes, 26 novembre 2026

Les maquettes soumises à Théo pour B-0364, la feuille de route qui doit
permettre de piloter un projet. Théo a validé, le 26 novembre, que la
forme retenue remplace les deux formats actuels, compact et détaillé,
partout (D-0212). Il a demandé un exemple fictif, et plusieurs s'il y a
plusieurs affichages pertinents : en voici trois, sur un même backlog
inventé, celui d'un moteur d'échecs, « Fou ».

Le backlog inventé : l'adoption d'une version du socle, en cours, hors de
tout jalon ; quatre jalons ensuite, dans l'ordre ; un besoin pour
l'humain ; douze besoins hors jalon, dont deux de priorité haute.

Dans la conversation, chaque titre serait un lien vers son entrée du
backlog : les identifiants ne s'afficheraient pas. Dans le terminal, ils
suivraient le titre, entre parenthèses.

## A. Le plan : chaque étape et ses besoins

Ce qui se fait maintenant, puis les étapes dans l'ordre, chacune avec ses
besoins en clair ; ce qui revient à l'humain ; la réserve, comptée.

```text
La suite de Fou — 26 novembre

Maintenant, hors étapes
 ▶ Finir l'adoption du socle 0.2.0
   reste : passer CLAUDE.md dans AGENTS.md

Les étapes, dans l'ordre
1. Embarquer le réseau N10 — 1 sur 4
   ✓ Entraîner N10 sur les parties de novembre
   · Mesurer N10 contre N8, 2 000 parties
   · Embarquer N10 dans le binaire
   · Situer le moteur sur la liste CCRL
2. Régler la recherche par SPSA — 0 sur 3
   · Les marges d'élagage
   · La gestion du temps
   · Valider en match de 10 000 parties
3. Accélérer la recherche — 0 sur 2
   · Paralléliser sur 8 fils
   · Évaluer 15 % plus vite
4. Nouvelle architecture de réseau — 0 sur 3

Pour toi
 · Copier les données d'entraînement sur un
   disque dur

En réserve, hors étapes : 12 besoins, dont
2 prioritaires : le test de déterminisme,
le temps que rembourse le ponder
```

## B. Le tableau de bord : une ligne par étape

L'avancement de chaque étape d'un coup d'œil, puis le prochain pas.

```text
Fou — 26 novembre

▶ Adoption du socle 0.2.0   ████████░░  3/4
  1 Réseau N10              ██▌░░░░░░░  1/4
  2 Réglages SPSA           ░░░░░░░░░░  0/3
  3 Vitesse de recherche    ░░░░░░░░░░  0/2
  4 Nouvelle architecture   ░░░░░░░░░░  0/3

Prochain pas : passer CLAUDE.md dans
AGENTS.md, puis mesurer N10 contre N8
Pour toi : 1 · En réserve : 12 besoins
```

## C. Les prochains pas : la file, dans l'ordre

Ce qui va se faire, pas à pas, chacun avec l'étape qu'il sert ; au-delà,
les étapes en une ligne.

```text
Fou — les cinq prochains pas

1. Passer CLAUDE.md dans AGENTS.md
   et l'adoption du socle est finie
2. Mesurer N10 contre N8, 2 000 parties
   étape 1, réseau N10
3. Embarquer N10 dans le binaire
   étape 1
4. Situer le moteur sur la liste CCRL
   ferme l'étape 1
5. SPSA sur les marges d'élagage
   ouvre l'étape 2, réglages

Puis : la fin de l'étape 2 (2 besoins),
l'étape 3, vitesse (2), l'étape 4,
nouvelle architecture (3)

Pour toi : copier les données
d'entraînement sur un disque dur
```

## La recommandation soumise

B en tête, pour la vue d'ensemble, puis A pour l'étape en cours et la
suivante, les autres en une ligne chacune ; « Pour toi » et la réserve à
la fin. C sert le récap de la clôture d'un lot, où seul compte ce qui
vient ensuite.

## Le choix de Théo, et deux variantes du plan

Théo retient A, le plan, et juge B puis A un peu lourd ; il demande des
variantes de A (J-2026-11-26-AD). Les deux qui suivent gardent la même
section « Maintenant » et le même backlog inventé.

### A1. Le plan complet

Trois ajouts à A : le travail en cours jusqu'à la tâche ; sous chaque
étape, son but en une ligne, que le jalon devrait alors donner ; la
réserve nommée par ses besoins prioritaires et datée.

```text
La suite de Fou — 26 novembre

Maintenant, hors étapes
 ▶ Finir l'adoption du socle 0.2.0 — 3 sur 4
     ✓ retoucher deux workflows
     ▶ passer CLAUDE.md dans AGENTS.md

Les étapes, dans l'ordre
1. Embarquer le réseau N10 — 1 sur 4
   pour jouer avec N10 et connaître sa force
   ✓ Entraîner N10 sur les parties de novembre
   · Mesurer N10 contre N8, 2 000 parties
   · Embarquer N10 dans le binaire
   · Situer le moteur sur la liste CCRL
2. Régler la recherche par SPSA — 0 sur 3
   pour gagner 20 Elo à réseau égal
   · Les marges d'élagage
   · La gestion du temps
   · Valider en match de 10 000 parties
3. Accélérer la recherche — 0 sur 2
   pour 30 % de nœuds par seconde en plus
4. Nouvelle architecture de réseau — 0 sur 3
   pour préparer le réseau d'après N10

Pour toi
 · Copier les données d'entraînement sur un
   disque dur

En réserve : 12 besoins, à trier à la fin
de l'étape 1
 ↑ Comparer les nœuds au test de
   déterminisme — en attente depuis 3 sem.
 ↑ Dépenser le temps que rembourse le
   ponder — en attente depuis 2 sem.
 · 10 autres, le plus ancien depuis 6 sem.
```

### A2. Le plan court

Seule l'étape suivante est dépliée ; les autres tiennent en une ligne.

```text
La suite de Fou — 26 novembre

Maintenant : finir l'adoption du socle
0.2.0 — reste CLAUDE.md dans AGENTS.md

Ensuite
1. Embarquer le réseau N10 — 1 sur 4
   ✓ Entraîner N10 sur les parties de novembre
   · Mesurer N10 contre N8, 2 000 parties
   · Embarquer N10 dans le binaire
   · Situer le moteur sur la liste CCRL
2. Régler la recherche par SPSA — 0 sur 3
3. Accélérer la recherche — 0 sur 2
4. Nouvelle architecture de réseau — 0 sur 3

Pour toi : copier les données
d'entraînement sur un disque dur
En réserve : 12 besoins, dont 2 prioritaires
```
