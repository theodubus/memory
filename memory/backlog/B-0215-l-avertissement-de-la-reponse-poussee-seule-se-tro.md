<!-- socle: couche=backlog zone=publique -->
# B-0215 — L'avertissement de la réponse poussée seule se trompe de base ou de nom : HEAD détaché, branche distante élaguée ou suivie ailleurs, push d'une autre branche, clé des seuils, nom de test trop courant, lien Markdown, plantage non protégé

> statut : ouvert · origine : J-2026-11-14-D · lu : backlog@12e5b66a

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

## Fait quand

- [ ] une clé des seuils est suivie comme un test, une exception du contrôle n'est qu'un avertissement, et un test le montre
