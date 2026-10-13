<!-- socle: couche=decisions zone=publique -->
# ADR-0025 — Le backlog, un fichier par sujet (format 3)

> statut : acceptée · date : 2026-10-13 · lu : decisions@6a56482b · validation : D-0017

## Contexte

Le backlog est un seul fichier, comme le veut l'arborescence de la mémoire
(ADR-0003@a701a157). Théo a demandé un fichier par sujet, pour en détailler
un sans buter sur un plafond commun et pour en privatiser un au détail, et
l'a validé (D-0017@22c858f3) : un dossier, son pendant privé, plus
d'archivage des sujets clos au journal, un plafond par sujet, dans la même
migration de format que les noms anglais (B-0045@d35a99b1). Le sujet qui
porte ce travail (B-0047@1585820c) y ajoute qu'une action humaine se donne
avec le lien vers son sujet, où vit son mode d'emploi.

Inventaire fait avant de décider : rien de ce que les noms anglais
renomment n'est versionné dans un projet. Sa configuration et sa mémoire
sont en anglais depuis le format 2, le moteur se remplace en bloc, les
marqueurs de `.socle/trace/` sont locaux, et les commandes gardent leurs
anciens noms le temps d'une version. La migration du format 3 ne porte donc
que le backlog, et les noms anglais n'en demanderont pas d'autre.

## Décision

- Au format 3, le backlog est un dossier de la mémoire : un fichier par
  sujet, nommé comme une décision (`B-NNNN-<titre court>.md`), un titre de
  niveau un `# B-NNNN — titre`, sa ligne de métadonnées, puis un corps
  libre, sous-titres compris. Dans la zone privée, `PB-NNNN-….md` sous le
  même dossier.
- Un sujet clos reste dans son fichier. L'index du backlog et son
  empreinte ne listent, comme avant, que les sujets non clos ; `socle
  archive` ne déplace plus rien au format 3.
- Un plafond par sujet, `"memory/backlog/*.md"` dans `[budgets]`, remplace
  celui du fichier unique. Le budget d'un fichier qui n'existe plus se
  retire sans assouplir le cliquet : il ne couvrait plus rien.
- La bascule d'un sujet en privé copie son fichier sous son identifiant
  privé, et le fichier public garde l'identifiant, comme une décision
  (ADR-0019@4a3cf7fb).
- La migration 2 → 3 est scriptée et idempotente : chaque sujet du fichier
  unique devient son fichier, ses sous-titres remontés d'un niveau, et le
  fichier unique est retiré. Un lien écrit vers l'ancre d'un sujet dans le
  fichier unique (le journal, une demande gelée) reste valide tant que le
  sujet existe. Le format se lit à la forme du backlog, fichier ou
  dossier.
- Une action que seul l'humain peut faire (`pour : humain`) figure dans
  l'état et dans « ce qui revient à l'humain » avec le permalien de son
  sujet.

## Conséquences

La lecture, la création d'un sujet, l'index, les plafonds, la bascule,
l'archivage, les liens et la lecture prouvée changent ; les formats 1 et 2
se lisent toujours, et un projet passe au format 3 à sa mise à jour. Ce
dépôt migre sa propre mémoire ; son verrou, protégé, garde `format = 2`
jusqu'à ce que l'installeur le réécrive, sans conséquence puisque le format
se lit à la forme du backlog. Pour défaire : une migration inverse, qui
recolle les fichiers dans l'ordre de leurs identifiants.
