"""Le mode compagnon mis en place d'un geste (B-0034, P5) :
`socle private install`, réservé à l'humain. Séparé de `prive`, qui lit et
contrôle la zone privée (L7)."""

from __future__ import annotations

from pathlib import Path

from socle import config, utils as outils
from socle.private import adresse_ssh, commit_compagnon, depot_compagnon, dossier, ecrire_verrou, fichier_verrou, mode


def installer_compagnon(projet: config.Projet, adresse: str) -> tuple[int, list[str]]:
    """Le mode compagnon mis en place d'un geste (B-0034, P5) : le dépôt privé
    cloné, son premier commit poussé s'il est vide, le verrou écrit, une clé
    de déploiement créée ; puis ce qui reste à faire sur GitHub, avec les
    liens. Réservé à l'humain : il pousse vers le dépôt privé et crée une clé."""
    import shutil
    import subprocess

    from socle import links as liens

    racine = projet.racine
    if mode(projet) != "compagnon":
        return 1, ["refus : la politique ne choisit pas le mode compagnon — relancer l'installation avec "
                   "`--private compagnon`, qui l'écrit"]
    rel = dossier(racine)
    zone = racine / rel
    res = []
    if depot_compagnon(racine) is None:
        if zone.exists() and any(zone.iterdir()):
            return 1, [f"refus : {rel}/ existe et n'est pas un clone : le déplacer, puis relancer"]
        r = subprocess.run(["git", "clone", "-q", adresse, str(zone)], cwd=racine, capture_output=True, text=True)
        if r.returncode != 0:
            return 1, [f"refus : clone impossible ({r.stderr.strip()[-300:] or 'git clone a échoué'})"]
        res.append(f"dépôt privé cloné dans {rel}/")
    else:
        res.append(f"dépôt privé déjà cloné dans {rel}/")
    if outils.ajouter_lignes(racine / ".gitignore", [f"{rel}/"], "# Le clone du dépôt privé (mémoire privée)"):
        res.append(f"{rel}/ ignoré par le dépôt public (.gitignore)")
    if not outils.a_des_commits(zone):
        (zone / "README.md").write_text(
            f"# Mémoire privée de {racine.name}\n\nLe socle y range la mémoire privée du projet, au même format que "
            "la mémoire publique. Ce dépôt reste privé.\n", encoding="utf-8")
        for args in (["add", "README.md"], ["commit", "-q", "-m", "Mémoire privée : premier commit"]):
            r = subprocess.run(["git", *args], cwd=zone, capture_output=True, text=True)
            if r.returncode != 0:
                return 1, res + [f"refus : premier commit du dépôt privé impossible ({r.stderr.strip()[-300:]})"]
        res.append("premier commit du dépôt privé")
    sha = commit_compagnon(racine)
    # La CI clone le dépôt privé au commit du verrou : il doit y être poussé.
    r = subprocess.run(["git", "push", "-q", "-u", "origin", "HEAD"], cwd=zone, capture_output=True, text=True)
    if r.returncode != 0:
        res.append(f"!! dépôt privé non poussé ({r.stderr.strip()[-200:]}) : le pousser, sans quoi la CI ne "
                   "trouvera pas le commit du verrou")
    else:
        res.append("dépôt privé poussé")
    ecrire_verrou(racine, sha)
    res.append(f"verrou : {sha[:10]} ({fichier_verrou(racine)})")

    cle = config.chemin_trace(racine).parent / "prive-deploiement"
    if not cle.is_file():
        cle.parent.mkdir(parents=True, exist_ok=True)
        if shutil.which("ssh-keygen"):
            r = subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", f"socle CI {racine.name}",
                                "-f", str(cle)], capture_output=True, text=True)
            if r.returncode != 0:
                res.append(f"!! clé de déploiement non créée ({r.stderr.strip()[-200:]})")
        else:
            res.append(f"!! ssh-keygen absent : créer la clé à la main, `ssh-keygen -t ed25519 -N \"\" -f {cle}`")
    if cle.is_file():
        res.append(f"clé de déploiement : {cle} (hors du dépôt, jamais commitée)")

    res += [""] + gestes_github(adresse, liens.url_depot(projet), cle)
    res += ["", "Ensuite :",
            f"  - effacer la clé privée une fois le secret posé : rm {cle}",
            f"  - commiter puis pousser : git add {fichier_verrou(racine)} .gitignore && "
            "git commit -m \"Mémoire privée : le dépôt compagnon\" && git push"]
    return 0, res


def gestes_github(adresse: str, web_public: str | None, cle: Path) -> list[str]:
    """Les deux gestes qui restent à l'humain sur GitHub, avec les liens des
    pages où les faire quand les dépôts y sont, et les commandes `gh`."""
    from socle import links as liens

    ssh = adresse_ssh(adresse)
    web_prive = liens.depuis_distant(adresse)
    github = (web_prive or "").startswith("https://github.com/")
    res = ["Sur GitHub, deux gestes :",
           "  1. la clé publique en clé de déploiement du dépôt privé, en lecture seule"
           + (f" : {web_prive}/settings/keys/new" if github else ""),
           f"     (le contenu de {cle}.pub)",
           "  2. deux secrets du dépôt public" + (f" : {web_public}/settings/secrets/actions/new"
                                                  if web_public and github else ""),
           f"     SOCLE_PRIVE_DEPOT = {ssh}",
           f"     SOCLE_PRIVE_CLE   = le contenu de {cle}"]
    if github:
        depot = web_prive.removeprefix("https://github.com/")
        res += ["  Ou, avec gh :",
                f"     gh repo deploy-key add {cle}.pub --repo {depot} --title \"socle CI\"",
                f"     gh secret set SOCLE_PRIVE_DEPOT --body \"{ssh}\"",
                f"     gh secret set SOCLE_PRIVE_CLE < {cle}"]
    return res
