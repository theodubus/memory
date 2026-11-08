<!-- socle: couche=demandes zone=publique -->
# D-0081 — Valider le skill socle-resume dans ce dépôt, et les deux tests qui comptent désormais quatre skills du socle (B-0132)

> date : 2026-11-08

## Décision demandée

Valider le texte français du skill `socle-resume`, recopié plus bas, dans
sa copie protégée de ce dépôt, `.claude/skills/socle-resume/SKILL.md`,
d'empreinte `sha256:7e6afad165b66aca` ; et la valeur attendue de deux
tests de `tests/test_skills.py`, qui listent les skills du socle et en
attendent maintenant quatre au lieu de trois.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA comme Claude Code. Il
garde la mémoire du projet, vérifie ce que l'agent produit, et vous pose
sous forme de « demandes », des fichiers comme celui-ci, les décisions qui
vous reviennent. Ce dépôt se sert lui-même du socle qu'il fabrique.

**Le chantier.** Le 8 novembre au soir, vous avez validé la règle qui fait
reprendre seul un agent coupé par une limite d'usage de votre compte :
deux réveils, des messages que l'agent programme pour sa propre session,
armés pendant chaque tour où il agit, retirés à sa fin, et vérifiés au
réveil. Un arrêt pour une autre raison, en attendant votre action, ne
relance jamais : vous l'avez demandé. Le skill qui l'applique est écrit.

**La question.** L'installeur, la commande qui équipe un projet, pose une
copie du skill dans chaque projet, et dans celui-ci, où elle est protégée :
un contrôle refuse qu'elle change sans une demande validée qui cite son
empreinte, et vérifie que l'empreinte est celle du texte. Deux tests, qui
listent les skills du socle, en attendent maintenant quatre : changer la
valeur attendue d'un test demande aussi votre accord. Rien ne se commite
avant votre réponse.

**Les mots.** Un tour : ce que fait l'agent entre deux messages reçus ;
coupé, la limite l'arrête en cours ; refusé, elle l'empêche de commencer.
Un sous-agent : un second agent lancé pour une tâche à part. Un lot : les
sujets traités d'affilée ; une étape, une partie d'un lot. Le contrôle de
fin de tour : ce que vérifie le socle avant que l'agent conclue. Les noms
entre accents graves sont des outils de l'agent. Une session cloud tourne
sur un serveur ; ailleurs, le skill ne fait rien.

**Ce qui diffère de la règle validée.** Le nom : la règle disait
`socle-reprise` ; votre décision du 13 octobre met en anglais les noms de
dossiers du socle, comme ceux des trois autres skills. Des précisions,
dont quatre venues de la revue du lot : un sous-agent ne touche à aucun
réveil ; l'agent réarme ses réveils si le contrôle de fin de tour refuse
de conclure ; il poursuit un sous-agent coupé avant de le relancer ; un
message de reprise de l'application vaut « reprends ». Le reste est la
mise en œuvre : les outils, le nom et le texte des réveils.

**Ce qu'il ne couvre pas**, relevé par la même revue : un tour qu'ouvre,
pendant une limite, un rappel de l'agent, un événement de GitHub ou votre
message, alors que l'agent attendait sans travailler, est refusé, et rien
ne le relance. Le couvrir change la règle : c'est un sujet à part, pour
une autre demande.

**Les deux tests**, dans `tests/test_skills.py` :
- `test_l_installeur_les_pose_et_la_politique_les_protege` et
  `test_dans_les_deux_langues_ils_passent_leurs_controles` : la liste
  attendue `socle-private-memory, socle-request, socle-review` gagne
  `socle-resume`, à son rang alphabétique.

**Le skill, en français, mot pour mot.** Sa version anglaise, posée dans
les projets en anglais, le traduit ; la revue du lot la relit.

> ---
> name: socle-resume
> description: Faire reprendre seul l'agent qu'une limite d'usage coupe, par deux réveils programmés sur sa propre session, sans jamais relancer un agent que rien n'a coupé. À utiliser dans une session cloud de Claude Code, au début et à la fin de chaque tour où l'agent agit, à chaque étape, et quand un message commence par « Reprise après limite ».
> ---
>
> # La reprise après une limite d'usage
>
> Une limite d'usage du compte, sur cinq heures ou sur sept jours, coupe la
> session ; coupé, l'agent ne reprend qu'au message suivant de l'humain. Deux
> réveils, des messages que l'agent programme pour sa propre session, le
> font reprendre dès que la limite se lève. Ils ne vivent que pendant un
> tour qui travaille : un tour qui finit, pour toute autre raison qu'une
> limite (en attendant l'humain, par exemple), ne relance jamais l'agent.
>
> ## Quand
>
> Dans une session cloud de Claude Code seulement, où existent les outils
> `send_later`, `update_trigger`, `delete_trigger`, `list_triggers`,
> `list_events` et `get_session` (serveur `claude-code-remote`). Ailleurs, ce
> skill ne s'applique pas. Une réponse en texte seul n'arme rien ; un tour où
> l'agent lance une commande, écrit un fichier ou lance un sous-agent arme.
> Un sous-agent ne touche à aucun réveil : ni armer, ni déplacer, ni retirer.
>
> ## Les deux réveils
>
> Un par fenêtre, nommés « Reprise après limite (cinq heures) — <dépôt> » et
> « Reprise après limite (semaine) — <dépôt> », chacun cinq minutes après la
> remise à zéro de sa fenêtre, de jour comme de nuit, quel que soit son
> remplissage. L'heure : `get_session` sans argument donne l'identifiant de
> la session ; `list_events` avec `kinds: ["rate_limit_event"]` et
> `limit: 100`, en remontant par `before_id` tant que rien n'est trouvé ;
> dans le plus récent, `rate_limit_info.unifiedWindows.five_hour.resetsAt`
> et `….seven_day.resetsAt`, en secondes depuis 1970, UTC.
>
> Leur texte, récrit à chaque fois :
>
> ```text
> Reprise après limite (<fenêtre>) — <dépôt>, branche <branche>.
> Avant tout : la vérification du skill socle-resume.
> Lot : <les sujets>. Étape : <ce qui était en cours, ce qui reste>.
> Sous-agents en cours : <chacun : son identifiant, sa tâche, ce qu'il doit rendre> | aucun.
> ```
>
> ## Au début de chaque tour où l'agent agit
>
> 1. Lire l'heure des deux remises à zéro.
> 2. Chercher ses réveils : `list_triggers` avec `enabled: true` et
>    `limit: 100`, en suivant `next_cursor`, ceux de ces deux noms dont
>    `persistent_session_id` est cette session.
> 3. Présent, le déplacer et récrire son texte : `update_trigger`, avec
>    `run_once_at` et `prompt`. Absent, l'armer : `send_later`, avec `at`
>    (la remise à zéro plus cinq minutes), `name` et `message`. Jamais deux
>    réveils de la même fenêtre.
>
> ## À chaque étape, et à chaque sous-agent lancé ou rendu
>
> Récrire le texte des deux réveils (`update_trigger`), et recaler leur
> heure si une fenêtre s'est remise à zéro pendant le tour.
>
> ## À la fin de chaque tour
>
> Avant la réponse finale, si aucun sous-agent ne tourne encore, retirer les
> deux réveils (`delete_trigger`). Si un sous-agent tourne, les laisser, leur
> texte à jour : ils restent jusqu'au tour qui reçoit son résultat. Un tour
> coupé ou refusé ne retire rien : c'est ce qui le fait reprendre. Si le
> tour continue après les avoir retirés (un hook de fin de tour refuse de
> conclure, par exemple), les réarmer.
>
> ## Au réveil : vérifier d'abord
>
> Un message qui commence par « Reprise après limite » :
>
> 1. Lire `list_events` avec `kinds: ["result"]` et `limit: 100` : le
>    dernier résultat avant ce réveil clôt le tour d'avant, quoi qui l'ait
>    ouvert (un message de l'humain, le résultat d'un sous-agent, un autre
>    réveil) ; il a fini sur une limite s'il est en erreur
>    `usage_limit_reached`. Puis, avec `kinds: ["user"]`, les messages
>    arrivés depuis la coupure, même refusés : ceux de l'humain sont un texte
>    tapé, ni un résultat d'outil, ni un réveil, ni une notification ; un
>    message de reprise de l'application (`text_not_typed`) vaut « reprends ».
> 2. Ne pas reprendre :
>    - si le tour d'avant n'a pas fini sur une limite (l'humain l'a
>      interrompu, ou il a fini normalement) ;
>    - si l'humain a écrit depuis la coupure : répondre à son message, qui
>      prime ; s'il dit d'arrêter, s'arrêter ;
>    - si une autre session a poussé sur la branche depuis le dernier commit
>      de l'agent (`git fetch`, puis comparer) ;
>    - si la pull request de la branche a été fusionnée ou fermée depuis.
>
>    Répondre alors brièvement pourquoi, avec les lignes de fin que le projet
>    exige, et retirer ses réveils, ou les recaler si un sous-agent tourne.
> 3. Sinon, reprendre l'étape notée. Chaque sous-agent noté dont le résultat
>    n'est pas arrivé : le poursuivre par un message (`SendMessage`, à son
>    identifiant) s'il répond encore, sinon le relancer avec son message tel
>    quel. Réarmer les réveils, et continuer comme sur « reprends ». Le récap le dit
>    (« Reprise après limite : coupé à <heure>, repris à <heure> »), et une
>    entrée au journal aussi.
>
> ## Ce que l'agent ne fait jamais
>
> Armer un réveil récurrent, ou hors d'un tour où il agit ; reprendre sans la
> vérification ; garder un réveil à la fin d'un tour sans sous-agent en
> cours ; toucher au réveil d'une autre session. L'humain arrête tout en
> écrivant « arrête » dans la session ; les réveils figurent aussi dans la
> liste des tâches programmées de son compte, où ils se suppriment.

## Éléments cités

Les numéros : B- un sujet du backlog, ADR- une décision de conception, D-
une demande, J- une entrée du journal ; après @, l'empreinte de la
version que j'ai lue, une somme de contrôle de son texte.

- D-0080@bf2d22c6 — la règle que vous avez validée le 8 novembre.
- ADR-0050@c8efc6f1 — la décision de conception qui la recopie, pour la
  garder au registre des décisions du projet.
- ADR-0027@a8288770 — votre décision du 13 octobre : les noms de fichiers
  et de dossiers du socle en anglais.
- B-0133@3ee39e0f — le sujet ouvert pour ce que le skill ne couvre pas.
- B-0132@cc8d5405 — le sujet, fait quand un réveil aura repris une coupure.
- `.claude/skills/socle-resume/SKILL.md` et `sha256:7e6afad165b66aca` — la
  copie protégée de ce dépôt, et l'empreinte de son texte.

## Où regarder

- [D-0080](https://github.com/theodubus/memory/blob/1d75aed350a3a6666269fdfcf1208dcda03f04cd/memory/requests/D-0080-valider-la-specification-de-la-reprise-apres-une-l.md) :
  la règle validée, pour la comparer au skill.

## Options

- **Valider** (`valider`, recommandée) : effort nul ; risque, qu'un réveil
  ne reprenne pas, et une reprise prend la fenêtre neuve comme si vous
  relanciez l'agent ; réversible, par une demande.
- **L'ancien nom** (`nom-socle-reprise`) : le même texte, nommé
  `socle-reprise`, par exception à la décision du 13 octobre ; effort et
  risque nuls ; réversible.
- **Refuser** (`refuser`) : effort nul ; rien ne se commite ; réversible.

## Conséquences

Si vous validez, je commite et pousse le lot sur la branche de travail,
dans la pull request ouverte ; ce dépôt applique le skill au tour suivant,
les autres projets à leur mise à jour du socle. Si vous refusez, je
corrige ce que vous dites. Sans réponse, rien ne se commite.

## Recommandation

Valider. Vérifié : le skill suit la règle validée, passe les contrôles des
skills en deux langues, et les 695 tests passent. Supposé : qu'un réveil
reprenne une session coupée ; la première coupure le dira.

## Réponses possibles

- `valider` — la copie du skill et les deux valeurs attendues sont validées ; l'agent commite et pousse le lot.
- `nom-socle-reprise` — le même texte, renommé `socle-reprise` ; l'agent renomme, puis vous soumet l'empreinte nouvelle.
- `refuser` — rien ne se commite ; l'agent revient avec ce qui change.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
