<!-- socle: couche=demandes zone=publique -->
# D-0060 — Valider le rafraîchissement des cinq fichiers protégés de ce dépôt par l'installeur

> date : 2026-10-31

## Décision demandée

Valider les cinq fichiers protégés de ce dépôt que l'installeur, relancé
comme pour une mise à jour, a remis à jour depuis leurs gabarits.

## Contexte

Vous avez demandé de rafraîchir le skill des demandes « si c'est
nécessaire/mieux » (B-0102@1d41aab2). C'est mieux, sans être nécessaire :
aucun contrôle n'en dépend. Les fichiers protégés de ce dépôt, que seul
l'humain modifie, sont en retard sur ce que le socle pose aujourd'hui dans
un projet. Vous n'avez pas de terminal pour `socle approve` : j'ai donc
pris la voie d'une mise à jour en session cloud. L'installeur, relancé sur
ce dépôt, a réécrit les fichiers. Les éléments cités disent ce que change
chacun, avec son empreinte nouvelle ; votre `valider` les fait accepter
par les contrôles.

En chemin, cette voie butait : en attendant votre réponse, le hook de fin
de tour refusait de conclure, et le hook avant push refusait d'envoyer
cette demande. Le pilote y aurait buté à chaque mise à jour. C'est corrigé
sur la branche (B-0115@dd1e5c4c).

## Éléments cités

- `.claude/settings.json` — fichier protégé rafraîchi depuis son gabarit ; empreinte nouvelle `sha256:c5bf42137e4fe404`. Le hook de l'agent voit le widget de questions, et le refuse ici comme dans un projet ; le délai du démarrage passe de 30 à 300 secondes, celui que le gabarit donne pour installer les outils en session cloud (ADR-0035@e59d1c4c). Il ne prend effet qu'à la session suivante de ce dépôt.
- `.claude/skills/socle-request/SKILL.md` — fichier protégé rafraîchi depuis son gabarit ; empreinte nouvelle `sha256:09f8209b23e0ade8`. Le skill des demandes ne parle plus de BMAD, et dit les réponses de base et le refus du widget.
- `.github/workflows/socle.yml` — fichier protégé rafraîchi depuis son gabarit ; empreinte nouvelle `sha256:d760b42e3b2274e8`. La CI du socle reçoit le droit de lire les exécutions de GitHub Actions et son jeton, que lit le contrôle du balayage de mutation planifié.
- `.socle/engine.lock` — fichier protégé rafraîchi depuis son gabarit ; empreinte nouvelle `sha256:a3f642eaeff0cbf5`. Le verrou note le format 3 de la mémoire, celui que ce dépôt a déjà.
- `.socle/socle` — fichier protégé rafraîchi depuis son gabarit ; empreinte nouvelle `sha256:13987d648705d206`. Le lanceur ne cherche plus l'ancien nom du verrou, `moteur.lock`, qu'aucun projet migré n'a plus.
- B-0102@1d41aab2 — le sujet du backlog : rafraîchir le skill des demandes et le réglage de Claude Code de ce dépôt depuis leurs gabarits.
- B-0115@dd1e5c4c — le défaut trouvé en chemin, corrigé : une mise à jour en session cloud qui attend la validation de l'humain ne pouvait ni finir son tour ni pousser sa demande.
- ADR-0035@e59d1c4c — la décision qui donne au démarrage d'une session cloud le temps d'installer les outils de l'adaptateur.

## Où regarder

Les nouvelles versions sont celles des gabarits, que l'installeur recopie :

- [le gabarit du réglage de Claude Code](https://github.com/theodubus/memory/blob/cd4d9966d758a5af018bb524e9eccb8ca9adccdd/engine/socle/templates/settings.json), à comparer à [la copie actuelle](https://github.com/theodubus/memory/blob/cd4d9966d758a5af018bb524e9eccb8ca9adccdd/.claude/settings.json) : la ligne `matcher` et le `timeout`.
- [le gabarit du skill des demandes](https://github.com/theodubus/memory/blob/cd4d9966d758a5af018bb524e9eccb8ca9adccdd/engine/socle/templates/skills/socle-request/SKILL.md), à comparer à [la copie actuelle](https://github.com/theodubus/memory/blob/cd4d9966d758a5af018bb524e9eccb8ca9adccdd/.claude/skills/socle-request/SKILL.md) : les réponses de base, et la séance sans BMAD.
- [le gabarit de la CI du socle](https://github.com/theodubus/memory/blob/cd4d9966d758a5af018bb524e9eccb8ca9adccdd/engine/socle/templates/socle.yml), à comparer à [la copie actuelle](https://github.com/theodubus/memory/blob/cd4d9966d758a5af018bb524e9eccb8ca9adccdd/.github/workflows/socle.yml) : `actions: read` et `GH_TOKEN`.
- [le gabarit du lanceur](https://github.com/theodubus/memory/blob/cd4d9966d758a5af018bb524e9eccb8ca9adccdd/engine/socle/templates/launcher.py), à comparer à [la copie actuelle](https://github.com/theodubus/memory/blob/cd4d9966d758a5af018bb524e9eccb8ca9adccdd/.socle/socle), et [le verrou](https://github.com/theodubus/memory/blob/cd4d9966d758a5af018bb524e9eccb8ca9adccdd/.socle/engine.lock), dont seule la ligne `format` change.

## Options

- **Valider** : les cinq fichiers se commitent dans la pull request en cours. Effort : un mot. Risque faible : ce sont les versions que tout projet reçoit déjà. Réversible, en relançant l'installeur d'une version antérieure.
- **Refuser** : je remets les cinq fichiers tels qu'ils sont sur la branche par défaut ; ce dépôt garde ses copies en retard, et B-0102 reste ouvert. Effort : nul. Réversible.

## Conséquences

- Si vous validez : je consigne votre réponse, je commite les cinq fichiers avec elle, et B-0102 est fait ; le réglage prend effet à la prochaine session de ce dépôt.
- Si vous refusez : je retire les changements de l'arbre ; rien ne part.
- Sans réponse : les fichiers restent changés dans l'arbre, hors de la pull request, qui peut se fusionner sans eux.

## Recommandation

Valider : ce dépôt, premier utilisateur du socle, devrait avoir ce qu'il pose dans les projets, et son agent lit encore BMAD dans ce skill.

Vérifié : les contrôles nomment ces cinq fichiers et ces empreintes, et rien d'autre ; la suite des tests passe avec eux dans l'arbre.

Supposé : que 300 secondes au démarrage ne gênent pas ici ; ce n'est qu'un plafond, et le démarrage de ce dépôt n'installe rien.

## Réponses possibles

- `valider` — les cinq fichiers se commitent, et B-0102 est fait.
- `refuser` — les changements sont retirés de l'arbre, et B-0102 reste ouvert.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
