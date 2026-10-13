<!-- socle: couche=backlog zone=publique -->
# B-0027 — Sans adresse de dépôt, l'agent ne sait pas quel lien mettre dans une demande

> statut : ouvert · origine : J-2026-10-11-G · lu : backlog@3cbd3c76

Au banc, huit premiers jets de demande sur onze ont été refusés pour « Où
regarder » sans lien (s4, s5, s9, s11) : sans `[human] repo_url` ni push, `socle
url` échoue, et l'agent écrit des chemins nus. Un lien relatif depuis la
demande (`../../calc.py`) passe le contrat ; le refus, ou le squelette de
`socle new request`, devrait le dire.
