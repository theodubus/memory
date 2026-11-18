<!-- socle: couche=backlog zone=publique -->
# B-0227 — Le hook refuse de remettre en état un fichier protégé dont une demande ne cite que le dossier, dans une valeur recopiée

> statut : ouvert · origine : J-2026-11-14-Z · lu : backlog@90b4b5a0

Relevé le 14 novembre (J-2026-11-14-Z). Après une mise à jour par
l'installeur, la remise en état d'un fichier protégé qu'il a changé sans
qu'aucune demande ne le couvre (D-0098) est refusée quand une demande en
attente, ou validée sans sa réponse dans `HEAD`, cite un dossier qui le
contient. D-0114 recopie une valeur attendue d'un test, « skills du
socle posés dans .claude/skills : … » : `_cite_chemin` (dans
`engine/socle/hooks.py`) y lit le dossier `.claude/skills`, donc les
copies de `socle-resume` et de `socle-review`, que la demande n'approuve
pas. Usage normal : une demande qui porte sur un skill du socle cite
souvent ce dossier. L'effet est rattrapé, puisque la remise passe une
fois la réponse commitée ; mais l'agent doit d'abord commiter en
laissant ces fichiers changés hors du commit.

Piste : ne compter pour citation d'un dossier que les lignes de fichiers
approuvés des « Éléments cités », ou un chemin qui n'est pas dans un
texte recopié entre accents graves.

## Satisfait quand

- [ ] après une mise à jour, l'agent remet en état un fichier protégé qu'aucune demande n'approuve sans attendre la réponse d'une demande qui ne cite son dossier que dans un texte recopié
