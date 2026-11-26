<!-- socle: couche=decisions zone=publique -->
# ADR-0114 — L'agent supprime lui-même ses branches distantes déjà contenues ailleurs : la commande prune-branches, après un fetch sans --prune, vérifiée sur l'origine et sous bail (remplace ADR-0113)

> statut : acceptée · date : 2026-11-26 · source : ADR-0113@6915f647, B-0351@bf78a534, D-0202@0eec86fd, ADR-0098@3081a5ed · lu : decisions@bb09b4e3

## Contexte

ADR-0113@6915f647 décidait le mécanisme de B-0351@bf78a534 sur
l'intention que Théo a retenue (D-0202@0eec86fd) : la commande
`socle prune-branches` lançait d'abord `git fetch --prune origin`. La
revue adversariale du lot (J-2026-11-26-G@8c5c65ae) l'a prise en défaut : ce fetch, même en
`--dry-run`, élague la référence locale d'une branche que l'origine n'a
plus, et perd le commit qu'elle seule garde. C'est le cas où l'état dit à
l'humain d'étiqueter d'abord un commit que la mémoire cite ; la commande
l'aurait perdu, contre son modèle de menace (« la perte d'un commit ») et
contre sa promesse de ne rien changer en `--dry-run`. ADR-0113 étant
poussée, elle ne se réécrit pas : celle-ci la remplace, avec la seule
correction du fetch.

## Décision

1. Une commande du socle, `socle prune-branches`, supprime les branches
   que l'état calcule à supprimer et dont le dernier commit porte l'un des
   motifs de `[agents] markers` : après `git fetch origin`, **sans
   `--prune`**, elle demande à l'origine ses branches (`git ls-remote
   --heads origin`) ; une branche qu'elle n'a plus est passée sous silence,
   sa référence locale gardée ; une autre doit y être à la tête que le
   fetch connaît, et la branche qui la garde (la branche par défaut, ou la
   branche de travail courante) doit la contenir sur l'origine. Puis elle
   la supprime par un push gardé par cette tête
   (`--force-with-lease=refs/heads/<b>:<sha>`), qui échoue si elle a
   bougé, et imprime la commande qui la recrée. `--dry-run` dit ce qu'elle
   supprimerait.
2. Un refus de l'origine se garde dans `.git/socle/prune-refused.json`,
   avec la tête refusée : tant qu'un fetch ne montre pas la branche
   changée, l'état la redonne à l'humain, avec la raison, et la commande
   ne la retente pas. Un bail refusé (la branche a bougé) n'est pas un
   refus : la branche est laissée, rien n'est gardé.
3. L'état ne donne plus à l'humain que ses branches et celles que
   l'origine a refusées ; une ligne pour l'agent, hors de ce qui revient à
   l'humain, nomme les siennes et la commande.
4. `prune_branches`, dans `[irreversible]` de la politique, vaut vrai par
   défaut ; toute autre valeur qu'un booléen vrai coupe la suppression :
   l'état redonne alors tout à l'humain, et la commande refuse en le
   disant. Les gabarits de la politique portent la ligne en commentaire.
5. Le hook avant push de git laisse passer, sans rien lancer, un push qui
   ne fait que supprimer. Le hook de l'agent refuse toujours
   `git push --delete` et `git push origin :<branche>` ; seul son message
   change, qui nomme la commande (ADR-0098@3081a5ed, sur la preuve de
   B-0351).

## Conséquences

Comme ADR-0113 : une passation ou une fusion ne laisse plus de branche de
l'agent à l'humain ; une pull request ouverte depuis une branche
supprimée se ferme avec elle, son contenu gardé dans la branche qui la
contient ; une marque d'agent que l'humain pose sur son propre commit lui
fait traiter sa branche comme celle de l'agent. En plus : la commande ne
retire aucune référence locale, et ce qu'elle laisse de périmé, l'état le
juge comme avant (une branche que l'origine n'a plus ne se propose pas ;
un commit cité qu'elle seule garde se dit à étiqueter), jusqu'au
`git fetch --prune` que l'humain ou une session neuve lance. Se défait,
pour un projet, par `prune_branches = false` ; pour le produit, en
retirant la commande et la partition de l'état.
