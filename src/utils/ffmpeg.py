# src/utils/ffmpeg.py - Gestion de FFmpeg. 

import os
import sys
from pathlib import Path


def get_application_base_path():
    """
    Retourne le répertoire de base de l'application.

    Fonctionne à la fois :
    - en développement ;
    - avec un exécutable PyInstaller.
    """

    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parent.parent.parent


def get_ffmpeg_directory():
    """
    Retourne le répertoire contenant FFmpeg.
    """

    base_path = get_application_base_path()

    return base_path / "ffmpeg-bin"


def configure_ffmpeg():
    """
    Ajoute le répertoire FFmpeg au PATH lorsque FFmpeg
    est fourni avec l'application.
    """

    ffmpeg_dir = get_ffmpeg_directory()

    if ffmpeg_dir.exists():
        current_path = os.environ.get("PATH", "")

        if str(ffmpeg_dir) not in current_path:
            os.environ["PATH"] = (
                str(ffmpeg_dir)
                + os.pathsep
                + current_path
            )


def get_ffmpeg_path():
    """
    Retourne le chemin vers ffmpeg.exe s'il est fourni
    avec l'application.

    Retourne None si aucun exécutable local n'est trouvé.
    """

    ffmpeg_dir = get_ffmpeg_directory()

    if sys.platform.startswith("win"):
        ffmpeg_path = ffmpeg_dir / "ffmpeg.exe"
    else:
        ffmpeg_path = ffmpeg_dir / "ffmpeg"

    if ffmpeg_path.exists():
        return ffmpeg_path

    return None