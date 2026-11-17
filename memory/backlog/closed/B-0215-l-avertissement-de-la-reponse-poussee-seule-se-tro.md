<!-- socle: couche=backlog zone=publique -->
# B-0215 — L'avertissement de la réponse poussée seule se trompe de base ou de nom : HEAD détaché, branche distante élaguée ou suivie ailleurs, push d'une autre branche, clé des seuils, nom de test trop courant, lien Markdown, plantage non protégé

> statut : fait · origine : J-2026-11-14-D · lu : backlog@12e5b66a · ref : J-2026-11-14-O

La revue de B-0142 (J-2026-11-14-D), constats 1, 2, 4, 5 et 6 : le
contrôle `demandes.reponse-seule`, un avertissement, se trompe dans des cas
hors de son modèle de menace.

- `utils.base_non_poussee` dit « pas encore poussée » d'une réponse déjà
  poussée : HEAD détaché ; branche distante supprimée puis élaguée ;
  branche qui suit `origin/main` plutôt que son homonyme ; push qui
  n'envoie pas HEAD (`git push origin main` depuis une autre branche, des
  étiquettes seules). Piste : `HEAD --not --remotes=origin`, ou le sha
  distant que le hook avant push reçoit.
- Une clé des seuils, que seule `valider` autorise aussi (D-0040), n'est
  pas suivie : `cliquet.garde-fous` refuse de même au push suivant.
- Un test nommé par sa description (`it('double')`) ou un identifiant nu
  fait avertir à tort quand la demande emploie ce mot ; un test nouveau
  que la demande nomme fait taire l'avertissement.
- Un fichier protégé cité par un lien Markdown sur la ligne de son
  empreinte est écarté, alors que `protege.fichiers` l'accepte.
- Une exception du contrôle deviendrait une erreur qui refuse le commit
  ou le push ; rien ne la protège.

Écartés le 14 novembre, sur la décision de Théo (D-0111, J-2026-11-14-L),
comme cas exotiques d'un simple avertissement : la base non poussée dans
les quatre cas de git (HEAD détaché, branche élaguée ou suivie ailleurs,
push d'une autre branche), le test nommé par sa description, le lien
Markdown. Restent, parce qu'ils se produisent dans l'usage normal : la clé
des seuils, le scénario même de B-0142, et l'exception non protégée, qui
refuserait un commit.

## Modèle de menace

Le garde-fou reste un avertissement (ADR-0076, qui remplace ADR-0074) ;
la rigueur de `cliquet.garde-fous`, de `tests.attendus` et de
`protege.fichiers` ne change pas.

Ce qu'il arrête, en plus : l'agent distrait qui pousse seule la réponse
`valider` d'une demande qui cite une clé des garde-fous à relâcher, la
clé citable en toutes lettres comme le cliquet la cherche (D-0040), sans
la plage qui la change ; et le commit, le push ou la fin de tour qu'un
contrôle en panne refuserait : une exception levée dans
`demandes.reponse-seule` devient un avertissement qui la nomme.

Ce qu'il laisse passer : une clé que la demande nomme autrement que
sous sa forme citable, ou qui n'existe ni avant ni après et que les
règles du cliquet ne nomment que par un motif (le plafond de mutation
d'un module neuf) ; les cas que D-0111 écarte. Une demande qui cite une
clé en passant, sans la relâcher, fait avertir à tort tant que rien de ce
qu'elle nomme ne change.

## Satisfait quand

- [x] une clé des seuils est suivie comme un test, une exception du contrôle n'est qu'un avertissement, et un test le montre
