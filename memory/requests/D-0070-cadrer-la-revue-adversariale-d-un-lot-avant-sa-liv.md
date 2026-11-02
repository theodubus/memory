<!-- socle: couche=demandes zone=publique -->
# D-0070 — Cadrer la revue adversariale d'un lot avant sa livraison (B-0124)

> date : 2026-11-02

## Décision demandée

Répondre librement aux questions de cadrage ci-dessous : la spécification
de ce sujet dépend d'une intention que la mémoire ne dit pas.

## Contexte

Avec BMAD, le travail d'un agent était relu par des relecteurs
indépendants, dont un relecteur adversarial, chargé de le prendre en
défaut. Au retrait de BMAD, ce principe a été rangé dans la répartition du
travail entre plusieurs agents, qui viendra tard : elle attend la
planification, qui attend le pilote. Vous avez demandé s'il avait été
abandonné. Il ne l'est pas, et il n'a pas besoin d'un agent maître : il a
son sujet propre, B-0124. Avant de livrer un lot, l'agent confierait son
diff à un relecteur qui n'a pas le contexte de la conversation. Ce
relecteur chercherait ce qui casse, ce qu'aucun test ne prouve, ce qui
contredit la mémoire ou une spécification. L'agent corrigerait chaque
constat, ou y répondrait. Les contrôles du socle jugent déjà la forme du
travail, sa mémoire, ses tests et ses refus. La revue ajouterait un
jugement sur le fond, qu'aucun contrôle automatique ne porte. La mémoire
ne dit pas quand la faire, ce qu'elle bloque, ce qu'elle peut coûter, ni si
elle vaut pour tout projet : ces points dépendent de ce que vous en
attendez.

## Questions

1. **Quand la revue a-t-elle lieu ?** Hypothèse de l'agent : à chaque lot
   qui change du code, une spécification ou un test, avant le push qui le
   livre dans la pull request ; pas sur un lot qui ne touche que la
   mémoire.
2. **Qui relit ?** Hypothèse de l'agent : un sous-agent lancé par l'agent,
   sans le contexte de la conversation, avec seulement le diff du lot, les
   sujets qu'il ferme et les spécifications qu'il cite ; le même modèle que
   la session. Un agent sans sous-agents la saute, et son récap le dit.
3. **Que fait un constat ?** Hypothèse de l'agent : aucun ne bloque seul.
   L'agent corrige chaque constat fondé, et répond aux autres en une ligne.
   Le récap dit combien de constats, combien sont corrigés et pourquoi les
   autres sont écartés. Rien n'est posté sur GitHub.
4. **Combien peut-elle coûter ?** Une revue ajoute à peu près le prix d'une
   relecture complète du diff. Hypothèse de l'agent : une seule passe par
   lot, sans seconde revue après les corrections.
5. **Vaut-elle pour tout projet équipé, ou seulement si l'humain la
   choisit ?** Hypothèse de l'agent : elle se mesure d'abord au banc, sur des
   défauts connus que les contrôles ne voient pas. Elle devient la règle par
   défaut si elle en trouve ; sinon, elle reste une option des questions de
   départ.
6. **Voulez-vous lire la revue elle-même**, ou seulement ce que le récap
   en dit ? Hypothèse de l'agent : le récap seulement.

## Éléments cités

- B-0124@fe238ccb — le sujet de la revue adversariale, sorti de la
  répartition entre agents le 1er novembre, sur votre question.
- B-0055@5f053f9e — la répartition du travail entre plusieurs agents, qui
  prévoyait des relecteurs sans contexte, et qui attend la planification.
- D-0051@cea58730 — le plan de retrait de BMAD, que vous avez validé, qui a
  rangé les relecteurs sans contexte dans la répartition entre agents.

## Où regarder

- [B-0124](https://github.com/theodubus/memory/blob/c96c2046c8920544cda7a1efc737255514f399a5/memory/backlog/B-0124-une-revue-adversariale-par-un-relecteur-sans-conte.md) :
  le sujet, et ses deux critères de fin.
- [D-0051](https://github.com/theodubus/memory/blob/c96c2046c8920544cda7a1efc737255514f399a5/memory/requests/D-0051-valider-le-plan-de-retrait-de-bmad-ce-qui-part-les.md) :
  ce que le retrait de BMAD a gardé de ses relecteurs.
- [B-0055](https://github.com/theodubus/memory/blob/c96c2046c8920544cda7a1efc737255514f399a5/memory/backlog/B-0055-un-mode-multi-agent-un-agent-maitre-qui-tient-la-m.md) :
  la répartition entre agents, dont la revue sort.

Ce qu'il faut vérifier : que chaque question demande votre intention, et
non un choix que l'agent pourrait trancher seul.

## Options

- **Répondre** : quelques minutes, votre texte en un ou plusieurs messages,
  que l'agent consigne tel quel ; risque faible, la spécification suit ce
  que vous voulez ; réversible.
- **Valider les hypothèses** : effort nul ; risque, une hypothèse qui ne dit
  pas votre intention, notée « supposée », se corrige plus tard ; réversible.
- **Refuser** : effort nul ; risque, la revue attend, sans spécification ;
  réversible.

## Conséquences

Si vous répondez, l'agent consigne votre texte exact, puis écrit la
spécification ou la décision qui en découle, et vous la soumet dans une
demande. Si vous validez les hypothèses, il les applique, notées
« supposées ». Si vous refusez, le sujet attend. Si les questions ne se
comprennent pas (`contexte-insuffisant`), l'agent les réécrit. Sans
réponse, la revue attend aussi, et l'agent travaille sur autre chose.

## Recommandation

Valider les hypothèses si elles disent votre intention ; sinon répondre, même brièvement, à celles qui ne la disent pas. Vérifié : le principe est gardé (D-0051), et il ne demande pas d'agent maître. Supposé : tout ce que disent les hypothèses, en particulier que la revue trouve des défauts que les contrôles ratent, à mesurer au banc.

## Réponses possibles

- `valider` — les hypothèses de l'agent s'appliquent, notées « supposées ».
- `reponses` — le texte de votre réponse, en un ou plusieurs messages, donne les réponses ; l'agent le consigne tel quel.
- `refuser` — le sujet attend, sans spécification.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
