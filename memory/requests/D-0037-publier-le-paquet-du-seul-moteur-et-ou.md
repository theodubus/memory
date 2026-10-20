<!-- socle: couche=demandes zone=publique -->
# D-0037 — Publier le paquet du seul moteur, et où

> date : 2026-10-20 · lu : decisions@2a93e7ab

## Décision demandée

Choisir comment l'utilisateur installe le seul moteur, sans cloner ce
dépôt : par pip depuis GitHub, sans rien publier ; en publiant un paquet
sur PyPI ; ou en joignant une archive du moteur à chaque version.

## Contexte

Tu as validé la séparation du produit et de l'atelier : l'utilisateur
n'installe que le moteur (`engine/socle/`), jamais les tests, les bancs ni
la mémoire de ce dépôt. Aujourd'hui, la documentation lui fait faire un
clone partiel qui ne télécharge que le moteur (environ 2 Mo), puis lancer
l'installeur par `PYTHONPATH` : deux commandes de git avant la sienne, et
une variable d'environnement. Un paquet ferait de l'installation une
commande, et donnerait la commande `socle` partout.

J'ai essayé, dans un dossier jetable, de rendre le moteur installable par
pip : un fichier de description du paquet dans `engine/` suffit (le nom,
la version, la commande `socle`, les gabarits et adaptateurs joints). Le
moteur installé ainsi a équipé un projet Python jetable, et l'installation
a fini verte. Le moteur lui-même reste sans dépendance : seule la
construction du paquet, au moment de l'installation, emploie l'outil
standard de construction de Python, que pip va chercher.

Le nom `socle` est déjà pris sur PyPI, par un autre projet (version 0.7,
dépôt `v6sa/socle`) ; `socle-agent` et `socle-memory` sont libres ce jour.

## Éléments cités

- B-0042@d51e8ba3 — le sujet du backlog : installer le socle sans clone,
  par un paquet ; une publication externe que tu avais mise à part.
- ADR-0033@ef7d0d5b — la séparation du produit et de l'atelier, que tu as
  validée : l'utilisateur n'installe que le produit.
- ADR-0001@9959255a — le moteur n'emploie que la bibliothèque standard de
  Python 3.11+ ; un paquet n'y change rien à l'exécution.

## Où regarder

- [le README](https://github.com/theodubus/memory/blob/c25340d31f98b31a233503b4b0ad0d845f33d6fb/README.md), section « Installer » : l'installation
  d'aujourd'hui, par un clone partiel ; c'est elle qu'une option ci-dessous
  remplace.
- [le sujet B-0042](https://github.com/theodubus/memory/blob/c25340d31f98b31a233503b4b0ad0d845f33d6fb/memory/backlog/B-0042-installer-le-socle-sans-clone-un-paquet-installabl.md) :
  ce qui était demandé.

## Options

- **pip depuis GitHub, sans publication** : j'ajoute la description du
  paquet dans `engine/` ; l'installation devient
  `pip install "git+https://github.com/theodubus/memory#subdirectory=engine"`,
  puis `socle install --target . --owner @toi`. Rien n'est publié ; pip
  clone le dépôt lui-même, mais n'installe que le moteur. Effort : une
  heure, tests et doc compris. Risque faible. Réversible : un commit.
- **PyPI** : la même chose, puis un paquet publié sous un nom libre
  (`socle-agent`) ; l'installation devient `pipx install socle-agent`.
  C'est une publication : ton compte PyPI, un jeton ou une publication de
  confiance depuis GitHub, et c'est toi qui publies (le hook me refuse
  toute publication). Effort : deux heures, plus ton compte. Risque moyen :
  un nom et une version publiés ne se reprennent pas. Peu réversible.
- **Une archive par version** : une version marquée sur la branche par
  défaut, avec l'archive du seul moteur jointe ; il faut d'abord fusionner
  ce travail dans `main`. Effort : une heure, plus ta fusion. Risque
  faible. Une version publiée se retire, mais d'autres ont pu la prendre.
- **Rien** : le clone partiel reste. Effort nul.

## Conséquences

- Si tu valides pip depuis GitHub : je le fais, avec ses tests et la doc,
  puis le projet pilote s'installe ainsi.
- Si tu valides PyPI : je fais d'abord l'option pip, puis je te prépare la
  publication, commande par commande, au backlog `pour : humain`.
- Si tu valides l'archive : je prépare l'archive et ce qu'il faut pour la
  version ; la fusion et la publication restent à toi.
- Si tu refuses (`rien`) : la documentation garde le clone partiel, qui
  marche aujourd'hui ; je passe au projet pilote.
- Sans réponse : rien n'est publié ni ajouté ; je passe au projet pilote
  avec le clone partiel.

## Recommandation

pip depuis GitHub maintenant, PyPI plus tard, une fois le projet pilote
passé et la version stable. Vérifié : le moteur s'installe par pip et équipe
un projet jetable ; `socle` est pris sur PyPI et `socle-agent` libre ce
jour. Supposé : que pip installe depuis un sous-dossier de dépôt sur les
machines de tes utilisateurs comme ici (pip 24 et plus récent) ; l'essai
s'est fait depuis un dossier local, pas depuis GitHub.

## Réponses possibles

- `pip-github` — j'ajoute le paquet installable par pip depuis GitHub, sans rien publier.
- `pypi` — l'option pip, puis la publication sur PyPI sous `socle-agent`, que tu fais.
- `archive` — une archive du seul moteur jointe à chaque version.
- `rien` — le clone partiel reste.
- `contexte-insuffisant` — la demande revient à l'agent, qui la réécrit en une demande qui la remplace.
