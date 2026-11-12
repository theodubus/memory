# Installation du socle sur chess, 12 novembre 2026 : faite, et ce qu'elle a montré

Le compte rendu de l'agent de la session de chess, recopié par Théo dans la
session du socle, tel quel, au numéro de version près. La session a repris à
l'étape 4 du premier prompt de `docs/fabrication/chess/prompt-installation.md`,
après l'arrêt du 11 novembre (`docs/fabrication/chess/installation-2026-11-11.md`).

```text
## Installation réelle du socle sur chess : faite, et ce qu'elle a montré

Résultat. Installé avec l'adaptateur propre à chess donné en fichier, fusionné sur main le 12 novembre (pull request 288), CI du socle exigée avant fusion. Théo a écrit lui-même les deux lignes de politique ([irreversible] tools sans la fusion, keep_branches) ; éprouvées, elles font ce qu'il faut.

La porte avant le push, sur le conteneur de la session : verify --fast 140 s, ci 262 s (dix-huit étapes, auto-test 142 cas sur 142), tools/verify.sh --rapide de chess 120 s. Sur GitHub, le job « Socle » prend de 5 à 9 minutes. L'audit d'initialisation pose bien les workflows en un seul fait, et le budget de CLAUDE.md a sa marge d'un dixième.

### À corriger ou à trancher côté socle, par ordre d'importance

1. Le mode adoption désarme le contrôle entier. Dans context.py, un contrôle nommé dans [adoption] warn_only voit toutes ses erreurs passer en avertissement, les nouvelles comme celles d'avant l'installation. Sur chess, tests.creux et memoire.references n'arrêtent donc plus rien tant que quatre constats anciens ne sont pas résorbés : une référence inventée demain passerait. Ni l'installeur ni l'état ne le disent en ces termes. Pistes : ne rétrograder que les constats présents à l'installation, ou faire dire à l'état « N contrôles désarmés par l'adoption ».

2. Le skill socle-resume ne s'applique jamais dans cette session cloud. Il exige l'outil list_events, que la session n'offre pas ; elle a send_later, update_trigger, delete_trigger, list_triggers et get_session. Conséquence : après une limite d'usage, l'agent ne reprend pas seul. Piste : sans cet outil, armer à la borne que le skill prévoit déjà (maintenant plus cinq heures et cinq minutes, plus sept jours et cinq minutes).

3. La fin de tour ne lance les étapes rapides que si un fichier des sources a changé (hooks.stop, par chemins_code). Les tests d'intégration n'en sont pas, ni dans l'adaptateur de chess ni dans le Rust maintenu (**/src/**). Un changement des seuls tests/*.rs n'est donc vérifié qu'au push et en CI. Voulu ?

4. L'installeur signale un état de démarrage en double, pas un hook de fin de tour en double. Chess avait le sien, qui lance les mêmes douze étapes : mesuré, 123 s pour lui et 122 s pour celui du socle à chaque fin de tour où un .rs attend son commit. Le hook du socle, relancé sur le même arbre, ne prend que 3 s.

5. L'installeur ne dit rien du JavaScript d'un sous-dossier quand l'adaptateur est donné en fichier (déjà noté chez vous).

6. Le hook de l'agent refuse socle decision --help et socle answer --help : pour connaître leurs arguments, il a fallu lire cli.py.

7. Consigner des décisions que l'humain donne de lui-même : socle decision exige une réponse de base. J'ai consigné les six décisions de Théo sous valider, avec une « question posée » qui dit qu'aucune question ne les a précédées. Une forme « consigne » serait plus juste.

8. Les identifiants du journal ont la forme de ceux du carnet d'avant le socle (J-AAAA-MM-JJ-L). Ses anciennes entrées ne peuvent pas être citées avant leur migration (le contrôle des références les dit inexistantes), et la migration se heurtera aux jours où les deux existent.

9. Le harnais de la session cloud a son propre hook de fin de tour, qui demande de commiter et pousser tout changement non commité. Il contredit « ne pousse rien avant la porte ». Le prompt d'installation devrait dire : commiter en local dès l'installeur passé, pousser après la porte.

### Ce qui reste côté chess, posé au backlog

Sortir les deux contrôles de l'adoption ; poser la feuille de route dans la mémoire avec Théo ; déplacer le carnet de bord vers la mémoire ; trancher les deux hooks de fin de tour.
```
