# src/utils/files.py - Utilitaires liés à la gestion des fichiers.


import os
import shutil
import tempfile
from pathlib import Path


def get_temp_dir():
    """
    Crée un répertoire temporaire et retourne son chemin.
    """
    return tempfile.mkdtemp()


def cleanup_temp_dir(temp_dir):
    """
    Supprime un répertoire temporaire et son contenu.
    """
    if not temp_dir:
        return

    temp_path = Path(temp_dir)

    if not temp_path.exists():
        return

    try:
        shutil.rmtree(temp_path)
    except OSError:
        pass


def ensure_directory(directory):
    """
    Crée un répertoire s'il n'existe pas.

    Retourne le chemin sous forme de Path.
    """
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    return directory


def get_filename_without_extension(filepath):
    """
    Retourne le nom du fichier sans son extension.
    """
    return Path(filepath).stem


def get_file_extension(filepath):
    """
    Retourne l'extension du fichier en minuscules.
    """
    return Path(filepath).suffix.lower()


def file_exists(filepath):
    """
    Vérifie qu'un fichier existe.
    """
    return Path(filepath).is_file()


def get_output_path(input_path, output_dir, extension):
    """
    Construit le chemin du fichier de sortie.

    Exemple :
        input : entretien.mp4
        output : /resultats
        extension : wav

        => /resultats/entretien.wav
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)

    extension = extension.lstrip(".")

    return output_dir / f"{input_path.stem}.{extension}"
