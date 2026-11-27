<!-- socle: couche=decisions zone=publique -->
# ADR-0117 — La clôture d'une entrée du backlog en un geste : socle close pose son statut, sa référence et son rangement ; « ce commit » désigne le commit qui la clôt

> statut : acceptée · date : 2026-11-27 · lu : decisions@3ff9f33c

## Contexte

Chez chess, clore une tâche de deux lignes demande environ huit gestes de
mémoire (B-0375@5dc4ed0a) : une entrée close exige une `ref`, et le commit
qui fait le travail n'existe pas encore quand la tâche se clôt, si bien
que seule une entrée de journal écrite pour l'occasion peut servir ; puis
le contrôle du backlog refuse l'entrée close tant que `socle archive` ne
l'a pas rangée (ADR-0030@946c5ba6). Théo a retenu, le 27 novembre
(D-0235@2eec26f8, point 5), une commande qui pose le statut, la référence et le
rangement, l'agent cochant toujours ses critères lui-même, et une
référence qui désigne le commit qui clôt, la forme spécifiée avant le
code (T-0214@ffe13d7e).

## Décision

- **La référence du commit qui clôt.** Dans le champ `ref` d'une entrée
  du backlog, la valeur `ce commit` (en anglais `this commit`), seule ou
  parmi d'autres références séparées par une virgule, désigne le commit
  qui l'a écrite sur la ligne de métadonnées de l'entrée : celui qui la
  clôt, que l'historique du fichier retrouve, à travers son rangement
  (`git log --follow`). Le contrôle du backlog l'accepte comme la
  référence d'une entrée close. Avant ce commit, elle désigne le commit à
  venir. `socle show` la résout, après le texte de l'entrée : le SHA
  court et le titre du commit, ou « pas encore commité ».
- **La commande.** `socle close <ID> [--ref <référence>]` clôt « fait »
  une entrée ouverte du backlog, de toute forme. Elle pose le statut
  `fait`, ajoute la référence au champ `ref`, après celles qu'il porte
  déjà (`ce commit` par défaut, dans la langue du projet ; `--ref` en
  donne une autre : une entrée du journal, une demande, `commit:<sha>`),
  puis range l'entrée parmi les closes et met son déplacement dans
  l'index, comme `socle archive`. Elle ne coche rien : cocher un critère
  reste le geste de l'agent qui l'atteste.
- **Ce qu'elle refuse.** Un identifiant inconnu, une entrée hors du
  backlog, déjà close ou basculée en privé (sa copie privée se clôt) ; et
  toute entrée que les contrôles du backlog refuseraient close
  (`memoire.backlog`, `memoire.formes`, `memoire.ordre`) : un critère de sa
  section non coché, un besoin dont une tâche reste ouverte, une entrée
  dont ce qu'elle attend reste ouvert. Pour ces derniers, la commande
  écrit la clôture, fait juger l'entrée par ces contrôles mêmes, et, à la
  moindre erreur sur son fichier, remet le fichier comme avant et donne
  leurs messages : une seule règle, celle des contrôles, sans copie dans
  la commande.
- **Abandonner** reste un geste à la main, avec la raison en référence :
  un abandon n'est pas le commit d'un travail.

## Modèle de menace

Ce que la règle doit arrêter : une entrée close sans rien qui dise ce
qui l'a close, et une entrée close « fait » qu'un critère vide dément.

- `ce commit` sur une entrée close par un commit qui ne porte que la
  mémoire désigne un commit sans travail. La référence n'en est ni plus
  ni moins faible qu'une entrée de journal écrite pour l'occasion, ce
  qu'elle était déjà : ce qui prouve une tâche faite, ce sont ses
  critères cochés et ce qu'ils nomment, que d'autres contrôles jugent
  (un correctif sans test, une fonction sans test). Accepté.
- `ce commit` ajouté après coup à une entrée déjà close désigne le commit
  de l'ajout, non celui de la clôture. Une entrée close sans référence ne
  passe aucun commit : l'ajout remplacerait une référence existante, sans
  rien changer à ce qui est fait. Rare et sans effet ; non contrôlé
  (C-0005@ef96e253).
- La commande ne coche rien et se range derrière les contrôles : elle ne
  clôt rien qu'un commit n'accepterait pas, et le commit rejuge tout.
- La valeur de `--ref` passe par le contrôle des références au commit,
  comme toute autre.

## Conséquences

Clore une tâche cochée tient en un geste, `socle close T-NNNN`, puis le
commit qui porte le travail ; l'entrée de journal n'est plus exigée pour
servir de référence, et le rangement ne se refuse plus après coup.
ADR-0030 reste : `socle archive` range toujours ce qu'un geste à la main
a clos ou rouvert. Une citation de l'entrée close survit, sa ligne de
métadonnées seule changeant (ADR-0053@5b55c0fa). Pour défaire : retirer la
commande et la valeur ; une entrée qui porte `ce commit` garde son sens,
que l'historique de son fichier donne.
