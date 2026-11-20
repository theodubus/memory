<!-- socle: couche=decisions zone=publique -->
# ADR-0103 — La fusion de sa pull request par l'agent, une option de la politique : la ligne [irreversible] tools que le gabarit propose en commentaire, la liste du moteur moins la fusion, sans toucher le hook

> statut : acceptée · date : 2026-11-20 · source : B-0200@c3d124f9, D-0092@42266c33, ADR-0098@3081a5ed, B-0279@b0933e72, J-2026-11-20-AE@060820b2 · lu : decisions@fccef362

## Contexte

B-0200@c3d124f9 veut dans le produit ce que ce dépôt a depuis D-0092@42266c33 :
l'agent fusionne lui-même sa pull request, quand l'humain l'a voulu. Ici,
Théo l'a voulu en écrivant dans la politique une ligne `[irreversible]
tools`, la liste des outils externes du moteur moins
`mcp__github__merge_pull_request` ; chess a écrit la même ligne à son
installation (`docs/fabrication/chess/installation-2026-11-12.md`). Le hook
de l'agent lit déjà cette liste : vide, celle du moteur refuse la fusion ;
remplacée, elle seule s'applique.

Une option à part, une clé `[irreversible]` booléenne qui retirerait la
fusion de la liste du moteur, ne figerait pas la liste ; mais elle
changerait le hook, qu'ADR-0098@3081a5ed déclare terminé sans une preuve,
qu'aucune session n'a fournie : rien n'a été refusé à tort, rien n'a été
contourné. J-2026-11-20-AE@060820b2 laissait à ce lot de trancher.

## Décision

1. L'option est la ligne `tools` de `[irreversible]`. Les gabarits de la
   politique, en français et en anglais, la portent en commentaire, la
   liste du moteur moins la fusion, avec ce qu'elle permet ; l'humain
   l'active en la décommentant, la politique n'étant écrite que par lui.
   Sans elle, la liste du moteur refuse la fusion, comme aujourd'hui. Le
   hook ne change pas.
2. Un test fige que la ligne des gabarits est la liste du moteur moins la
   fusion, exactement : un outil ajouté au moteur sans elle le fait
   échouer.
3. Les conditions de la fusion par l'agent, celles de D-0092 : sa propre
   pull request seulement ; la CI verte sur son commit de tête, qu'il
   donne ; la revue du dernier lot faite et ses constats traités ; aucune
   demande en attente sur son contenu. Le guide les dit (« La fusion par
   l'agent », en français et en anglais), le gabarit d'`AGENTS.md` renvoie
   au guide, et le skill `socle-batch` les applique ; il y ajoute la
   vérification de ce que la fusion déclenche (B-0279@b0933e72).

## Conséquences

L'option se lit dans la politique, où l'humain l'a écrite : rien d'autre
ne la dit à l'agent. Une politique qui a activé l'option fige la liste :
un outil que le moteur ajoutera à la sienne n'y sera pas refusé tant que
l'humain ne l'y aura pas recopié ; la note de version qui l'ajoute devra
le dire. Se défait, pour un projet, en retirant la ligne ; pour le
produit, par une décision nouvelle qui, sur une preuve, change le hook.
