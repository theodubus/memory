<!-- socle: couche=demandes zone=publique -->
# D-0163 — Les deux cas que la règle de la reprise laisse : le tour refusé pendant une attente, le réveil d'un tour interrompu sur un arbre rouge

> date : 2026-11-23

## Décision demandée

Compléter la règle de la reprise après une limite d'usage pour les deux cas qu'elle laisse : garder les réveils pendant une attente dont l'agent connaît l'heure au plus tard (piste 1A), et, au réveil d'un travail que vous avez interrompu, répondre en une ligne sans le finir (piste 2A).

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un moteur en Python qui s'installe dans le dépôt d'un projet de code tenu par un agent d'IA, Claude Code : il garde la mémoire du projet, vérifie ce que l'agent produit, et vous pose en demandes, comme celle-ci, les décisions qui vous reviennent. Ce dépôt s'en sert lui-même ; chess, votre jeu d'échecs, recevra ces changements à sa prochaine mise à jour.

**Le chantier.** Le jalon en cours, un ensemble de besoins, corrige et stabilise le produit avant cette mise à jour ; ce lot, un groupe de tâches relues ensemble, traite la reprise après une limite d'usage. Votre compte Claude a deux limites, sur cinq heures et sur la semaine ; atteinte, l'une arrête net la session de l'agent, la conversation que vous suivez dans l'application Claude. Le 8 novembre, vous avez validé la règle qui la fait repartir seule, et précisé que le projet ne doit pas attendre votre retour, l'application ne relançant que la conversation que vous avez ouverte. La règle vit dans le skill `socle-resume`, une procédure écrite que l'agent charge quand elle sert, que chess recevra aussi.

**La question.** La relecture de ce skill, le 8 novembre, a relevé deux cas que la règle laisse ; le premier s'est produit la nuit suivante, le second n'a pas été relevé depuis. Les couvrir change la règle que vous avez validée : c'est à vous de choisir.

**La règle aujourd'hui.** Un tour est ce que fait l'agent entre un message reçu et sa réponse ; pendant une limite, un tour est refusé : il ne s'exécute pas, et l'application affiche que la limite est atteinte. Au début de chaque tour où il travaille, l'agent programme deux réveils, des messages pour sa propre session qui commencent par « Reprise après limite », chacun cinq minutes après la remise à zéro d'une limite. À la fin du tour, il les retire, pour ne jamais relancer un agent que rien n'a coupé. Un tour coupé par la limite ne finit pas : ses réveils restent, et le relancent à la levée. Au réveil, l'agent lit dans l'historique de la session comment a fini le tour d'avant, et les messages arrivés depuis, même refusés : coupé par la limite, il reprend ; un message de vous prime, il y répond ; sinon, il répond en une ligne.

### Cas 1 : un tour refusé pendant une attente

L'agent finit un tour en attendant un événement qui rouvrira la session de lui-même : un rappel qu'il s'est programmé, la fin d'une commande laissée en arrière-plan, les vérifications que GitHub lance à chaque envoi (la CI), ou votre message. Ses réveils sont retirés. Si la limite est atteinte entre-temps, par une autre session de votre compte par exemple, l'événement ouvre un tour refusé, et rien ne le relance : un message refusé n'attend pas en file.

C'est arrivé la nuit du 8 au 9 novembre, heures de Paris : un tour fini vers 0 h 58 en attendant la CI de la pull request alors ouverte, ses réveils retirés, la fenêtre de cinq heures épuisée ; à 1 h 00 et 1 h 01, les deux avis de la CI ouvrent des tours refusés ; à 1 h 04, votre message, refusé ; remise à zéro à 3 h 40, puis plus rien jusqu'à votre « Reprends » à 7 h 45.

- **1A — garder les réveils pendant une attente à heure bornée.** À la fin d'un tour qui attend un événement dont il connaît l'heure au plus tard (son rappel ; sa commande en arrière-plan, à son délai ; la CI qu'il vient de lancer, à la durée qu'il lui connaît), l'agent garde ses deux réveils, et repousse après cette heure celui qui tomberait avant. Sans limite, le tour de l'événement fait siens les réveils, sans en armer d'autres, et les retire à sa fin : rien ne tire. Refusé, le réveil tire à la levée ; l'agent lit l'événement refusé dans l'historique, et le traite. La nuit du 8 au 9 novembre, il aurait repris à 3 h 45, en répondant à votre message de 1 h 04.
- **1B — garder les réveils pendant toute attente**, même sans heure bornée : une revue sur GitHub, votre message.
- **1C — ne rien changer.** Le récap, le résumé qui termine chaque réponse de l'agent, dit déjà ce qu'une attente attend et jusqu'à quand ; au-delà, vous écrivez « reprends ».

### Cas 2 : le réveil d'un travail que vous avez interrompu, sur un arbre rouge

Interrompu en plein travail, l'agent ne passe pas par sa fin de tour : ses réveils restent. Si vous n'écrivez pas avant la remise à zéro suivante, un réveil tire ; l'agent voit l'interruption, et ne reprend pas. Mais le travail interrompu laisse souvent les contrôles du projet en échec, un « arbre rouge ». Le contrôle de fin de tour, un hook que Claude Code lance quand l'agent veut conclure, refuse alors de conclure et lui dit de corriger d'abord : l'agent est poussé à finir ce que vous aviez arrêté. Depuis le 11 novembre, relancé sur le même échec, les fichiers inchangés, ce contrôle ne bloque plus, et il le dit ; rien ne dit à l'agent de s'en tenir là ici.

- **2A — le skill le dit.** Au réveil qui ne reprend pas, si le contrôle de fin de tour refuse, l'agent répond en une ligne que vous avez interrompu ce travail, sans y toucher ; relancé, le contrôle le laisse conclure.
- **2B — le contrôle de fin de tour ne bloque pas** sur des contrôles en échec un tour ouvert par un réveil.
- **2C — ne rien changer** : l'agent peut finir ce que vous aviez arrêté.

## Éléments cités

- B-0133@73fabdd7 — le besoin qui relève ces deux cas, ouvert par la relecture du skill de la reprise le 8 novembre.
- ADR-0050@da14d54e — la règle de la reprise que vous avez validée le 8 novembre, que cette demande complète.
- D-0080@0e4fe1fd — la demande par laquelle vous avez validé cette règle.
- J-2026-11-08-R@21a0dcd9 — votre consigne : le projet ne doit pas attendre votre retour pour repartir après une limite.
- J-2026-11-09-A@f8094317 — l'entrée du journal qui relève la nuit du 8 au 9 novembre, la coupure jamais reprise.
- J-2026-11-09-G@175a360f — la première coupure reprise par un réveil, le 9 novembre au matin : les avis de la CI et d'un agent auxiliaire, refusés pendant la limite, y finissent sur l'erreur de la limite.
- J-2026-11-11-Q@29ade8a4 — votre précision du 11 novembre : un réveil tiré avant la levée de la limite s'est perdu, sans attendre en file.
- ADR-0061@514e0797 — la décision du 11 novembre : le contrôle de fin de tour ne relance plus un échec inchangé.
- T-0082@5de97847 — la tâche qui écrira dans le skill la règle que vous retiendrez.

## Où regarder

- [Le skill `socle-resume`](https://github.com/theodubus/memory/blob/74c372d1b187cf2c86b294dd833e28150bc1da11/engine/socle/templates/skills/socle-resume/SKILL.md) : ses sections « À la fin de chaque tour » et « Au réveil : vérifier d'abord » sont la règle que les pistes complètent.
- [La nuit du 8 au 9 novembre](https://github.com/theodubus/memory/blob/74c372d1b187cf2c86b294dd833e28150bc1da11/memory/journal/2026-11.md#j-2026-11-09-a--th%C3%A9o-valide-d-0083--la-nuit-montre-une-coupure-jamais-reprise--les-r%C3%A9veils-retir%C3%A9s-en-fin-de-tour-puis-la-relance-par-les-hooks-refus%C3%A9e) : le cas 1 tel qu'il s'est produit.

## Options

Un point est un pour cent d'une limite ; un point de la semaine vaut environ sept de la fenêtre de cinq heures.

| Piste | Couvre | Coût en usage | Effort | Risque |
| --- | --- | --- | --- | --- |
| 1A | le rappel, la commande en arrière-plan, la CI | nul sans limite ; avec une limite, un réveil ordinaire | une dizaine de lignes du skill, sa version anglaise, un test | laisse l'événement sans heure bornée : une revue, votre message |
| 1B | toute attente | un réveil qui tire sans limite relance l'agent pour rien ; après une pause de plus d'une heure, le service relit toute la conversation au prix fort : 7 points de la fenêtre de cinq heures à 100 000 jetons (les unités de texte qu'il compte), 20 à 300 000, la taille d'une session qui mène un lot ; jusqu'à une fois par fenêtre tant que l'attente dure, des jours pour une revue | comme 1A | contredit le principe validé : ne jamais relancer un agent que rien n'a coupé |
| 1C | rien | nul | aucun | une attente coupée reste arrêtée jusqu'à votre retour |
| 2A | le réveil d'un travail interrompu | une relance du contrôle, dans un tour déjà payé | deux lignes du skill, sa version anglaise, un test | tient à ce que l'agent suive le skill ; le contrôle lui dit toujours « corriger » |
| 2B | le même, sans compter sur l'agent | nul | du code dans le contrôle, son test, et un défaut volontaire qui prouve qu'il l'attrape | un message tapé qui commence par « Reprise après limite » rend le contrôle indulgent pour ce tour ; le commit et la CI refusent toujours |
| 2C | rien | nul | aucun | l'agent peut finir le travail que vous aviez arrêté |

Réversibilité : toutes les pistes se défont, le texte d'un skill ou, pour 2B, quelques lignes de code.

## Conséquences

Si vous validez : la tâche T-0082 écrit 1A et 2A dans le skill, en français et en anglais, avec un test, dans ce lot ; une décision nouvelle complète celle du 8 novembre ; chess les reçoit à sa mise à jour. Si vous refusez : rien ne change (1C et 2C), T-0082 s'abandonne en citant votre réponse, et les deux cas restent connus. Sans réponse : T-0082 attend, le reste du lot avance, et le lot ne se clôt pas.

## Recommandation

1A et 2A : chacune couvre le cas courant pour presque rien, sans relancer un agent que rien n'a coupé. 1B paie à chaque longue attente un cas vu une fois en six semaines ; 2B touche le code d'un contrôle pour ce que deux lignes du skill font.

Vérifié : la nuit du 8 au 9 novembre, dans l'historique de la session ; un réveil refusé n'attend pas en file ; le coût d'une relecture après une pause, mesuré ; le contrôle de fin de tour qui ne bloque plus un échec inchangé, testé depuis le 11 novembre.

Supposé : qu'un rappel refusé finisse, comme les avis refusés du 9 novembre au matin, sur l'erreur que le réveil lit comme une coupure ; sinon, le réveil de 1A tire une fois pour rien, l'agent répond en une ligne, et je vous le dis au premier rappel refusé. Et que l'agent applique 2A quand le contrôle lui dit de corriger.

## Réponses possibles

Répondez dans la conversation par l'une de ces valeurs ; une autre combinaison se dit en clair, et je la reposerai en une demande courte.

- `valider` — 1A et 2A, écrites par T-0082 dans ce lot.
- `toute-attente` — 1B et 2A.
- `controle` — 1A et 2B ; T-0082 change aussi le contrôle de fin de tour.
- `attente-seule` — 1A et 2C.
- `interruption-seule` — 1C et 2A.
- `refuser` — rien ne change (1C et 2C) ; T-0082 s'abandonne.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
