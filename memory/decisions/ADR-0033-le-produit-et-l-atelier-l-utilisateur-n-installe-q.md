<!-- socle: couche=decisions zone=publique -->
# ADR-0033 — Le produit et l'atelier : l'utilisateur n'installe que le moteur, le dépôt les sépare d'entrée

> statut : acceptée · date : 2026-10-20 · lu : decisions@71682948

## Contexte

Théo, en répondant à D-0033@43487fd4 (J-2026-10-20-S@5844ec0a, son texte exact) : « Un
projet a juste besoin d'un outil, pas de la backlog ni des arbitrages de
cet outil ». Un projet équipé ne reçoit déjà ni la mémoire, ni les tests,
ni les bancs de ce dépôt : l'installeur ne copie que `engine/socle/` et
pose une mémoire vide. Mais trois choses mêlent encore l'outil et sa
fabrication : pour installer, on clone tout ce dépôt pour n'en copier qu'un
dossier (B-0042@d51e8ba3) ; le moteur copié porte environ 330 renvois à la mémoire
de ce dépôt (B-0077@d7c693cf) ; et le dépôt montre au même niveau le produit et
l'atelier (B-0046@4f8f71dc).

## Décision

Le dépôt a deux parts. **Le produit** : `engine/socle/`, ce qu'un projet
reçoit, et rien d'autre. **L'atelier** : la mémoire de ce dépôt, ses tests,
ses bancs et sa documentation de fabrication ; le socle y est appliqué à
lui-même, comme à un projet, mais sa mémoire est l'historique de
fabrication de l'outil, pas un modèle à copier.

1. L'utilisateur n'installe que le produit : un paquet qui ne contient que
   le moteur, installable en une commande sans clone (B-0042), ou à défaut
   une archive du seul moteur publiée avec chaque version. C'est une
   publication : elle passe par une demande.
2. Le produit ne parle plus de l'atelier : ses commentaires disent le
   pourquoi en clair, sans renvoi à la mémoire de ce dépôt (B-0077).
3. Le dépôt le dit d'entrée : le README et la documentation présentent le
   produit d'un côté et l'atelier de l'autre (B-0046@4f8f71dc).

Un seul dépôt, pas deux : chaque session de développement toucherait les
deux, et une session à deux dépôts reprend sans hooks (J-2026-10-20-T@a4ce3ee0).
Théo l'a validé en séance (D-0034@3a1db7ab).

## Conséquences

La documentation suit cette séparation, et son plan est soumis à Théo
avant d'être écrit. Le retrait des renvois du moteur (B-0077) rend ses
commentaires autonomes ; le pourquoi détaillé reste dans la mémoire de
l'atelier. La publication du paquet attend sa demande. Se défait sans
coût : rien ne bouge encore dans l'arborescence ; seuls des commentaires
et la documentation changent.
