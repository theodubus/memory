<!-- socle: couche=demandes zone=publique -->
# D-0108 — Priorités des sujets à finir avant les nouvelles fonctions ; B-0204 et B-0205 sans priorité haute

> date : 2026-11-13 · forme : séance

## Question posée

B-0204 et B-0205, les deux contournements du hook trouvés par B-0171, passent-ils en priorité haute ? Et les priorités proposées pour les sujets à finir avant de revenir aux nouvelles fonctions sont-elles retenues ?

Le contexte, donné à Théo dans la conversation le 13 novembre : à sa demande, la liste des sujets ouverts ces derniers jours (corrections, ajouts importants, ce que ce dépôt a seul et qui devrait entrer dans le produit) qui restent à faire avant de revenir aux nouvelles fonctions, chacun avec une priorité suggérée. Pour B-0204 (une commande après then, do, else ou ! n'est pas jugée par le hook) et B-0205 (un chemin relatif jugé depuis la racine, pas depuis le dossier courant), l'agent proposait « moyenne », c'est-à-dire sans priorité : le hook n'est que la première barrière, et le contrôle protege.fichiers attrape une écriture dans un fichier protégé à la fin du tour, au commit et dans la CI. Les changements proposés : B-0202 (le clone superficiel complété au démarrage), B-0196 (la fin de tour qui refuse l'arbre pendant une mise à jour), B-0151 (les notes de version) et B-0199 (la conduite d'un lot dans le produit) en priorité haute ; le sujet à ouvrir pour le constat 15 de la revue de B-0171 en haute pour la suppression d'un dossier qui contient le projet (rm -rf ..), sans priorité pour les autres commandes non jugées ; B-0172 en basse ; les autres inchangés. L'ordre proposé après le lot en cours : B-0142, B-0202 avec B-0175, B-0196, la mise à jour de chess, B-0151, B-0199, puis le reste par priorité.
