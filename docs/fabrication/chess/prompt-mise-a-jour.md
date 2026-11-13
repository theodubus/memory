# Le prompt de la mise à jour du socle sur chess

À coller dans une session de chess, qui tourne sur un autre compte et ne lit
pas ce dépôt. Il met à jour le socle installé le 12 novembre
(`docs/fabrication/chess/installation-2026-11-12.md`) vers la version qui
corrige ce que cette installation avait montré, et dit à l'agent de chess ce
qui a été ajouté et corrigé, comme Théo l'a demandé.

````text
Mets à jour le socle de ce dépôt depuis son dépôt public, sans ajouter ce dépôt à la session. Le socle a corrigé ce que ton compte rendu d'installation du 12 novembre avait montré. Lis d'abord ce qui change, puis fais la mise à jour.

## Ce qui a été ajouté ou corrigé depuis ta version

Tes constats, sous les numéros de ton compte rendu :

1. L'adoption ne désarme plus un contrôle entier. Elle ne tolère que les constats présents à l'installation, inscrits un par un dans [adoption.tolerated] des garde-fous, sous une clé « fichier — objet ». Tout constat nouveau de tests.creux ou de memoire.references fait désormais échouer son contrôle.
   - À cette mise à jour, l'installeur inscrit lui-même les constats présents sur la branche par défaut, et le dit. Tu dois y retrouver tes quatre constats anciens, pas un de plus : les deux chemins morts de tools/README.md et les deux assertions de déterminisme. S'il en inscrit d'autres, ou en écarte un comme « né sur la branche », arrête-toi et dis-le-moi.
   - La liste ne peut que se réduire. Corriger un constat puis retirer sa ligne est libre ; en ajouter une demande mon accord.
   - L'état dit, par contrôle, combien de constats restent tolérés ; à zéro, le contrôle peut sortir de warn_only. C'est ton sujet « sortir les deux contrôles de l'adoption ».
   - Renommer un fichier qui porte un constat toléré : le contrôle te demandera de renommer sa clé dans la liste, dans la même pull request. Commite le renommage seul, avant de modifier le fichier, sinon git ne le reconnaît pas.
2. Le skill socle-resume s'applique maintenant dans ta session, qui n'a pas l'outil list_events : les réveils s'arment à leur borne. Relis-le après la mise à jour, et applique-le dès ce tour.
3. La fin de tour lance les étapes rapides aussi quand seuls des fichiers de tests ont changé.
5. L'installeur nomme un langage en sous-dossier même quand l'adaptateur est donné. Chez toi il doit se taire, puisque ui/ est déclaré tiers.
6. L'aide de socle decision, de socle answer et de socle reviewed passe le hook.

Trouvé en chemin : le hook ne se laisse plus cacher une commande du socle derrière une option de python (-W, -X).

Pas encore faits, inutile de les signaler de nouveau : le hook de fin de tour en double (ton point 4), une forme pour consigner mes décisions données sans question (7), l'import de l'ancien carnet et ses identifiants (8). Pour le carnet, d'ici là : une entrée importée garde sa date et prend la première lettre libre de ce jour.

Une règle à connaître, tant que le socle ne l'a pas corrigée : quand je valide une demande qui autorise un changement (une valeur attendue, un fichier protégé), commite ma réponse dans le même push que ce changement, jamais avant. Le contrôle d'avant push ne juge que ce qui part.

## La mise à jour

1. Si le clone est superficiel (git rev-parse --is-shallow-repository répond true), complète son historique : git fetch --unshallow.
2. Clone le socle à jour, après avoir supprimé un /tmp/socle resté d'avant :
   git clone --depth 1 https://github.com/theodubus/socle /tmp/socle
3. Sur une branche de travail neuve depuis main, à la racine du dépôt :
   PYTHONPATH=/tmp/socle python3 -m socle install --target .
   Ne redonne pas l'adaptateur : celui de chess est en place, et il est gardé.
4. Lis ce que dit l'installeur, et vérifie :
   - la liste [adoption.tolerated] : tes quatre constats, sous les deux contrôles ;
   - python3 .socle/socle state : une ligne « adoption » par contrôle, avec son compte ;
   - rien de changé dans ta politique ni dans ton adaptateur.
5. Suis les étapes « Et maintenant » de l'installeur, dans son ordre : la demande qui cite chaque fichier protégé changé avec son empreinte, poussée seule, puis les fichiers commités et poussés, pour que je les lise dans la pull request avant de répondre. Donne-moi son lien, et attends ma réponse.
6. La porte, avant de me demander de fusionner : python3 .socle/socle verify --fast --redo (sans --redo, un arbre déjà vérifié saute ses étapes), python3 .socle/socle ci et tools/verify.sh --rapide passent. Donne-moi les durées.
7. Ouvre la pull request, et dis-moi ce qui me revient.

Rends-moi compte, court : ce que l'installeur a dit de l'adoption, mot pour mot ; la liste inscrite ; les fichiers protégés changés ; tout ce qui t'a gêné.
````
