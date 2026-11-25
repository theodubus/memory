# L'organisation proportionnée : les règles nouvelles

Théo a retenu la réforme le 25 novembre (D-0194) et la suggestion 3 de
la revue de cap 6 (D-0193). Cette page dit les règles telles qu'elles
entreront dans le produit ; validée, elle s'applique dans L-0039, avec
T-0181 et T-0182, qui récrivent déjà les mêmes skills.

## Le principe

Chaque étape qui coûte (un sous-agent, une revue, une relecture à froid,
une demande, une passation) se déclenche sur ce qu'elle protège, jamais
sur la forme du travail. Ce qui est automatique ne change pas : les
contrôles, les hooks, la CI, la politique d'autonomie.

## 1. La session et le lot

- **Le lot regroupe ce qui se relit ensemble** : les tâches proches, qui
  touchent les mêmes fichiers, le même garde-fou ou les mêmes tests. Il
  se forme une fois, sur tout le backlog prêt du jalon, par thème ; une
  tâche ouverte plus tard rejoint le prochain lot dont la règle
  s'applique.
- **La session est l'unité de budget.** À la fin d'un lot, elle enchaîne
  le suivant si son coût estimé tient dans ce qui reste de la fenêtre de
  cinq heures et de la semaine, la marge de dix points du rangement
  comprise, et si sa conversation reste sous 300 000 jetons de contexte
  (au-delà, chaque appel coûte de plus en plus) ; sinon elle range et
  passe la main. La règle remplace « un lot par session » et le seuil
  fixe de 15 % de la fenêtre au départ d'une session programmée. La
  borne des deux lots sans message de l'humain reste.

## 2. Une conception à trancher

- **La question d'intention d'abord**, dans la conversation, en quelques
  lignes : le besoin tel que l'agent le comprend, le choix qui reste, sa
  recommandation. La réponse se consigne en séance.
- **Puis la spécification et le code dans le même lot**, la
  spécification écrite d'abord. Ce qui reste coûteux à défaire après la
  réponse va en demande, courte ; le reste, l'agent le décide et l'écrit
  en décision (politique, point 3).

## 3. La revue

- **Une revue adversariale, par un relecteur sans contexte, quand le lot
  la justifie** : il pose ou change un garde-fou (un contrôle, un refus,
  un hook), un format que d'autres parties lisent (la mémoire, le
  contrat des adaptateurs, la CI posée), ou plus de 150 lignes de code
  et de tests. Sinon, l'agent relit son diff contre les critères de ses
  tâches, et le récap le dit.
- **Une passe** ; une seconde seulement si la correction d'un bloquant
  change la conception d'une partie.
- **Une spécification, de la documentation ou de la mémoire seules**
  n'ont pas de revue adversariale : c'est l'humain qui en juge
  l'intention.
- Le tri des constats ne change pas (bloquant, backlog, écarté).

## 4. Les sous-agents

- **Un sous-agent implémente quand il paie** : des tâches indépendantes
  qui avancent en parallèle, ou une tâche dont la lecture saturerait la
  conversation qui orchestre (plus de 400 lignes changées, ou des
  fichiers longs à lire). Sinon, l'agent qui orchestre implémente.
- **Chaque sous-agent nomme ses fichiers temporaires de l'identifiant de
  sa tâche** ; **un sous-agent arrêté** (une vérification en
  arrière-plan dont il n'a pas repris le fil) se reprend depuis sa copie
  isolée, par l'agent qui orchestre (D-0193).
- **La relecture à froid d'une demande**, seulement pour une demande qui
  passe la moitié de son budget ; une demande courte, ou qui ne fait
  qu'approuver des fichiers protégés par leurs empreintes, part sans
  elle.

## 5. Le ménage

Dans la même tâche, chaque skill d'organisation du produit
(`socle-batch`, `socle-review`, `socle-request`, `socle-handoff`,
`socle-resume`), la section du socle du gabarit d'`AGENTS.md`, le guide
et le skill `delegate-lot` d'ici se relisent : une règle qui ne protège
rien de vu en usage se retire, et le récap dit chacune avec sa raison.
Les tests qui lisent ces textes changent sous la demande qui remet les
copies protégées : une seule validation de Théo pour tout L-0039.

## Ce qui ne change pas

La politique d'autonomie ; les décisions qui reviennent à l'humain ; la
revue du code qui touche un garde-fou ; le tri des constats ; les
contrôles et la CI ; le hook de l'agent (ADR-0098).
