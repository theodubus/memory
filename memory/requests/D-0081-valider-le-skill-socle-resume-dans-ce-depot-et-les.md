<!-- socle: couche=demandes zone=publique -->
# D-0081 — Valider le skill socle-resume dans ce dépôt, et les deux tests qui comptent désormais quatre skills du socle (B-0132)

> date : 2026-11-08

## Décision demandée

Valider le texte français du skill `socle-resume`, recopié plus bas, dans
sa copie protégée de ce dépôt, `.claude/skills/socle-resume/SKILL.md`,
d'empreinte `sha256:f6b79cabf96ab4e1` ; et la valeur attendue de deux
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
réveil. Un arrêt pour une autre raison, en attendant une action de votre
part, ne relance jamais : vous l'avez demandé, et la règle le garantit par
le retrait et par la vérification. Le skill est écrit, avec deux tests.

**La question.** La source du skill est dans le moteur ; l'installeur, la
commande qui équipe un projet ou le met à jour, en pose une copie dans
chaque projet, et dans celui-ci. Cette copie est protégée : un contrôle
refuse qu'elle change sans une demande validée qui cite son empreinte, et
vérifie lui-même que l'empreinte est celle du texte. Deux tests existants,
qui listent les skills du socle, en attendent maintenant quatre : changer
la valeur attendue d'un test demande aussi votre accord. Rien de ce
travail ne se commite avant votre réponse.

**Les mots.** Un tour : ce que fait l'agent entre deux messages reçus ;
coupé, la limite l'arrête en cours ; refusé, elle l'empêche de commencer.
Un sous-agent : un second agent lancé pour une tâche à part, comme une
relecture ; son message reste dans la conversation. Un lot : les sujets
traités d'affilée ; une étape, une partie d'un lot. Le contrôle de fin de
tour : la vérification que le socle fait avant que l'agent conclue. Le
récap : la fin de chaque réponse ; le journal : la mémoire datée du
projet ; « reprends » : votre mot pour relancer l'agent. Les noms entre accents graves du skill sont des outils et des
champs que l'agent emploie. Une session cloud tourne sur un serveur ;
ailleurs, le skill ne fait rien.

**Ce qui diffère de la règle validée.** Le nom : la règle disait
`socle-reprise` ; votre décision du 13 octobre met en anglais les noms de
dossiers du socle, comme ceux des trois autres skills. Deux précisions :
un sous-agent n'arme aucun réveil ; si le contrôle de fin de tour refuse de
conclure après le retrait des réveils, l'agent les réarme. Le reste n'est
que la mise en œuvre : les outils, le nom et le texte des réveils.

**La coupure de ce soir.** À 22 h 41, deux minutes après la remise à
zéro, l'application web de Claude a envoyé seule un message de reprise :
sans doute parce qu'une page était ouverte. Les réveils couvrent le cas
contraire, sans reprise en double.

**Les deux tests**, dans `tests/test_skills.py` :
- `test_l_installeur_les_pose_et_la_politique_les_protege` : la liste
  attendue `socle-private-memory, socle-request, socle-review` devient
  `socle-private-memory, socle-request, socle-resume, socle-review`.
- `test_dans_les_deux_langues_ils_passent_leurs_controles` : le message
  attendu de l'installeur gagne `socle-resume` dans la même liste.

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
> Seul l'agent de la session arme : un sous-agent n'arme rien.
>
> ## Les deux réveils
>
> Un par fenêtre, nommés « Reprise après limite (cinq heures) — <dépôt> » et
> « Reprise après limite (semaine) — <dépôt> », chacun cinq minutes après la
> remise à zéro de sa fenêtre, de jour comme de nuit, quel que soit son
> remplissage. L'heure se lit dans les événements de la session :
> `get_session` sans argument donne son identifiant, puis `list_events`
> avec `kinds: ["rate_limit_event"]` ; le plus récent donne, pour
> `five_hour` et `seven_day`, `resetsAt`, en secondes depuis 1970, UTC.
>
> Leur texte, récrit à chaque fois :
>
> ```text
> Reprise après limite (<fenêtre>) — <dépôt>, branche <branche>.
> Avant tout : la vérification du skill socle-resume.
> Lot : <les sujets>. Étape : <ce qui était en cours, ce qui reste>.
> Sous-agents en cours : <chacun : sa tâche, ce qu'il doit rendre, où est son message> | aucun.
> ```
>
> ## Au début de chaque tour où l'agent agit
>
> 1. Lire l'heure des deux remises à zéro.
> 2. Chercher ses réveils : `list_triggers`, ceux de ces deux noms dont
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
> 1. Lire `list_events` avec `kinds: ["user", "result"]`. Le tour d'avant
>    est le dernier avant ce réveil, quoi qui l'ait ouvert : un message de
>    l'humain, le résultat d'un sous-agent, un autre réveil. Il a fini sur
>    une limite si son résultat est en erreur `usage_limit_reached`. Lire
>    aussi chaque message de l'humain arrivé depuis la coupure, même refusé.
> 2. Ne pas reprendre :
>    - si le tour d'avant n'a pas fini sur une limite (l'humain l'a
>      interrompu, ou il a fini normalement) ;
>    - si l'humain a écrit depuis la coupure : répondre à son message, qui
>      prime ; s'il dit d'arrêter, s'arrêter ;
>    - si une autre session a poussé sur la branche depuis le dernier commit
>      de l'agent (`git fetch`, puis comparer) ;
>    - si la pull request de la branche a été fusionnée ou fermée depuis.
>
>    Répondre alors en une ligne qui dit pourquoi, et retirer ses réveils,
>    ou les recaler si un sous-agent tourne encore.
> 3. Sinon, reprendre l'étape notée, relancer chaque sous-agent noté dont le
>    résultat n'est pas arrivé, avec son message tel quel, réarmer les
>    réveils, et continuer comme sur « reprends ». Le récap le dit
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
- J-2026-11-08-L@f0f4b23f — la coupure de ce soir, heure par heure.
- B-0132@cc8d5405 — le sujet, fait quand un réveil aura repris une coupure.
- `.claude/skills/socle-resume/SKILL.md` et `sha256:f6b79cabf96ab4e1` — la
  copie protégée de ce dépôt, et l'empreinte de son texte.

## Où regarder

- [D-0080](https://github.com/theodubus/memory/blob/1d75aed350a3a6666269fdfcf1208dcda03f04cd/memory/requests/D-0080-valider-la-specification-de-la-reprise-apres-une-l.md) :
  la règle validée, pour la comparer au skill.

## Options

- **Valider** (`valider`, recommandée) : effort nul ; risque, qu'un réveil
  ne reprenne pas une session coupée, ce que la première coupure dira, et
  une reprise prend la fenêtre neuve comme si vous relanciez l'agent ;
  réversible, par une demande.
- **L'ancien nom** (`nom-socle-reprise`) : le même texte, nommé
  `socle-reprise`, par exception à la décision du 13 octobre ; effort et
  risque nuls ; réversible.
- **Refuser** (`refuser`) : effort nul ; rien ne se commite, et je reviens
  avec le texte à changer ; réversible.

## Conséquences

Si vous validez, je consigne votre réponse, puis commite et pousse le lot
sur la branche de travail, dans la pull request ouverte, que vous fusionnez
quand vous voulez ; ce dépôt applique le skill au tour suivant, et les
autres projets à leur mise à jour du socle. Si vous refusez, je corrige ce
que votre réponse dit. Sans réponse, rien ne se commite, et je travaille
sur autre chose.

## Recommandation

Valider. Vérifié : le skill suit la règle validée, passe les contrôles des
skills en deux langues, et les 695 tests passent. Supposé : qu'un réveil
reprenne une session coupée ; la première coupure le dira.

## Réponses possibles

- `valider` — la copie du skill et les deux valeurs attendues sont validées ; l'agent commite et pousse le lot.
- `nom-socle-reprise` — le même texte, renommé `socle-reprise` ; l'agent renomme, puis vous soumet l'empreinte nouvelle.
- `refuser` — rien ne se commite ; l'agent revient avec ce qui change.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
