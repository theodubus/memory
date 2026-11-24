<!-- socle: couche=decisions zone=publique -->
# ADR-0107 — La reprise garde ses réveils pendant une attente à heure bornée, et le réveil d'un travail interrompu répond en une ligne sans le finir

> statut : acceptée · date : 2026-11-23 · validation : D-0163 · source : ADR-0050@da14d54e, B-0133@8d235f96, D-0163@01b2736f, J-2026-11-09-A@f8094317, ADR-0061@514e0797, J-2026-11-23-S@d05f0dfb · lu : decisions@2f9746c5

## Contexte

La règle de la reprise (ADR-0050) retire les deux réveils à la fin de
chaque tour qui ne finit pas sur une limite. Elle laisse deux cas
(B-0133). Un tour qui finit en attendant un événement qui rouvrira la
session (un rappel de l'agent, une commande en arrière-plan, la CI) n'a
plus de réveil : si une limite refuse le tour de l'événement, rien ne le
relance, comme la nuit du 8 au 9 novembre (J-2026-11-09-A). Et le réveil
d'un tour que l'humain a interrompu sur des contrôles en échec voit le
contrôle de fin de tour refuser de conclure, et pousser l'agent à finir
ce que l'humain avait arrêté, alors qu'une relance sur le même échec ne
bloque plus (ADR-0061). D-0163 a soumis à Théo trois pistes pour chacun,
avec leur coût ; il a retenu 1A et 2A (J-2026-11-23-S).

## Décision

1. *Attente à heure bornée (1A).* Un tour qui finit en attendant un
   événement dont l'agent connaît l'heure au plus tard (son rappel ; sa
   commande en arrière-plan, à son délai ; la CI qu'il vient de lancer, à
   la durée qu'il lui connaît) garde ses deux réveils, chacun repoussé
   après cette heure s'il tombait avant. Le tour de l'événement les fait
   siens et les retire à sa fin ; refusé par une limite, le réveil le
   relance à la levée, et l'agent traite l'événement refusé. Une attente
   sans heure bornée (la revue d'un humain, son message) ne garde rien.
2. *Réveil d'un travail interrompu (2A).* Au réveil d'un travail que
   l'humain a interrompu, si le contrôle de fin de tour refuse de conclure
   sur des contrôles en échec, l'agent le dit en une ligne, sans y toucher
   ni réarmer les réveils ; relancé sur le même échec et le même arbre, le
   contrôle le laisse conclure.

La règle s'écrit dans le skill `socle-resume`, en français et en
anglais. Le reste d'ADR-0050 tient.

## Conséquences

Une limite qui refuse l'événement attendu ne laisse plus la session en
panne jusqu'au retour de l'humain, sans réveil qui tire pour rien quand
rien n'est refusé. L'événement sans heure bornée reste non couvert,
choisi. Gardés après un tour fini, les réveils peuvent tirer après un
tour refusé que l'humain a ouvert : ses messages se lisent donc depuis le
dernier travail de l'agent, celui qui a provoqué le refus compris ; et
le réveil qui a tiré, éteint, ne se déplace pas : il manque, et le début
du tour en arme un, comme la relecture du lot l'a relevé.
Supposé : qu'un rappel refusé finisse sur l'erreur de la limite
que le réveil lit comme une coupure, comme les avis refusés du 9
novembre ; sinon, le réveil tire une fois pour rien, et l'agent le dit
au premier rappel refusé. Se défait par une décision nouvelle de Théo :
le texte du skill seul change.
