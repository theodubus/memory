<!-- socle: couche=backlog zone=publique -->
# B-0272 — L'entrée qu'un sous-agent ouvre cite l'index de son worktree, que le hook avant push refuse quand la branche a été poussée depuis le départ du sous-agent

> statut : ouvert · origine : J-2026-11-16-S · lu : backlog@ff00445d

Vu en livrant le lot B-0264 (J-2026-11-16-S). Le sous-agent de B-0261,
parti de ea73156, a ouvert B-0268 en citant l'index du backlog de son
worktree ; entre-temps, l'orchestrateur avait poussé b786d09 sur la
branche. Le hook avant push juge la plage depuis la branche distante :
l'index cité n'est dans aucune de ses versions, et `memoire.lectures`
refuse le push. La CI, qui juge depuis la branche par défaut, l'aurait
accepté. Il a fallu faire citer à B-0268 l'index relu, dans un commit de
plus. Cela se produit chaque fois qu'un sous-agent ouvre une entrée et
que la branche a été poussée depuis son départ, l'usage normal d'une
session cloud.

La piste : que `memoire.lectures` accepte une version de l'index qu'un
ancêtre commun de la plage et de la branche du sous-agent connaît, ou que
le skill `socle-batch` dise de relire l'index à l'intégration.

## Fait quand

- [ ] l'entrée qu'un sous-agent ouvre s'intègre et se pousse sans être récrite, même quand la branche a été poussée depuis son départ, et un test le montre
