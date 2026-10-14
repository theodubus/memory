<!-- socle: couche=decisions zone=publique -->
# ADR-0005 — La trace des hooks de l'agent voyage dans les commits

> statut : acceptée · date : 2026-10-10 · source : J-2026-10-10-B

## Contexte

Le cadrage demande que la CI vérifie que les hooks de l'agent ont tiré
pendant la session. Dans `chess`, la trace (`chess:.claude/hooks-fired.log`) est
ignorée par git : la CI ne peut pas la lire.

## Décision

Chaque hook écrit une ligne dans `.socle/trace/hooks.log`, non versionné. Le
hook git `prepare-commit-msg`, sur un commit fait dans une session d'agent
(`CLAUDECODE` dans l'environnement), ajoute les trailers `Socle-Agent` et
`Socle-Hooks: SessionStart=… PreToolUse=… Stop=…`, comptés sur la session la
plus récente de la trace. La CI exige, sur tout commit d'agent fait après
l'installation, un `Socle-Hooks` avec au moins un `PreToolUse`, et un
`SessionStart` non nul ou `installation` (socle installé pendant la session).

## Conséquences

- Hooks de l'agent jamais chargés, ou hooks git absents : la CI le voit.
- Un commit d'agent se reconnaît à ses trailers (`Co-Authored-By: Claude`) ;
  un agent qui n'en met pas échappe à ce contrôle, pas aux autres.
- Réversible et éprouvé par l'auto-test (défaut « hook jamais tiré » et son
  témoin).
