<!-- socle: couche=demandes zone=publique -->
# D-0168 — Fermer les 88 besoins et tâches du backlog que le tri par le but écarte, et garder les 39 qu'il retient, comme le dit docs/fabrication/tri-du-backlog-2026-11-24.md

> date : 2026-11-24 · sujet : docs/fabrication/tri-du-backlog-2026-11-24.md

## Décision demandée

Fermer les 88 besoins et tâches que le tri écarte, chacun avec la raison que donne le document du tri, et garder les 39 entrées qu'il retient (20 besoins, 19 tâches).

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code tenu par un agent d'IA : il garde la mémoire du projet, donne à l'agent le bon contexte au bon moment, vérifie son travail par des tests, et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Chess, votre jeu d'échecs, le reçoit à ses mises à jour.

**Le chantier.** Le jalon en cours, un ensemble de besoins, corrige et stabilise le produit avant la mise à jour de chess. Il ne converge pas : du 14 au 23 novembre, les revues (la relecture de chaque lot par un agent sans contexte, le relecteur, avant sa livraison) ont ouvert 111 entrées du backlog, la liste des besoins (ce qui doit devenir vrai) et des tâches (un commit qui y mène). Ce matin, vous avez fixé le but du socle et les critères qui disent ce qui y entre, et demandé, avant tout abandon, le récap de ce qu'on abandonne, chacun avec sa raison.

**La question.** Le tri est fait : sur 127 besoins et tâches ouverts, 39 entrées passent les critères et 88 non. Rien n'est fermé avant votre réponse.

Le tri applique à chaque entrée les trois tests de vos critères : à quoi elle sert (la mémoire, le contexte, la vérification, votre décision, ou un bug qui casse un projet réel) ; sa preuve (vue en usage réel, demandée par vous, ou d'effet irréversible) ; son coût en proportion. Puis leurs six exclusions, de X1 à X6. Se ferment 39 besoins, avec leurs 49 tâches, abandonnés et non faits :

- 4 parades contre un agent qui chercherait à contourner le socle (X1) ;
- 12 cas imaginés par un relecteur, jamais vus, rattrapés par un autre contrôle ou bénins (X2) ;
- 8 finitions des outils du socle (une sortie, une règle de méthode) sans gêne constatée (X3) ;
- 4 qui ne concernent que ce dépôt, rien de ce qu'un projet reçoit (X4) ;
- 2 mesures de la consommation dont aucune décision ne dépend (X6) ;
- 3 légères gênes que l'agent règle lui-même, selon votre règle de ce matin ;
- 3 qui attendaient un fait qui n'arrive pas ;
- 3 faits ou remplacés.

Une entrée fermée se rouvre si son cas est vu en usage réel, une session ou une CI, comme vos critères le disent.

Sur les 39 besoins fermés, 26 sont du jalon en cours, qui passerait de 39 besoins ouverts à 13, et de 13 lots (des tâches relues ensemble) à 4 : celui-ci (ce tri, le tri des constats de revue, l'auto-test que la CI de chess a vu échouer), la session longue sans session neuve ouverte à la main, ce que le récap et l'état vous disent, et l'adaptateur Kotlin sur Android.

Cinq fermetures vont contre ce que vous aviez dit avant ces critères, à regarder d'abord :

- le push que vous aviez validé et que le hook (le contrôle qui juge chaque commande de l'agent) refuse quand même : vous le gardiez en tête jusqu'à un refus nouveau (le 14 octobre, puis le 21 novembre) ; il n'y en a eu aucun depuis le 22 octobre ;
- un seul balayage de mutation (la mesure de ce que les tests attrapent) sur chess, celui du socle, que vous gardiez en priorité basse (13 novembre) ; celui de chess marche ;
- distinguer deux tests de même nom dans deux classes d'un même fichier, à juger à la mise à jour de chess (21 novembre) : aucun projet n'en a eu besoin ;
- l'agent maître que vous aviez demandé (13 octobre) : le skill des lots, la procédure qui fait confier chaque tâche à un sous-agent puis la faire relire, le fait ; il reste une règle de choix du modèle, que vous fixez (Opus partout) ;
- la proposition 7 à reformuler (10 novembre), séparer le cœur du socle de sa méthode de travail, dont votre description du projet tient lieu.

## Éléments cités

- D-0167@4a24a192 — votre validation de ce matin : la description du projet et les critères de tri.
- D-0165@d8aaca8b — votre règle de ce matin : pas de temps pour un cas limite rare, légère gêne que l'agent gère.
- D-0166@c5faec31 — votre rappel de ce matin du but du socle : la mémoire, le bon contexte, les tests.
- B-0343@c7ded381 — le besoin : le backlog ouvert dépasse le but du socle.
- T-0173@12e8e5b3 — la tâche qui fait ce tri et pose cette demande.
- JA-0005@1a6ff5b2 — le jalon en cours : le produit corrigé et stabilisé avant chess.
- B-0048@b618c863 — l'action externe validée que le hook refuse, gardée en tête.
- B-0172@11208d4c — un seul balayage de mutation sur chess, celui du socle.
- B-0192@8dc2f0c3 — la classe d'un test dans la clé d'un constat toléré.
- B-0055@e4b90869 — l'agent maître qui confie chaque tâche à un sous-agent.
- B-0162@40796a62 — reformuler la proposition 7, séparer le noyau de la méthode.

## Où regarder

- [Le tri, entrée par entrée](https://github.com/theodubus/memory/blob/304bfdb4a6cb9d306b352a6a2d76d7a911ad43b0/docs/fabrication/tri-du-backlog-2026-11-24.md) : « Ce qui reste » et « Ce qui se ferme », une ligne par besoin, ses tâches entre parenthèses, avec sa raison. À vérifier : qu'aucune fermeture n'écarte ce que vous jugez nécessaire, et qu'aucune entrée gardée ne vous semble de trop.
- [Vos critères](https://github.com/theodubus/memory/blob/304bfdb4a6cb9d306b352a6a2d76d7a911ad43b0/docs/fabrication/but-et-tri.md) : les trois tests et les six exclusions (X1 à X6) que cite le tri.

## Options

- **Tout valider** : les 88 se ferment, chacune citant cette demande et sa raison ; les lots et le jalon sont recomposés. Effort : un commit de l'agent, dans ce lot. Risque : une entrée utile fermée. Réversible : une entrée fermée se rouvre d'une commande, et dès que son cas est vu en usage réel.
- **Valider avec des exceptions** : de même, sauf les entrées que vous nommez, gardées ou fermées en plus.
- **Refuser** : rien ne se ferme ; le jalon garde ses 39 besoins et ses 13 lots.

## Conséquences

Si vous validez : les entrées se ferment dans ce lot, avant sa livraison, et la suite du projet (`socle roadmap`) le montre dans le récap. Si vous refusez : rien ne se ferme, T-0173 se clôt sur votre réponse, et le jalon avance lot par lot comme avant. Sans réponse : rien ne se ferme ; le lot continue avec le tri des constats de revue, la revue de cap (un agent neuf qui juge si l'effort va vers le but) et l'auto-test de chess.

## Recommandation

Valider. Le jalon redevient fini : treize besoins, quatre lots, chacun vu en usage réel, demandé par vous ou d'effet irréversible.

Vérifié : chaque entrée ouverte lue en entier, son origine et ses critères ; les comptes, par commande sur le backlog.

Supposé : que les cas imaginés par les relecteurs ne se verront pas en usage réel ; la mise à jour de chess le dira, et un cas vu revient.

## Réponses possibles

- `valider` — les 88 se ferment, les 39 restent, les lots et le jalon sont recomposés, comme le dit le document.
- `refuser` — rien ne se ferme ; T-0173 se clôt sur votre réponse.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.

Pour une exception, répondez `valider` suivi des entrées à traiter autrement, en clair (« valider, mais garder B-0055 ») : votre texte est consigné mot pour mot.
