<!-- socle: couche=demandes zone=publique -->
# D-0092 — Autoriser l'agent à fusionner lui-même ses pull requests dans ce dépôt

> date : 2026-11-10

## Décision demandée

Autoriser l'agent à fusionner lui-même ses pull requests dans ce dépôt, en
retirant la fusion de la liste des actions que la politique lui refuse.

## Contexte

**Le projet.** Ce dépôt, theodubus/memory, fabrique le socle, un outil qui
s'installe dans le dépôt d'un projet de code entretenu par un agent IA : il
tient la mémoire du projet, et des contrôles automatiques vérifient ce que
l'agent produit. Sa partie installable, le moteur (le code Python du
socle), est publiée telle quelle dans le dépôt public theodubus/socle par
un workflow (un script que GitHub lance) à chaque fusion sur la branche
principale, `main`. JustCook, votre application de cuisine, le reçoit de
là quand vous lancez sa mise à jour ; c'est aujourd'hui le seul projet
équipé.

**Le chantier.** L'agent travaille sur une branche à lui et livre chaque
lot de travail par une pull request, une proposition de changements que
vous fusionnez dans `main` ; une seule est ouverte à la fois, et un lot
touche le moteur, sa documentation et la mémoire du projet. Avant de
pousser un lot, l'agent le fait relire par un second agent sans contexte,
la revue adversariale, que vous avez voulue début novembre ; la CI, les
vérifications que GitHub lance à chaque envoi, doit ensuite être verte,
et GitHub refuse la fusion tant qu'elle ne l'est pas. Ce 10 novembre, vous
avez fusionné vous-même deux pull requests de l'agent.

**La question.** Ce 10 novembre, vous l'avez écrit : « c'est long de merge
a chaque fois, fais une demande pour modifier la politique et t'autoriser a
merge toi meme ». La politique, `.socle/policy.toml`, est le fichier où
vous fixez ce que l'agent peut faire seul ; lui ne peut pas l'écrire. Sa
section `[irreversible]` liste les actions irréversibles ou externes que
le hook de l'agent (le contrôle qui juge chacune de ses commandes) lui
refuse, même après une demande validée. Vide, elle vaut la liste par
défaut du socle, qui comprend la fusion.

### Ce qui changerait

L'agent agit sur GitHub par des outils nommés `mcp__github__…`. La liste
par défaut refuse ces huit outils : fusionner une pull request
(`merge_pull_request`), supprimer un fichier sur GitHub, créer un dépôt,
copier un dépôt (fork), créer une release (une version publiée sur
GitHub), pousser des fichiers par l'API, créer ou modifier un fichier par
l'API, activer la fusion automatique (GitHub fusionne seul dès que la CI
passe). La ligne proposée est un motif qui désigne les sept derniers :
elle remplace la liste par défaut par la même, moins la fusion. Le push
forcé et le push direct sur `main` restent refusés par une règle à part
du hook, que cette ligne ne touche pas.

L'agent fusionnerait sa pull request quand trois conditions tiennent :

1. sa CI est verte, ce que GitHub impose ;
2. la revue adversariale du dernier lot est faite et ses constats traités ;
3. aucune demande qui vous attend ne porte sur ce que la pull request
   contient.

Seule la première est contrôlée. Les deux autres, et le fait de ne
fusionner que ses propres pull requests, seraient des consignes écrites
dans les instructions de ce dépôt, `AGENTS.md` : l'outil lui-même
permettrait de fusionner toute pull request. Chaque fusion se dirait dans
le récap, le compte rendu qui clôt chaque intervention de l'agent, avec
son lien.

La ligne fige la liste : un outil que le socle ajouterait plus tard à sa
liste par défaut ne serait pas refusé ici avant que la ligne le reprenne.
Elle ne vaut que pour ce dépôt ; l'étendre aux projets équipés serait une
autre décision.

Chaque fusion publie le moteur dans theodubus/socle, comme aujourd'hui.
Une fusion fautive se défait par un commit qui l'annule, que la fusion
suivante publie ; l'historique du dépôt public garde la version fautive.

### Votre geste, si vous validez

La politique étant protégée, vous l'écrivez vous-même, sur GitHub :

1. ouvrir `.socle/policy.toml` sur la branche de travail de l'agent,
   `ccr-82da0a2e-iccil9`, et l'éditer (le crayon) ;
2. juste sous la ligne `# tools = ['mcp__github__merge_pull_request', ...]`,
   sans ligne vide, ajouter cette ligne, telle quelle :

```toml
tools = ['mcp__github__(delete_file|create_repository|fork_repository|create_release|push_files|create_or_update_file|enable_pr_auto_merge)']
```

3. valider le commit sur cette même branche, sans rien changer d'autre.

L'autorisation vaut dès ce commit sur la branche, que l'agent récupère.
Le contrôle des fichiers protégés, qui tourne dans la CI, compare le
fichier obtenu à l'empreinte citée plus bas : s'ils diffèrent, la CI est
rouge, rien ne se fusionne, et l'agent vous propose la correction.

La pull request qui portera votre commit et la règle que l'agent écrira
dans `AGENTS.md`, vous la fusionnez vous-même, après en avoir lu la
règle ; l'agent ne fusionne que les suivantes.

## Éléments cités

Les numéros : B- un sujet du backlog, ADR- une décision du projet, D- une
demande comme celle-ci ; après @, l'empreinte de la version que j'ai lue.

- ADR-0040@0f8b7bb0 — la décision du 31 octobre : le moteur se publie
  dans theodubus/socle, par un workflow, à chaque fusion sur `main`.
- ADR-0042@c8fe8e02 — la décision du 2 novembre : chaque lot est relu par
  un relecteur sans contexte avant d'être livré.
- B-0048@af110830 — le sujet ouvert du 12 octobre : une action externe
  reste refusée par le hook même quand une demande validée l'autorise ;
  vous aviez choisi d'attendre qu'il devienne bloquant. Cette demande
  règle le cas de la fusion par la politique, sans toucher à ce sujet.
- `.socle/policy.toml`, `sha256:694e4780d1085f3a` — l'empreinte de la
  politique actuelle avec la seule ligne ajoutée : une signature de son
  contenu octet par octet (SHA-256), que le contrôle des fichiers protégés
  compare.

## Où regarder

- [La politique actuelle](https://github.com/theodubus/memory/blob/ec382d255cf77d7a98ee05f4a914d362eb05d6a7/.socle/policy.toml) :
  la section `[irreversible]`, où la ligne s'ajoute ; vérifier que
  l'exemple commenté `# tools = …` y est.
- [La liste par défaut du moteur](https://github.com/theodubus/memory/blob/ec382d255cf77d7a98ee05f4a914d362eb05d6a7/engine/socle/hooks.py#L43) :
  vérifier que la ligne proposée la reprend, moins `merge_pull_request`.

## Options

- **Valider** : quelques minutes, votre édition de la politique sur
  GitHub, puis une dernière pull request à fusionner vous-même. L'agent
  fusionne ensuite ses pull requests, à peu près une par lot, sous les
  trois conditions. Risque : un lot arrive dans `main` et dans le dépôt
  public sans que vous l'ayez regardé ; le récap le dit à chaque fois.
  Réversible : retirer la ligne rend la règle par défaut.
- **Refuser** : aucun effort ; vous continuez de fusionner vous-même,
  quand vous voulez. Aucun risque nouveau.

## Conséquences

Si vous validez, l'agent consigne votre réponse, attend votre commit de la
politique, vérifie son empreinte, écrit la règle dans `AGENTS.md` et le
note au journal ; vous fusionnez cette pull request-là, puis il fusionne
les suivantes. Si vous refusez, rien ne change. Sans réponse, rien ne
change non plus : l'agent continue de livrer par des pull requests que
vous fusionnez.

## Recommandation

Valider. Vérifié : la ligne proposée laisse passer la fusion et refuse les
sept autres outils de la liste par défaut (essayé sur le texte de la
politique) ; GitHub exige la CI du socle avant toute fusion sur `main` ;
l'empreinte citée est celle de la politique actuelle avec la seule ligne
ajoutée. Supposé : que les trois conditions, dont deux reposent sur la
consigne, suffisent à ce que vous n'ayez pas à relire chaque lot avant sa
fusion.

## Réponses possibles

- `valider` — vous ajoutez la ligne à la politique ; l'agent fusionne ensuite lui-même ses pull requests, sous les trois conditions.
- `refuser` — rien ne change : vous fusionnez vous-même.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
