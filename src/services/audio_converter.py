# src/services/audio_converter.py - Services de conversion audio.


from pathlib import Path

from moviepy import AudioFileClip
from pydub import AudioSegment

from src.services.video_converter import is_video_file
from src.utils.files import (get_temp_dir, cleanup_temp_dir,
                              ensure_directory, get_output_path,)


def convert_audio_format(
    audio_path,
    output_dir,
    output_format,
    progress_callback=None,
):
    """
    Convertit un fichier audio vers un autre format.

    Les fichiers MP4 contenant uniquement de l'audio
    sont également pris en charge.

    Parameters
    ----------
    audio_path : str | Path
        Fichier audio source.

    output_dir : str | Path
        Dossier de sortie.

    output_format : str
        Format audio souhaité.

    progress_callback : callable, optional
        Fonction appelée avec un pourcentage.

    Returns
    -------
    Path
        Chemin du fichier converti.
    """

    audio_path = Path(audio_path)
    output_dir = ensure_directory(output_dir)

    if not audio_path.is_file():
        raise FileNotFoundError(
            f"Le fichier audio n'existe pas : {audio_path}"
        )

    output_path = get_output_path(
        audio_path,
        output_dir,
        output_format,
    )

    temp_dir = get_temp_dir()
    temp_wav = None
    clip = None

    try:

        extension = audio_path.suffix.lower()

        # Cas particulier : MP4 contenant uniquement de l'audio
        if extension == ".mp4":

            if is_video_file(audio_path):
                raise ValueError(
                    f"Le fichier '{audio_path.name}' "
                    "contient une vidéo. "
                    "Utilisez la conversion vidéo → audio."
                )

            clip = AudioFileClip(str(audio_path))

            temp_wav = (
                Path(temp_dir)
                / f"{audio_path.stem}_temp.wav"
            )

            clip.write_audiofile(
                str(temp_wav),
                codec="pcm_s16le",
                logger=None,
            )

            clip.close()
            clip = None

            source_path = temp_wav

        else:
            source_path = audio_path

        if progress_callback:
            progress_callback(50)

        audio = AudioSegment.from_file(
            str(source_path)
        )

        audio.export(
            str(output_path),
            format=output_format.lower(),
        )

        if progress_callback:
            progress_callback(100)

        return output_path

    finally:

        if clip is not None:
            try:
                clip.close()
            except Exception:
                pass

        cleanup_temp_dir(temp_dir)
