# Mise à jour du socle sur chess, 26 novembre 2026 : faite, et ce qu'elle a montré

Le retour de la session de chess, recopié par Théo dans la session du
socle, tel quel. La session a suivi le prompt de
`docs/fabrication/chess/prompt-mise-a-jour.md`, récrit par thème le
26 novembre (T-0186), avec la version publiée du socle de ce jour.

```text
Retour de chess sur la mise à jour du 26 nov. 2026 :
1. Après une mise à jour qui migre le backlog, les hooks avant commit et avant push refusent de commiter puis de pousser la demande seule : ils jugent l'index (backlog à l'ancien format, ancien chantier actif) avec le moteur neuf de l'arbre de travail (memoire.formes sur chaque « Fait quand », memoire.budgets sur active.md). Contourné par git stash --include-untracked, git commit --only, push, git stash pop. Et git stash --keep-index garde dans l'index les renommages que l'installeur a déjà faits par git mv.
2. L'installeur dit « !! aucun propriétaire (--owner) : CODEOWNERS non posé — la politique n'est protégée que par la CI », alors que .github/CODEOWNERS existe et est protégé.
3. La politique protège .github/workflows/socle-mutation.yml, absent de chess : attendu ?
4. tests.regression prend un commit de mémoire intitulé « Correction : … » pour un correctif (motif (?i)^(fix|corrige|correctif|correction)\b) et exige un test ; la seule issue est une demande, ou réécrire l'historique.
5. La fin de tour a pris le nom de la commande prune-branches, cité entre accents graves dans « Pour toi », pour une branche à supprimer absente de l'origine.
6. Le prompt de mise à jour disait la liste [adoption] warn_only de chess non vide : elle est vide (« rien à inscrire »).
7. La copie remplacée n'ayant pas de CHANGES.md, l'installeur a imprimé les 122 notes en entier (~100 Ko).
Ce qui a marché : le démarrage tient (état à 5 665 octets, sans « !! coupé ») ; l'auto-test du socle passe en CI, sans la course du 23 nov.
```

## Ce que le socle en a fait

Le tri, par `docs/fabrication/but-et-tri.md`, le 26 novembre
(J-2026-11-26-AA) :

| Gêne | Suite |
| --- | --- |
| 1. La demande seule, refusée par les hooks avant commit et avant push | B-0357 |
| 2. CODEOWNERS dit non posé alors qu'il existe | B-0358 |
| 3. `socle-mutation.yml` protégé, absent de chess | écartée : attendu, sans effet |
| 4. Un commit de mémoire « Correction : … » jugé correctif | B-0359 |
| 5. Le nom d'une commande pris pour une branche à supprimer | B-0360 |
| 6. Le prompt disait `warn_only` non vide | écartée : l'atelier seul |
| 7. Les 122 notes imprimées en entier | B-0361 |

La gêne 3 : la politique protège ce chemin dans tout projet, que
l'installeur y pose le balayage ou non ; chez chess, son propre
workflow lance déjà le balayage, et l'installeur n'en pose pas un
second. Protégé et absent, le chemin ne gêne aucun contrôle : il empêche
seulement l'agent d'y écrire lui-même un balayage. Rien ne change.

La gêne 6 : une phrase fausse du prompt, que le compte rendu du
13 novembre démentait déjà (« Le lot fusionné juste avant avait déjà
corrigé les quatre constats et vidé warn_only ») ; elle ne change rien à
ce que reçoit un projet (X4). Le prompt repart de cette mise à jour pour
la suivante.
