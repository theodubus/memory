<!-- socle: couche=demandes zone=publique -->
# D-0130 — Changer la commande de tests de l'adaptateur pour le lanceur parallèle, et valider la spécification de la durée des étapes rapides et de son seuil (lot L-0012)

> date : 2026-11-17

## Décision demandée

Deux points, à valider ensemble ou séparément : changer vous-même deux
lignes de fichiers protégés, pour que les tests du dépôt tournent sur tous
les cœurs sans que l'agent puisse changer seul la façon de les lancer ; et
valider la spécification ci-dessous avant que l'agent n'en écrive le code.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA comme Claude Code : il
garde la mémoire du projet, vérifie ce que l'agent produit, et vous pose en
« demandes », comme celle-ci, les décisions qui vous reviennent. Chess,
votre jeu d'échecs, est le projet pilote qui l'utilise.

**Le chantier.** Avant toute nouvelle fonction, l'agent termine une file
de lots, chacun un groupe de tâches menées puis relues ensemble par un
agent relecteur sans contexte. Ce lot, que vous avez mis en priorité haute
le 16 novembre, raccourcit `verify --fast`, la vérification rapide que le
socle lance à la fin de chaque tour de l'agent et avant chaque push vers
GitHub. Elle prenait 143 secondes le 13 octobre, sur une autre machine ;
près de onze minutes aujourd'hui, sans que rien ne l'ait signalé. La
cause n'est pas mesurée (plus de tests, une machine plus lente) : le
premier remède rend la vérification moins longue, le second fera voir la
prochaine dérive. Chaque lot en paie le prix : chaque push attend autant,
et un sous-agent (un agent que l'agent principal lance) qui attend plus de cinq minutes perd le cache de sa conversation et la
relit entière, ce qui consomme davantage de la limite d'usage.

**La question.** Les deux remèdes vous reviennent. Le premier lance les
tests sur tous les cœurs ; sa commande est dans l'adaptateur du dépôt
(`.socle/adapter.toml`, le fichier qui dit au socle comment compiler et
tester le code), un fichier protégé : le socle refuse tout changement que
vous n'avez pas approuvé. Le second fait dire au socle la durée de chaque
étape, et avertir au-delà d'un seuil : sa conception n'est pas tranchée.

**Ce qui est mesuré.** Dans le conteneur d'une session du 17 novembre (4
cœurs) : `verify --fast --redo` (tout relancé) prend 650,9 s ; les tests
seuls, lancés l'un après l'autre, 648,7 s. Un lanceur écrit pour ce lot,
`tests/parallele.py`, lance chaque fichier de tests dans son propre
processus, autant à la fois que la machine a de cœurs : 176, 175 et 174 s
de temps écoulé, trois fois de suite, les mêmes 1 172 tests verts. Après
le changement, `verify --fast` devrait prendre environ 180 s : c'est
déduit, pas encore mesuré.

**Le premier point : deux lignes protégées.** Le lanceur échoue si un
fichier de tests échoue, ne s'importe pas ou n'a aucun test ; il lance
aujourd'hui les mêmes 54 fichiers que la commande actuelle, ce que le
relecteur a vérifié ; neuf tests le couvrent. Comme la commande actuelle,
il n'a pas de délai par fichier : un test bloqué bloque tout.

1. Dans `.socle/adapter.toml`, section `[capabilities.tests]`, la ligne
   `command = "python3 -m unittest discover -s tests -t . -q"` devient
   `command = "python3 tests/parallele.py"`.
2. Dans `.socle/policy.toml`, la liste `paths` de la section `[protected]`
   (les fichiers que vous seul modifiez) reçoit la ligne
   `"tests/parallele.py",`, indentée de deux espaces, juste après celle de
   `".socle/adapter.toml",`. Sans elle, la commande protégée confierait
   les tests, et la CI (les contrôles que GitHub lance à chaque push), à
   un fichier que l'agent peut changer seul ; avec elle, tout changement
   du lanceur passe par vous, ceux que le backlog prévoit compris.

Le geste, si vous validez : sur GitHub, sur la branche de travail de cette
session, `claude/socle-l0012-passation-xw9g3i`, éditer les deux fichiers
et commiter, avec le message que vous voulez ; puis répondre dans la
conversation, avant ou après. Les empreintes citées plus bas identifient
le contenu exact des fichiers ainsi changés, et du lanceur qui devient
protégé : votre réponse, que l'agent consigne, approuve ce contenu-là, et
la CI refuse tout autre. Si l'éditeur changeait autre chose, l'agent vous
le dirait. L'agent ne touche pas à ces fichiers : votre commit n'entre en
conflit avec rien.

**Le second point : la spécification de la durée des étapes.** Une étape
est une commande de l'adaptateur (compiler, tester…) ; `verify --fast`
lance celles marquées rapides, `verify` toutes.

1. Chaque vérification qui lance une étape (`verify`, `verify --fast`, la
   CI) imprime sa durée, en secondes écoulées, au bout de sa ligne, puis
   le total des étapes lancées.
2. Un seuil, la clé `[verify] fast_max_seconds` des garde-fous du projet
   (`.socle/guardrails.toml`, le fichier de ses limites), porte sur le
   total des étapes rapides. Le gabarit d'un projet neuf le pose à 300 s,
   la valeur aussi d'un projet qui ne l'écrit pas : au-delà de cinq
   minutes d'attente, un sous-agent perd son cache. Ce délai tient aux
   agents : d'où une clé que chaque projet règle.
3. `verify --fast` ne relance pas des étapes rapides déjà passées sur
   exactement le même contenu : la fin de tour et le push, qui suivent
   d'ordinaire une vérification de l'agent, ne relancent rien. Quand il
   les lance toutes, il garde leur total et la plus longue, avec la trace
   de ce passage (un fichier local). Au-delà du seuil, un
   avertissement, jamais un échec, donne le total, le seuil et l'étape la
   plus longue avec sa durée : à la fin de ce passage ; à chaque
   vérification qui ne relance pas les étapes, sur la ligne qui le dit ;
   et dans l'état du projet (`socle state`), que le démarrage de chaque
   session donne à l'agent, tant que le dernier passage complet dépasse
   le seuil.
4. Relever le seuil l'assouplit : comme pour les autres limites des
   garde-fous, cela exige une demande que vous validez, et le contrôle qui
   juge ces changements connaît la clé ; le baisser est libre. La durée
   ne se compare pas d'une fois à l'autre : elle dépend de la machine.
5. En CI, les durées s'impriment, sans seuil : la CI lance toutes les
   étapes, sur une autre machine.
6. L'auto-test du socle, qui injecte chaque défaut connu et vérifie que
   son contrôle l'attrape, en reçoit deux (une étape lente sous un seuil
   d'une seconde ; le seuil relevé sans demande) et leurs cas sains. Le
   guide d'utilisation et une note de version le disent aux projets qui le
   reçoivent à leur mise à jour, chess compris, dont la durée n'est pas
   mesurée.

Écartés : un échec plutôt qu'un avertissement (la durée dépend de la
machine : un échec bloquerait sans que l'agent puisse corriger) ; un seuil
par étape (une dérive répartie sur plusieurs y échapperait) ; les durées
sans seuil (personne ne les lit : c'est le constat de départ).

## Éléments cités

- L-0012@0ed64bf9 — le lot présent et l'historique de ses revues.
- B-0257@4a64e0f3 — le besoin de lancer la suite de tests sur plusieurs cœurs, avec les premières mesures, du 15 novembre.
- T-0044@8d037e37 — sa tâche : la durée relevée avant et après, la suite parallèle verte trois fois de suite en local et en CI, moins de cinq minutes.
- B-0258@8aa6945c — le besoin que la durée des étapes se dise et ait un seuil, avec le modèle de menace du seuil : ce qu'il arrête, ce qu'il laisse passer.
- T-0045@2be8b0ed — sa tâche : la durée de chaque étape imprimée, et l'avertissement d'un seuil dépassé.
- B-0281@cfb15e80 — les suites du lanceur que la revue a relevées : sa comparaison figée avec la commande actuelle, un délai par fichier.
- J-2026-11-17-I@47fe7455 — l'entrée du journal qui consigne le lanceur et ses mesures.
- ADR-0001@692e0dfc — la décision d'architecture qui borne le socle à la bibliothèque standard de Python, que le lanceur respecte.
- tests/parallele.py sha256:1c953e00a189257a — le lanceur, au contenu que votre réponse approuve en le protégeant.
- .socle/adapter.toml sha256:5dffd22cd3ada2b2
- .socle/policy.toml sha256:6ac747029a7e63ce

Le suffixe après `@` est l'empreinte de la version lue.

## Où regarder

- [tests/parallele.py](https://github.com/theodubus/memory/blob/d4e4f56d2f61b29d091805df420922349dee26e9/tests/parallele.py) : le lanceur, 137 lignes ; vérifier qu'il ne fait que lancer chaque fichier de tests et en rendre le bilan.
- [Le journal, sixième fichier de novembre](https://github.com/theodubus/memory/blob/d4e4f56d2f61b29d091805df420922349dee26e9/memory/journal/2026-11-6.md) : l'entrée J-2026-11-17-I, les mesures et la nature de chacune, mesurée ou déduite.
- [B-0258](https://github.com/theodubus/memory/blob/d4e4f56d2f61b29d091805df420922349dee26e9/memory/backlog/B-0258-la-duree-des-etapes-rapides-se-dit-et-a-un-seuil-v.md) : le besoin du second point et son modèle de menace.

## Options

- **Les deux points.** Effort : deux lignes pour vous, puis une
  demi-journée de lot. Risque : faible ; le lanceur est testé
  et relu, le seuil ne fait qu'avertir. Pas encore éprouvée : la
  vérification complète, `verify`, où l'auto-test du socle tournera en
  même temps que d'autres fichiers de tests ; l'agent la relève après le
  changement. Réversible : les lignes se remettent, le seuil se règle.
- **Le premier sans protéger le lanceur.** Effort : une ligne. Risque :
  l'agent peut changer seul la façon dont les tests et la CI se lancent ;
  seule la relecture de chaque lot le verrait. Réversible : la ligne de la
  politique s'ajoute plus tard.
- **Le premier seul.** Effort : deux lignes. Risque : la durée reste
  muette, une nouvelle dérive ne se verrait pas. Réversible : la
  spécification se reprend selon votre remarque.
- **Le second seul.** Effort : le lot de l'agent seul. Risque : la
  vérification reste à onze minutes, et l'avertissement le dira à chaque
  session. Réversible : les lignes peuvent changer plus tard.
- **Aucun.** Effort : nul. Risque : chaque lot continue de payer onze
  minutes par vérification. Réversible : les deux tâches restent ouvertes.

## Conséquences

- Si vous validez : après votre commit, l'agent relève la durée de
  `verify --fast --redo` et celle de `verify`, attend trois CI vertes de
  suite (contre un test que le parallélisme rendrait instable), puis
  implémente la spécification, la fait relire et livre le lot.
- Si vous refusez : l'adaptateur garde sa commande ; l'agent reprend les
  deux tâches selon votre remarque.
- Sans réponse : le lot attend ; l'agent avance sur les lots suivants, et
  la vérification reste à onze minutes.

## Recommandation

Valider les deux points. Vérifié : les durées ci-dessus, mesurées une fois
pour la suite séquentielle et trois fois pour la suite parallèle, tous les
tests verts à chaque fois ; les neuf tests du lanceur ; les mêmes 54
fichiers des deux façons ; les empreintes des trois fichiers. Supposé : la
durée d'environ 180 s, déduite de deux relevés ; le gain en CI, que la
machine de GitHub fixera ; qu'un seuil de 300 s convienne aux autres
projets, sans mesure faite chez eux.

## Réponses possibles

- `valider` — vous changez les deux lignes, et la spécification est validée telle quelle.
- `sans-protection` — vous changez la seule ligne de l'adaptateur, sans protéger le lanceur ; la spécification est validée.
- `adaptateur-seul` — vous changez les deux lignes ; la spécification revient à l'agent avec votre remarque.
- `specification-seule` — l'adaptateur garde sa commande ; la spécification est validée.
- `refuser` — ni l'un ni l'autre ; l'agent reprend les deux tâches selon votre remarque.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
