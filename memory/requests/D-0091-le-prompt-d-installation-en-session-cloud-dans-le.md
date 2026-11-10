<!-- socle: couche=demandes zone=publique -->
# D-0091 — Le prompt d'installation en session cloud dans le README, et celui de mise à jour dans le guide

> date : 2026-11-10 · forme : séance

## Question posée

Le prompt d'installation dans le README : utile, le README dit qu'en session cloud l'agent fait tout, sans le texte à lui donner. Le plan : dans la section « Installation » du README, après le paragraphe de la session cloud, ce prompt ; et le prompt de mise à jour dans le guide, au même format.

    Installe le socle dans ce dépôt depuis son dépôt public, sans ajouter ce dépôt à la session :
    1. git clone --depth 1 https://github.com/theodubus/socle /tmp/socle
    2. Sur ta branche de travail, depuis la racine du dépôt : PYTHONPATH=/tmp/socle python3 -m socle install --target . --owner @<ton compte GitHub> --human <ton prénom> (ajoute --adoption si le projet a déjà du code).
    3. Suis les étapes « Et maintenant » de l'installeur, puis commite, pousse et ouvre la pull request.
    4. Dis-moi ce qui me revient : fusionner la pull request, protéger la branche par défaut. Le travail continuera dans une session neuve.

(c) le prompt du README : tu valides le texte ci-dessus, ou tu le corriges ?
