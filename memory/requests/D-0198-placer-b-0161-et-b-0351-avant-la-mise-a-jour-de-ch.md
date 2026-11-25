<!-- socle: couche=demandes zone=publique -->
# D-0198 — Placer B-0161 et B-0351 avant la mise à jour de chess, B-0101 réduit à un lot après elle, JA-0003 après elle, B-0104 clos à elle, B-0158 juste après B-0353, B-0188 écarté ?

> date : 2026-11-25 · forme : séance

## Question posée

Théo demande, le 25 novembre, si B-0161 (la couche des consignes) n'est pas à la limite d'une correction et donc à faire avant chess, le détail de B-0101 (la planification), de JA-0003 (mesurer en usage réel) et des trois besoins hors des jalons, et si B-0351 (l'agent supprime ses branches de travail déjà contenues ailleurs) ne vaut pas mieux avant chess. La réponse de l'agent, dans la conversation, recommande pour chacun :

1. B-0161 : avant chess ; une spécification à valider, puis un à deux lots ; le chantier actif est à 3 693 octets sur 3 700, ses 25 consignes en font 87 %, et un changement du format de la mémoire passe mieux dans la seule mise à jour de chess.
2. B-0101 : après chess, réduit à un lot (un skill court socle-plan, l'emplacement fixe de la spécification et de l'architecture, un scénario du banc).
3. JA-0003 : après chess, tel que décrit ; les refus sont d'abord à porter par chaque commit, la trace locale des hooks se perdant avec le conteneur d'une session cloud.
4. B-0351 : avant chess ; la gêne revient à chaque session, et chess la recevrait corrigée dans sa seule mise à jour.
5. B-0104 : le clore avec le compte rendu de la mise à jour de chess, qui fait le même geste.
6. B-0158 : juste après B-0353 ; l'architecture fait 79,8 Ko.
7. B-0188 : l'écarter tant qu'il n'y a que deux projets équipés.

Réponses : `valider` (les sept recommandations), `refuser`, `contexte-insuffisant`, ou un choix par besoin (`choix-par-besoin`) ; Théo répond besoin par besoin : B-0161 et B-0351 avant chess, B-0101 et JA-0003 comme recommandés, B-0104 plus tard après chess au lieu de le clore, B-0158 et B-0188 plus tard après chess.
