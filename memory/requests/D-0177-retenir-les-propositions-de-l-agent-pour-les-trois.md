<!-- socle: couche=demandes zone=publique -->
# D-0177 — Retenir les propositions de l'agent pour les trois points de B-0346 : la tête de la garde, la passation reprise, « reprends » sans passation ?

> date : 2026-11-24 · forme : séance

## Question posée

Les trois points de B-0346, « reprends » seul, la passation écrite dans le dépôt ; propositions de l'agent :
- Quelle tête la garde nomme. La passation devient un fichier du dépôt, sans identifiant de commit. La garde prend pour tête le dernier commit qui a écrit ce fichier, et pour heure la date de ce commit. Si la session qui part pousse encore quelque chose, elle réécrit sa passation dans le même commit, et rien ne se périme.
- Qui la marque reprise. La session neuve, une fois sa garde acceptée, retire la passation dans son premier commit, poussé aussitôt. Une autre session ouverte ensuite n'en trouve plus, ou voit la branche bouger et s'arrête.
- « reprends » sans passation. La session fait ce que fait aujourd'hui une session neuve : l'état, le chantier actif, le prochain lot. Son premier message dit qu'aucune passation n'attendait.
