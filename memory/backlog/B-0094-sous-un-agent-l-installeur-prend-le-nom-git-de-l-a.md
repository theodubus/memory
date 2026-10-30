<!-- socle: couche=backlog zone=publique -->
# B-0094 — Sous un agent, l'installeur prend le nom git de l'agent pour celui de l'humain

> statut : ouvert · origine : J-2026-10-30-B · lu : backlog@6da5822d

L'installeur nomme l'humain dans la politique d'un projet neuf d'après
`git config user.name` (B-0073) : c'est lui qui signe les réponses que
l'agent relaie. Mais quand l'agent lance l'installation, en session cloud,
l'identité git du conteneur est celle de l'agent : « Claude »,
noreply@anthropic.com. La politique du pilote nomme ainsi l'humain
« Claude », et ses réponses seraient signées du nom de l'agent. La
politique est protégée : seul l'humain peut la corriger.

Sous un agent (`CLAUDECODE`), l'installeur ne prend pas le nom git ; une
option `--human <nom>` le donne, et sans elle les étapes qui suivent
l'installation demandent à l'humain d'écrire son nom dans la politique.
