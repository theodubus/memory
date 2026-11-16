<!-- socle: couche=backlog zone=publique -->
# B-0245 — Le hook de l'agent ne suit pas les motifs d'un case : un cd sous un motif qui ne s'applique pas vaut pour la suite, et la suppression du projet y passe

> statut : abandonné · origine : J-2026-11-15-M · priorité : haute · ref : J-2026-11-16-G · lu : backlog@cc3fa160

Le découpage du hook de l'agent lit les commandes d'un `case` comme si
chacune s'exécutait : un `cd` sous un motif qui ne s'applique pas vaut
pour la suite, et une suppression qui suit se juge depuis un dossier où le
shell n'est pas. `case a in b) cd /usr;; esac; rm -rf ../projet`, lancé
depuis la racine d'un projet nommé `projet`, passe le hook : il juge
`/projet`, quand bash supprime la racine. B-0204 avait laissé les motifs
d'un `case` lus comme avant, parce que `protege.fichiers` rattrape
l'écriture d'un fichier protégé ; la suppression du projet, rien ne la
rattrape. Vu en menant B-0232 (J-2026-11-15-M) ; ADR-0080, sa première
conséquence, ouvre un sujet pour ce trou, de priorité haute comme B-0232.

La piste : ouvrir un `case` comme une condition (`OUVRANTS`, fermé par
`esac`), chaque motif comme une branche : ce qu'il change devient inconnu
après lui, sauf un dossier connu où il revient (`incertain`).

Abandonné le 16 novembre selon D-0120 (J-2026-11-16-G) : les motifs d'un `case`, qu'aucun agent n'écrit dans son travail, va à la liste des formes connues que le hook ne juge pas (B-0261).

## Satisfait quand

- [ ] `case a in b) cd /usr;; esac; rm -rf ../<nom de la racine>` est refusé par le hook, `case a in a) ls;; esac; rm -rf build` passe, et un test le montre
