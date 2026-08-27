# src/services/video_converter.py - Services de conversion vidéo.

from pathlib import Path
import shutil
from typing import Callable
from moviepy import VideoFileClip
from pydub import AudioSegment

from src.utils.files import (
    get_temp_dir, cleanup_temp_dir, ensure_directory, get_output_path,
)


def is_video_file(filepath):
    """
    Vérifie si un fichier contient réellement une piste vidéo.

    Retourne True si une piste vidéo est présente.
    """
    clip = None

    try:
        clip = VideoFileClip(str(filepath))
        return clip.reader.nframes > 0

    except Exception:
        return False

    finally:
        if clip is not None:
            try:
                clip.close()
            except Exception:
                pass


def convert_video_to_audio(
    video_path: str | Path,
    output_dir: str | Path,
    audio_format: str = "wav",
    progress_callback: Callable[[int], None] | None = None,
)-> Path:
    """
    Extrait la piste audio d'une vidéo.

    Parameters
    ----------
    video_path : Chemin de la vidéo.
    output_dir : Dossier de sortie.
    audio_format : Format audio souhaité.
    
    progress_callback : callable, optional
        Fonction appelée avec un pourcentage de progression.

    Returns
    -------
    Path :Chemin du fichier audio généré.
    """

    video_path = Path(video_path)
    output_dir = ensure_directory(output_dir)

    if not video_path.is_file():
        raise FileNotFoundError(
            f"Le fichier vidéo n'existe pas : {video_path}"
        )

    output_path = get_output_path(
        video_path,
        output_dir,
        audio_format,
    )

    temp_dir = get_temp_dir()
    video = None
    temp_wav_path = None

    try:
        video = VideoFileClip(str(video_path))

        if video.audio is None:
            raise ValueError(
                f"La vidéo '{video_path.name}' "
                "ne contient pas de piste audio."
            )

        temp_wav_path = (Path(temp_dir) / f"{video_path.stem}_temp.wav")
        video.audio.write_audiofile(str(temp_wav_path), codec="pcm_s16le", 
                                    logger=None,)

        if progress_callback:
            progress_callback(50)

        if audio_format.lower() == "wav":
            shutil.move(str(temp_wav_path), str(output_path),)
            temp_wav_path = None

        else:

            audio = AudioSegment.from_wav(
                str(temp_wav_path)
            )

            audio.export(
                str(output_path),
                format=audio_format.lower(),
            )

        if progress_callback:
            progress_callback(100)

        return output_path

    finally:

        if video is not None:
            try:
                video.close()
            except Exception:
                pass

        cleanup_temp_dir(temp_dir)

    