<!-- socle: couche=demandes zone=publique -->
# D-0024 — Refuser ou seulement signaler un commit d'agent fait sans hooks de l'agent depuis le commit précédent

> date : 2026-10-14 · lu : decisions@efc2a4a3

## Décision demandée

Choisir ce que fait la CI quand un commit d'agent montre qu'aucun hook de
l'agent n'a tiré depuis le commit précédent de sa session : le refuser, ou
seulement le signaler.

## Contexte

Chaque commit d'un agent porte une ligne qui compte les passages des hooks
de l'agent (le filtre de ses commandes, les contrôles de fin de tour), et
la CI refuse un commit dont le compte est à zéro : c'est la preuve que ces
hooks étaient chargés. Mais le compte couvre toute la session, depuis son
début. Cette session-ci l'a montré : depuis sa reprise, ouverte au-dessus
du dépôt, ses hooks ne se chargent plus, et ses commits affichent pourtant
encore 2186 passages, tous d'avant la reprise. La CI n'a rien vu.

La correction est prête à écrire et ne change aucun test existant :
compter aussi les passages depuis le commit précédent, dans une seconde
ligne du commit, que la CI lit. Un commit d'agent en compte toujours au
moins un quand ses hooks marchent, puisque la commande qui commite passe
elle-même par le filtre.

Reste la sévérité. Refuser, c'est la règle de la trace jusqu'ici ; mais
alors, tant que cette session reste ouverte au-dessus du dépôt, chacun de
mes commits sera refusé par la CI, celui de la correction compris : je ne
pourrais plus pousser de travail vert d'ici, et il faudrait ouvrir une
session neuve sur le dépôt seul. Signaler laisse passer, avec un
avertissement dans la CI et au commit.

## Éléments cités

- **Le sujet de ce défaut** (B-0058@c394a6cc) : le constat fait dans cette
  session, et la correction proposée.
- **La trace des hooks dans les commits** (ADR-0005@fc835669) : la
  décision qui la fait voyager dans chaque commit d'agent, pour que la CI
  vérifie que les hooks de l'agent ont tiré pendant la session.

## Où regarder

- [le sujet du défaut](https://github.com/theodubus/memory/blob/19c4b755da90c52139b1af9822671b8fc24bb568/memory/backlog/B-0058-la-trace-des-hooks-compte-toute-la-session-des-hoo.md) :
  le constat et la correction.
- [le contrôle de la trace](https://github.com/theodubus/memory/blob/19c4b755da90c52139b1af9822671b8fc24bb568/engine/socle/checks_ratchet.py#L332-L353) :
  ce que la CI refuse aujourd'hui, un compte à zéro sur toute la session.

## Options

- **Refuser** : un commit d'agent sans aucun passage depuis le commit
  précédent est refusé par la CI, comme un compte à zéro aujourd'hui.
  Effort faible ; risque faible pour les projets ; pour cette session,
  plus aucun commit vert tant qu'elle reste ouverte au-dessus du dépôt ;
  réversible.
- **Signaler** : le même cas donne un avertissement, dans la CI et au
  commit, sans refuser. Effort faible ; risque moyen : un agent dont les
  hooks ont cessé de tirer continue sans que rien ne l'arrête ;
  réversible.
- **Refuser, après une session neuve** : j'écris la correction en
  « refuser » ; tu ouvres la prochaine session sur le dépôt seul, et elle
  la commite. Effort : une session à rouvrir ; risque faible ;
  réversible.

## Conséquences

- Si tu valides « refuser » : j'écris la correction et je la commite ;
  la CI de ce commit et des suivants sera rouge tant que la session reste
  ouverte au-dessus du dépôt, et je m'arrête de pousser d'ici.
- Si tu choisis « signaler » : j'écris la correction en avertissement,
  et je continue de travailler dans cette session.
- Si tu choisis « refuser après une session neuve » : je laisse la
  correction au chantier actif, et la session suivante l'écrit et la
  commite.
- Si tu refuses tout : la trace reste telle quelle, et B-0058 se clôt
  sans correction.
- Sans réponse : rien ne change ; je travaille sur les deux autres sujets du tri du backlog.

## Recommandation

Refuser après une session neuve : la trace n'a de valeur que si elle
arrête un agent dont les hooks ne tournent plus, et une session ouverte
sur le dépôt seul les recharge. Vérifié : les hooks de l'agent ne tirent
plus depuis le 12 oct. au soir, et la session démarre au-dessus du dépôt,
où se trouvent aussi les copies du projet d'échecs. Supposé : qu'une
session ouverte sur le seul dépôt `memory` démarre dans son dossier, et
recharge donc ses hooks.

## Réponses possibles

- `refuser` — la CI refuse ; je commite la correction d'ici, et la CI de cette session devient rouge.
- `signaler` — la CI avertit sans refuser ; je continue d'ici.
- `refuser-session-neuve` — la CI refusera ; la correction s'écrit dans une session neuve, ouverte sur le dépôt seul.
- `rien` — la trace reste telle quelle, et le sujet se clôt.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
