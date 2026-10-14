<!-- socle: couche=decisions zone=publique -->
# ADR-0019 — Une entrée basculée en privé garde son identifiant en public

> statut : acceptée · date : 2026-10-11 · source : J-2026-10-11-O@9cd059f6 · lu : decisions@6d1e0f62

## Contexte

Théo veut pouvoir rendre privé tout ce qui touche aux décisions et à la
stratégie, y compris ce qui est déjà écrit en public (B-0029@46e602ca). Une
entrée publique est citée ailleurs, souvent par des entrées gelées (journal,
décisions, demandes répondues) que l'ajout seul interdit de réécrire. La
déplacer sous un identifiant privé casserait ces renvois, ou obligerait à
publier la correspondance entre l'ancien identifiant et le nouveau, qui est
une fuite. La supprimer serait un effacement.

## Décision

Une entrée publique basculée garde son identifiant en public, avec un titre
et un texte fixes (« Entrée basculée dans la mémoire privée ») et la date
de la bascule ; tout le reste part dans une copie privée, sous un
identifiant privé, qui cite `depuis : <identifiant public>`. Les renvois
publics restent valides sans rien réécrire ; la correspondance ne se lit
que dans la zone privée.

L'ajout seul admet cette seule réécriture, et seulement si une copie privée
reprend le titre et le texte : sans elle, c'est un effacement, refusé. Là
où la mémoire privée ne se lit pas, la bascule est signalée, pas jugée.
Une entrée basculée ne change plus. La commande refuse une demande (elle se
lit là où l'humain lit : la retirer et en poser une privée) et une entrée
de journal qui archive des sujets (leurs renvois ne survivraient pas).

Le choix par défaut se fait couche par couche (`[private] layers`), et
entrée par entrée par `--private` ou `--public`, sur consigne de l'humain.

## Conséquences

Un renvoi public vers une entrée basculée mène à une entrée vide de sens :
c'est voulu, le sens est privé. L'existence de l'entrée et sa date restent
publiques. L'historique public garde l'ancien texte : seule une réécriture
de l'historique l'efface, et c'est à l'humain de la faire ; la commande et
les instructions de l'agent le disent.

Pour défaire une bascule : recopier l'entrée privée sous son identifiant
public, ce que l'ajout seul refuse aujourd'hui (une entrée basculée ne
change plus) ; il faudrait une demande validée. Pour défaire la décision :
retirer `_bascule` de `moteur/socle/controles_memoire.py` et la commande
de `moteur/socle/prive.py` ; les tests de `tests/test_bascule.py` diront ce
qui casse.
