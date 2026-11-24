<!-- socle: couche=backlog zone=publique -->
# L-0010 — Lot de la session longue et de la reprise : le contexte long sans session neuve à la main, la reprise sans list_events

> statut : en cours · origine : J-2026-11-15-J · après : L-0009, T-0039, T-0079, T-0040, T-0041, T-0080, T-0081, T-0134, T-0162 · lu : backlog@19378efe · ancien : B-0240

Le dernier lot du jalon : une session qui dure sans que l'humain en
ouvre une neuve à la main (B-0156, une conception à trancher d'abord) et
la reprise après une limite qui ne sait ni quand ni pourquoi la session
a été coupée (B-0198), le skill `socle-resume`.

Le 16 novembre, Théo y fait entrer B-0259, la passation programmée, qui précise une piste de B-0156 (J-2026-11-16-I).

Le 16 novembre, selon la règle qui réunit dans un lot les sujets qui touchent les mêmes fichiers ou le même garde-fou, appliquée à tout le backlog ouvert (J-2026-11-16-J) : les hooks git débranchés au redémarrage du conteneur (B-0252), et le tour ouvert pendant une limite jamais relancé (B-0133), la reprise comme B-0198.

Le 18 novembre, T-0049 découpe B-0156, B-0259 et B-0133 (J-2026-11-18-J), chacun en une demande à Théo puis ce qu'elle retient : T-0039 puis T-0079 ; l'essai de T-0041, la spécification de T-0080, puis le mode de T-0081 ; T-0043 puis T-0082.

Le 21 novembre, à la formation des lots qui manquent à JA-0005 (D-0154,
J-2026-11-21-Q), il est coupé en deux, dans son ordre : dix tâches pour
un seuil de neuf (ADR-0101). Restent ici les six premières, la session
longue : le contexte long (T-0039, T-0079), la vérification du réveil
sans list_events (T-0040) et la passation programmée (T-0041, T-0080,
T-0081), que Théo garde à sa place (D-0155). Les hooks git au démarrage
(T-0042), les deux cas de la reprise (T-0043, T-0082) et la remise des
copies protégées (T-0114) passent à L-0023, qui le suit.

Le 23 novembre, L-0023 passant avant sa fin, la remise des copies protégées de `socle-batch` et de `socle-resume` que changent T-0079 et T-0081 revient ici, la dernière : T-0165 (J-2026-11-23-Q, J-2026-11-23-R).

Le 24 novembre, sur D-0168, le tri du backlog ouvert par le but (`docs/fabrication/tri-du-backlog-2026-11-24.md`) : T-0165 s'abandonne avec B-0218 (X4) ; T-0134 et T-0162, qui changent le même gabarit, celui de `socle-batch`, le rejoignent depuis L-0026, fermé.

## Revues

### Passe 1 — 2026-11-23

Commits : a68f5bc0..03830147

- Bloquant : une phrase du skill resserrée pour le budget contredisait la suivante (quel réveil laissé se déplace)
- Ouvre : B-0336, T-0164

### Passe 2 — 2026-11-24

Commits : e5b37d6..4c6edf7

- Bloquant : la garde refusait la passation dès que la session qui part poussait après avoir programmé, comme le 23 novembre
- Bloquant : la pull request ouverte, que la session programmée ne pouvait ni continuer sans l'humain ni fusionner
- Ouvre : rien
