<!-- socle: couche=decisions zone=publique -->
# ADR-0004 — Une validation humaine est une réponse ajoutée qui cite ce qu'elle valide

> statut : acceptée · date : 2026-10-10 · source : J-2026-10-10-B

## Contexte

Plusieurs règles du cadrage exigent une validation humaine : assouplir un
garde-fou, changer une valeur attendue, modifier la politique ou un fichier
protégé, écrire le statut « validé ». La CI doit pouvoir le vérifier par
script.

## Décision

Une validation est une réponse `valider` à une demande, dans un fichier
`<demande>.reponse.toml` que seul l'humain écrit (`socle answer`, refusé à
l'agent par son hook). Elle ne couvre un changement que si elle est ajoutée
dans la plage contrôlée et si la demande cite ce qui change : la clé
assouplie, le nom du test, ou le chemin et l'empreinte du fichier protégé.
Pour un changement qu'il fait lui-même, l'humain écrit demande et réponse
d'un geste (`socle approve`).

## Conséquences

- Une vieille validation ne couvre pas un assouplissement nouveau.
- La réponse porte l'empreinte du texte de la demande : celle-ci est gelée.
- Limite assumée : un agent qui détient les droits de l'humain pourrait
  écrire une réponse en passant outre son hook. La parade est hors du dépôt :
  CODEOWNERS et branche protégée (voir la demande sur la protection de
  branche).
- Réversible : le mécanisme vit dans le moteur et l'auto-test l'éprouve.
