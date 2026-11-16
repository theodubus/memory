<!-- socle: couche=backlog zone=publique -->
# B-0267 — Un sujet ouvert rejoint aussitôt le lot qui touche les mêmes fichiers, et former un lot balaie tout le backlog ouvert selon la règle, sans le demander à l'humain

> statut : ouvert · origine : J-2026-11-16-J · priorité : haute · lu : backlog@c0a47b1b

Théo, le 16 novembre (J-2026-11-16-J), quand l'agent lui a soumis des
sujets qui allaient avec des lots : « je t'ai demandé de faire des
suggestions si ça va ensemble selon les regles qu'on s'était fixé (touche
aux mêmes fichiers, etc) alors ça va ensemble » ; « Ça ne devrait même pas
etre séparé si la regle qui fait que plusieurs choses appartiennent à un
lot s'applique ».

Le skill `socle-batch` dit comment former le prochain lot (les prêts du
prochain jalon et de priorité haute d'abord), et le format dit ce qui
réunit des sujets dans un lot (les mêmes fichiers, le même garde-fou ou les
mêmes tests, qu'une seule revue juge ensemble). Rien ne dit qu'un sujet
qu'on ouvre rejoint aussitôt le lot ouvert qui touche ses fichiers, ni
qu'on balaie tout le backlog ouvert en formant un lot : douze sujets sont
restés hors des lots du jalon B-0224 jusqu'au 16 novembre, et l'agent les
a soumis à Théo au lieu de les placer.

La piste : le skill `socle-batch` et son gabarit disent qu'un sujet ouvert
rejoint le lot ouvert dont la règle s'applique à lui, sans demander à
l'humain ; qu'en formant un lot, l'agent balaie tout le backlog ouvert, et
pas seulement le jalon ; et qu'un lot qui ne tient plus en une session se
coupe en deux lots, sur leurs fichiers. Le récap dit les placements, la
priorité restant à l'humain.

## Fait quand

- [ ] le skill `socle-batch` et son gabarit disent qu'un sujet ouvert rejoint aussitôt le lot dont la règle s'applique à lui, qu'un lot se forme en balayant tout le backlog ouvert, et qu'un lot trop grand pour une session se coupe en deux
