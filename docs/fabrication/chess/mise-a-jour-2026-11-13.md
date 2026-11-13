# Mise à jour du socle sur chess, 12 et 13 novembre 2026 : faite, et ce qu'elle a montré

Le compte rendu de l'agent de la session de chess, recopié par Théo dans la
session du socle, tel quel. La session a suivi le prompt de
`docs/fabrication/chess/prompt-mise-a-jour.md`, avec la version publiée du
socle d'avant le lot de B-0173.

```text
Compte rendu de la mise à jour du socle sur chess, 12-13 nov. 2026.

Fait. Installeur lancé depuis d3f516d sur une branche repartie de main, sans redonner l'adaptateur. 26 fichiers protégés changés : 24 du moteur, engine.lock, le skill socle-resume. Le moteur installé est identique, fichier par fichier, au dépôt public. Politique, adaptateur, garde-fous et .claude/settings.json inchangés. Aucun langage nommé en sous-dossier. Demande D-0010 posée, relue à froid, poussée seule ; fichiers commités et poussés ensuite ; validée par Théo. La PR sera fusionnée par l'agent à CI verte, règle propre à chess.

Ce que l'installeur a dit de l'adoption, mot pour mot : rien. Aucune ligne. Le lot fusionné juste avant avait déjà corrigé les quatre constats et vidé warn_only.
Lancé à blanc sur le main d'avant cette fusion, il disait :
  - mise à jour : tests.creux était désarmé en entier par l'adoption ; ses 2 constat(s) présent(s) sont consignés comme tolérés (`[adoption.tolerated]`), et tout constat nouveau échouera désormais (B-0180)
  - mise à jour : memoire.references était désarmé en entier par l'adoption ; ses 2 constat(s) présent(s) sont consignés comme tolérés (`[adoption.tolerated]`), et tout constat nouveau échouera désormais (B-0180)
et inscrivait exactement les quatre attendus : les tautologies de engine/src/search.rs et tools/src/bin/spsa.rs, les chemins tools/nnue-train/checkpoints/ et tools/spsa.py. Aucun de plus, aucun écarté. L'état rendait une ligne « adoption » par contrôle.

La porte. Avant la réponse : verify --fast 5 s (étapes non relancées, arbre déjà vérifié), socle ci 279 s (échec attendu sur protege.fichiers seul), verify.sh --rapide 118 s. Après la réponse, avec --redo : 198 s, 277 s, 169 s, tout passe.

Ce qui a gêné :
1. Sur un projet où l'adoption est déjà vidée, l'installeur ne dit rien de l'adoption. Une ligne « aucun contrôle en adoption : rien à inscrire » aurait suffi à vérifier ; il a fallu un essai à blanc sur l'état d'avant.
2. L'ordre du prompt (demande, attendre, porte, PR) et celui de l'installeur (demande poussée seule, puis fichiers poussés et lus dans la PR) divergent. J'ai suivi l'installeur : sans cela, les fichiers attendent hors commit dans un conteneur éphémère, qui a redémarré deux fois cette nuit, et l'humain ne peut pas les lire avant de répondre.
3. Entre l'installation et le push de la demande, la fin de tour refuse l'arbre : 26 lignes en ECHEC, chacune avec sa commande de remise, environ 17 Ko de contexte. Elle pourrait dire en une ligne « pose la demande ». Une fois la demande poussée, ce n'est plus qu'un avertissement.
4. verify --fast saute les étapes sur un arbre déjà vérifié : pour donner des durées, il faut --redo, que le prompt ne dit pas.
5. L'installeur réaffiche à chaque passage le diff de la politique sur deux lignes que l'humain a écrites exprès (tools, keep_branches) : du bruit.
6. Une réponse validée dans la conversation (D-0009) ne se commite qu'avec le changement qu'elle autorise. D'ici là, l'état l'affiche « en attente » à l'humain, qui l'a déjà donnée.
7. La relecture à froid d'une demande : 131 786 jetons, 69 s.
8. socle-resume, sans list_events : armé à la borne, il a repris seul la session à 2 h 46, heure de Paris. L'heure et la cause de la coupure restent illisibles. Coût : 4 à 6 appels par tour qui agit.
```
