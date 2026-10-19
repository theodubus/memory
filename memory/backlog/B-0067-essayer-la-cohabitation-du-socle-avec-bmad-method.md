<!-- socle: couche=backlog zone=publique -->
# B-0067 — Essayer la cohabitation du socle avec BMAD Method, avant les sujets qui la recoupent

> statut : ouvert · origine : J-2026-10-19-E · lu : backlog@46629a4e

Le but de Théo (texte exact au journal) : un produit pratique qui combine
les avantages du socle, actuels et prévus, et ceux de BMAD Method. Ni
fusion des codes ni réimplémentation de BMAD (J-2026-10-19-D) : BMAD
au-dessus pour décider quoi faire, le socle dessous pour contrôler ce qui
est fait.

L'essai : dans un projet jetable du banc, installer BMAD (version stable,
par npm) et le socle, faire tourner un petit cycle de BMAD (planifier,
puis construire une story) sous les hooks du socle, et relever les
frictions :

- deux fichiers d'instructions, et lequel l'agent suit quand ils
  divergent ;
- deux mémoires : les documents de BMAD et celle du socle, et ce qui s'y
  recopie ;
- ce que les hooks et les contrôles du socle refusent dans le travail de
  BMAD, à tort ou à raison ;
- les documents de BMAD à lier au code, et ses stories face au backlog ;
- vérifier ce qui n'est que supposé : que BMAD ne bloque rien de
  lui-même.

À faire avant les sujets qui recoupent BMAD, pour les concevoir pour la
combinaison : B-0009, B-0042, B-0046, B-0054, B-0055, B-0066. Le socle n'y
change rien ; l'essai se défait sans trace.
