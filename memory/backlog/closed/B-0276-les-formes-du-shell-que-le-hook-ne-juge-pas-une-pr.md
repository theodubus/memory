<!-- socle: couche=backlog zone=publique -->
# B-0276 — Les formes du shell que le hook ne juge pas : une procédure d'atelier, que le produit ne donne plus aux projets (D-0128)

> statut : fait · origine : J-2026-11-17-G · ref : D-0128, ADR-0099, J-2026-11-20-AD · lu : backlog@6141fdaf

Théo, le 17 novembre (J-2026-11-17-G), mot pour mot : « En fait je me
demande, est ce que c'est au rôle du socle de juger le hook ? Ou juste
celui de l'atelier (de l'implementation du socle dans l'atelier) / Car la
on va faire juger a tout le monde le hook alors que c'est pas ce qu'ils
demandent + faire ouvrir potentiellement des issues sur des formes
exotiques qu'on ne traitera pas de toute façon ». Puis, sur les trois
options proposées : « Je valide A » (D-0128).

Le constat : la règle d'ADR-0082 sur les formes du shell qu'un agent
n'écrit pas est née de la revue des lots du hook dans ce dépôt (le lot
B-0234, ses bloquants de formes exotiques). B-0261 l'a mise dans le
produit, et ADR-0085 y a ajouté le signalement au dépôt du socle. Or un
projet équipé ne relit pas le hook, qui est du moteur installé, et une
forme exotique ne se corrige jamais : la procédure fait juger aux projets
un outil qu'ils n'ont pas demandé à juger, et leur ferait signaler ce
qu'on ne traitera pas.

La spécification, l'option A de D-0128 :

- Le produit ne dit plus la procédure ni la liste. Sortent : le
  paragraphe des formes du shell du skill `socle-review` (deux langues),
  la phrase d'ADR-0085 comprise ; sa phrase dans la consigne du relecteur
  de `socle review` ; celle du gabarit d'AGENTS.md ; dans le guide, les
  phrases de procédure (un trou qui ouvre une entrée ou non, la forme qui
  ne bloque pas la revue d'un lot du hook) et la liste des formes
  connues.
- Le guide garde le modèle de menace du hook, comme description de
  l'outil : ce qu'il arrête, ce qu'il juge, ce qu'il refuse de ne pas
  savoir lire, et la limite connue qu'un agent peut écrire
  (`find … | xargs rm` vers le projet).
- L'atelier garde la règle d'ADR-0082 : le skill `delegate-lot`, propre à
  ce dépôt et que l'installeur ne pose pas, la dit pour la revue d'un lot
  du hook ; la liste des formes connues passe dans `docs/fabrication`.
- Une décision remplace ADR-0085 et dit la nouvelle répartition. Le texte
  du guide que Théo avait validé (D-0120) change : les tests qui le
  fixent mot pour mot se nomment dans une demande, validée avant leur
  changement. La copie protégée du skill dans ce dépôt se rafraîchit avec
  les autres du lot L-0006 ; le prompt de mise à jour de chess le dit, et
  une note de version.

## Satisfait quand

- [x] un projet équipé ne reçoit plus de procédure sur les formes du shell que le hook ne juge pas, et l'atelier la garde pour la revue d'un lot du hook
