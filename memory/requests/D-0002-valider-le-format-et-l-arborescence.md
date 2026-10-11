<!-- socle: couche=demandes zone=publique -->
# D-0002 — L'emplacement des fichiers du socle dans un projet, et la façon d'écrire une entrée de mémoire, te conviennent-ils avant qu'on installe ailleurs ?

> date : 2026-10-10 · réécrite après ton retour du 10 oct. · bloque : l'installation sur chess ou un autre projet

## Décision demandée

Accepter, amender ou refuser l'arborescence et le format de mémoire décrits
ci-dessous, qui deviendront difficiles à changer dès que le socle sera
installé sur un premier projet.

## Contexte

Le cadrage dit lui-même que ses noms de fichiers sont indicatifs et seront
fixés à la fabrication. Je les ai fixés pour construire les jalons 2 à 5 ; ce
dépôt les utilise déjà pour sa propre mémoire. Tant qu'aucun autre projet n'a
le socle, en changer ne coûte qu'une réécriture du moteur et de ses tests.
Après la première installation (chess, au jalon 8), chaque changement
exigera une migration scriptée dans chaque projet. D'où la question
maintenant.

**L'arborescence, dans un projet installé.**

```text
AGENTS.md                  instructions de l'agent ; CLAUDE.md contient seulement « @AGENTS.md »
.socle/                    caché : ce qui fait tourner le socle
  socle                    le lanceur : python3 .socle/socle <commande>
  moteur/                  le moteur copié, jamais modifié à la main
  moteur.lock              sa version et son empreinte
  politique.toml           les 8 règles d'autonomie, modifiées par toi seul
  garde-fous.toml          seuils et budgets : durcir libre, assouplir sur demande
  adaptateur.toml          les commandes du langage (format, lint, tests…)
  git-hooks/               les hooks git
memoire/                   visible : la mémoire du projet
  canonique.md             les faits vérifiés
  actif.md                 le chantier en cours
  backlog.md               les sujets à traiter
  decisions/ADR-0001-….md  une décision par fichier
  journal/2026-10.md       un fichier par mois
  demandes/D-0001-….md     une demande par fichier, ta réponse à côté
```

**Une entrée de mémoire**, ici un fait :

```markdown
## F-0007 — Le bench à profondeur 7 explore 70 452 nœuds

> statut : mesuré · preuve : cmd:`cargo run --release -- bench 7` · date : 2026-10-10

Mesuré sur le binaire de base.
```

Un titre qui commence par l'identifiant, une ligne de métadonnées
« clé : valeur » séparées par des points médians, puis du texte libre. Les
identifiants : F pour les faits, B pour le backlog, ADR pour les décisions, D
pour les demandes, J suivi de la date pour le journal.

**Un écart avec le cadrage.** Il évoquait une file `PENDING.md`. J'ai mis un
fichier par demande dans `memoire/demandes/`, ta réponse dans un fichier
voisin : une demande à laquelle tu as répondu peut ainsi être gelée (la CI
refuse qu'on la modifie après coup), et l'état calculé au démarrage liste
celles qui attendent, ce qui tient lieu de file.

## Éléments cités

- ADR-0003 — la fiche de décision qui consigne ce choix d'arborescence et de format, au statut « proposée » en attendant ta réponse.

## Où regarder

- L'exemple vivant : la mémoire de ce dépôt, [memoire/](../), en particulier
  [memoire/canonique.md](../canonique.md) et [memoire/backlog.md](../backlog.md),
  et cette demande elle-même.
- La spécification complète du format : [moteur/socle/FORMAT.md](../../moteur/socle/FORMAT.md).
- La fiche de décision : [ADR-0003](../decisions/ADR-0003-arborescence-et-format-de-la-memoire.md).

Ce qu'il faut vérifier : les noms (`.socle/` caché, `memoire/` visible et en
français), la syntaxe d'une entrée, et le choix d'un fichier par demande au
lieu d'un `PENDING.md`.

## Options

- **Accepter** : effort nul ; risque faible, ce format sert déjà à toute la
  mémoire de ce dépôt et passe tous les contrôles ; réversible par migration
  après la première installation.
- **Amender** : tu dis quoi changer (un nom, le séparateur, la forme des
  identifiants, un `PENDING.md` unique) ; effort d'une session ; risque nul ;
  réversible.
- **Refuser** : tu décris ce que tu voudrais à la place ; effort de deux
  sessions ; réversible.

## Conséquences

Si tu valides, la décision passe à « acceptée » et l'installation sur chess
peut commencer. Si tu amendes ou refuses, je réécris le moteur et la mémoire
de ce dépôt avant toute installation. Sans réponse, rien n'est installé hors
de ce dépôt ; le reste avance.

## Recommandation

Accepter. Vérifié : toute la mémoire de ce dépôt est écrite dans ce format et
passe les contrôles, et l'auto-test installe un projet selon cette
arborescence. Supposé : que tu préfères un `.socle/` caché à un répertoire
visible — c'est un goût, pas une mesure.

## Réponses possibles

- `valider` — arborescence et format acceptés tels quels.
- `amender` — le texte de ta réponse dit quoi changer.
- `refuser` — tu décris ce que tu voudrais à la place.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit.
