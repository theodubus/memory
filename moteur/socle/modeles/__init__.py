"""Gabarits que l'installeur pose dans un projet."""

from pathlib import Path

DOSSIER = Path(__file__).resolve().parent


def gabarit(nom: str) -> str:
    return (DOSSIER / nom).read_text(encoding="utf-8")
