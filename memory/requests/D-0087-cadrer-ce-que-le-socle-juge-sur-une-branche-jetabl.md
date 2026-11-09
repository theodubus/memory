<!-- socle: couche=demandes zone=publique -->
# D-0087 — Cadrer ce que le socle juge sur une branche jetable

> date : 2026-11-09

## Décision demandée

Répondre librement aux questions de cadrage ci-dessous : la spécification
de ce sujet dépend d'une intention que la mémoire ne dit pas.

## Contexte

**Le projet.** Ce dépôt fabrique le socle, un outil qui s'installe dans le
dépôt d'un projet de code entretenu par un agent IA : il tient la mémoire
du projet, et des contrôles automatiques vérifient ce que l'agent produit,
à trois endroits : dans la session de l'agent, avant chaque commit, et dans
la CI, les vérifications que GitHub lance à chaque envoi de commits.
JustCook, votre application de cuisine, est le projet pilote : l'agent qui
y travaille vous rapporte ce qui le gêne dans le socle, et vous me le
transmettez. La règle qui sortira de vos réponses vaudra pour tout projet
équipé du socle.

**Le chantier.** Le 8 novembre, l'agent de JustCook vous a rapporté six
gênes. Ce 9 novembre, vous avez demandé qu'elles soient réglées avant la
prochaine mise à jour du socle installé dans JustCook. Trois sont réglées ;
les trois autres vous sont posées ce jour, chacune dans sa demande. Celle-ci
porte sur la dernière : ce que le socle juge sur une branche jetable, une
branche d'essai que l'agent crée pour un prototype et ne compte pas
fusionner.

**La question.** Aujourd'hui, une branche jetable est jugée comme la
branche de travail, celle où l'agent livre son travail et que vous
fusionnez par une pull request. Pour écrire une règle qui la juge
autrement, il me manque ce qu'est pour vous une branche jetable, et ce que
le socle doit y juger encore.

### Ce qui gêne, concrètement

- **La CI rouge.** La CI du socle tourne à chaque envoi, sur toute branche.
  Sur une branche d'essai de JustCook, un commit de correctif (son titre
  commence par `fix:`) sans test l'a fait échouer : le socle exige qu'un
  correctif livre un test qui échoue sans lui. Une CI rouge sur une branche
  jamais fusionnée ne bloque rien ; elle marque la branche en rouge sur
  GitHub, et peut vous valoir un courriel d'échec.
- **Un fichier tiers.** L'agent de JustCook a copié dans une branche
  d'essai un paquet avec son mode d'emploi. Le contrôle des références du
  socle, qui vérifie les liens de chaque fichier Markdown du dépôt, a
  refusé les liens morts de ce mode d'emploi, dès le commit. Le socle sait
  ignorer les fichiers d'un outil tiers, mais il faut les déclarer dans les
  garde-fous du projet, le fichier de réglages de ses contrôles. Les y
  déclarer relâche un contrôle, ce que seule votre validation permet, même
  sur une branche qui ne sera jamais fusionnée. L'agent a contourné en
  remplaçant le mode d'emploi par un fichier sans liens.

## Questions

1. **Qu'est-ce qu'une branche jetable, pour vous : une branche nommée d'une
   certaine façon, toute branche sans pull request, ou autre chose ?**
   C'est l'agent qui crée les branches et les nomme : une branche nommée
   jetable pourrait porter du vrai travail ; « toute branche sans pull
   request » ferait jetable la branche de travail avant que sa pull request
   ne s'ouvre. Hypothèse de l'agent : une branche dont le nom commence par
   un préfixe que le projet déclare dans ses garde-fous, `proto/` par
   défaut ; ce qui en sort ne se fusionne que par une pull request, jugée
   en entier (question 5).
2. **Sur une branche jetable, la CI du socle doit-elle tourner à chaque
   envoi, ne pas tourner, ou tourner en avertissant sans jamais échouer ?**
   Hypothèse de l'agent : elle ne tourne pas aux envois ; elle tourne, et
   juge tout, dès qu'une pull request part de cette branche.
3. **Les contrôles avant commit et ceux de la session de l'agent
   doivent-ils s'y relâcher aussi, et lesquels ?** Hypothèse de l'agent :
   ils restent, sauf le contrôle des références sur un fichier qu'une
   branche jetable ajoute, qui y avertit au lieu de refuser. Il rend alors
   inutile, sur la branche, de déclarer ce fichier tiers (question 4).
4. **Sur une branche jetable, déclarer un fichier tiers doit-il encore
   attendre votre validation ?** Hypothèse de l'agent : oui ; avec la
   réponse supposée à la question 3, l'agent n'a plus à le déclarer tant
   que la branche reste jetable.
5. **Une branche jetable peut-elle finir fusionnée ?** Hypothèse de
   l'agent : oui, par une pull request, dont la CI juge tout comme pour
   n'importe quelle branche ; un fichier tiers qu'elle apporte se déclare
   alors, par une demande que vous validez.

## Éléments cités

Les numéros : B- un sujet du backlog, ADR- une décision du projet, J- une
entrée du journal, datée et suivie de son rang dans la journée ; après @,
l'empreinte de la version que j'ai lue.

- B-0137@9aee47bd — le sujet des branches jetables, ouvert sur le retour de
  l'agent de JustCook, qui réserve son cadrage à votre réponse.
- J-2026-11-08-S@b8e4e7e4 — le retour de l'agent de JustCook, le 8
  novembre, et ses six gênes, dont celle-ci.
- ADR-0031@ded211d6 — la décision du 19 octobre : les fichiers d'un outil
  tiers, déclarés une fois, échappent à tous les contrôles ; les déclarer
  relâche un contrôle.

## Où regarder

- [B-0137](https://github.com/theodubus/memory/blob/95a3f20d7268e6d860ad8ca14e2dabab425a6f34/memory/backlog/B-0137-les-branches-jetables-sont-jugees-comme-la-branche.md) :
  la gêne telle que l'agent de JustCook l'a décrite.

Ce qu'il faut vérifier, avant de répondre : que chaque question demande
votre intention, et non un choix que l'agent pourrait trancher seul.

## Options

- **Répondre** : quelques minutes, votre texte dans la conversation, en un
  ou plusieurs messages, que l'agent consigne tel quel. Vous pouvez valider
  certaines hypothèses et répondre aux autres (« valider, sauf la 3 :
  … »). Risque faible, la spécification suit ce que vous voulez ;
  réversible.
- **Valider les hypothèses** : effort nul. Elles s'appliquent, notées
  « supposées » dans la mémoire du projet : une intention qu'aucune réponse
  de votre part n'a confirmée, que l'agent signale et corrige dès qu'un
  fait la contredit. Réversible.
- **Refuser** : effort nul ; le sujet attend, sans spécification ;
  réversible.

## Conséquences

Si vous répondez, l'agent consigne votre texte exact, puis écrit la
spécification qui en découle, et vous la soumet dans une demande. Si vous
validez les hypothèses, il les applique, notées « supposées ». Si vous
refusez, le sujet attend. Si les questions ne se comprennent pas
(`contexte-insuffisant`), l'agent les réécrit. Sans réponse, le sujet
attend aussi ; selon votre consigne, la mise à jour de JustCook attend vos
réponses à ses gênes, mais vous pouvez la lancer sans celle-ci : la règle
viendrait alors avec une mise à jour suivante.

## Recommandation

Valider les hypothèses si elles disent votre intention ; sinon répondre,
même brièvement. Vérifié : la CI que pose le socle tourne à chaque envoi,
sur toute branche ; le contrôle des références refuse dès le commit un
lien mort dans un fichier Markdown ; déclarer un fichier tiers relâche un
contrôle, ce qui attend votre validation. Supposé : que l'agent d'un projet
crée ses branches d'essai sous un nom reconnaissable.

## Réponses possibles

- `valider` — les hypothèses de l'agent s'appliquent, notées « supposées ».
- `reponses` — le texte de votre réponse, en un ou plusieurs messages, donne les réponses ; l'agent le consigne tel quel.
- `refuser` — le sujet attend, sans spécification.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
