<!-- socle: couche=backlog zone=publique -->
# B-0274 — Une vue de la suite d'un coup d'œil : jalons, lots, tâches et besoins, calculée depuis le backlog, dans le terminal, la conversation et la CI

> statut : ouvert · origine : J-2026-11-16-AC · lu : backlog@4164cb9f

Théo, le 16 novembre (J-2026-11-16-AC), mot pour mot : « j'aimerais
(dans l'atelier mais aussi dans le socle) une façon facile (que ça soit
skill ou autre peu importe) d'avoir une vision sur la suite (taches, lots,
besoins, jalons, etc) ». La spécification, proposée en séance et validée
par Théo (D-0127@4d91f8cd : « Ok pour ouvrir le besoin et ses tâches, ok
pour A et B, on oublie C ») :

- **Le contenu**, calculé depuis le backlog comme l'état, rien d'écrit :
  chaque jalon et ses besoins clos sur le total ; les lots dans leur ordre
  d'exécution, déduit de leurs `après` ; dans chaque lot, ses tâches avec
  leur besoin, leur priorité et leur avancement (faite, en cours, prête,
  qui attend une entrée ou une demande, bloquée) ; hors des lots, les
  besoins sans tâche, à fermer, bloqués, et ce qui revient à l'humain
  (`pour : humain`) ; ce qui vient après le jalon ; une alerte quand deux
  lots attendent le même lot sans ordre entre eux.
- **Format A, compact** : une ligne par jalon et par lot, avec son
  avancement, le lot en cours marqué.
- **Format B, détaillé**, en Markdown : le lot en cours et les deux
  suivants tâche par tâche, les autres en une ligne (`--all` pour tout) ;
  lu par lot, ou par besoin (`--by need`), chaque besoin avec ses tâches
  et le lot de chacune. Pas de graphe.
- **La commande** : `socle roadmap`, `--format text|markdown`,
  `--by batch|need`, `--all` (`batch`, et non `lot`, sur la
  décision de Théo en séance, D-0131).
- **Les déclencheurs** : l'humain dans un terminal, dit en une phrase par
  le guide ; l'agent qui colle le format B quand l'humain demande la
  suite, une ligne des instructions du socle ; le format A dans le récap de
  la clôture d'un lot, par le skill `socle-batch` ; le format B dans le
  résumé de chaque exécution de la CI, lisible sur GitHub sans agent
  (le workflow est protégé : une demande à l'humain, ici et à la mise à
  jour d'un projet) ; une ligne de l'état qui renvoie à la commande. Dans
  l'atelier, le skill `delegate-lot` l'appelle à l'annonce et à la
  clôture d'un lot.

## Satisfait quand

- [ ] l'humain voit d'un coup d'œil la suite du projet (jalons, lots, tâches, besoins, et ce qui n'est dans aucun lot), dans un terminal, dans la conversation avec l'agent et sur la page de la CI, sans rien demander d'autre que « la suite »
