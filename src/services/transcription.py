# src/services/transcription.py

import os
import tempfile
import shutil

import speech_recognition as sr
from pydub import AudioSegment

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from src.services.translation import translate_text

def _create_temp_dir():
    """Crée un répertoire temporaire pour les fichiers intermédiaires."""
    return tempfile.mkdtemp()


def _cleanup_temp_dir(temp_dir):
    """Supprime un répertoire temporaire et son contenu."""
    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)


def _save_as_txt(text, output_path):
    """Sauvegarde un texte au format TXT."""
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(text)


def _save_as_pdf(text, output_path):
    """Sauvegarde un texte au format PDF."""
    try:
        c = canvas.Canvas(output_path, pagesize=letter)

        width, height = letter
        margin = 50
        text_width = width - (2 * margin)
        line_height = 14
        y_position = height - margin

        font_name = "Helvetica"
        font_size = 11

        c.setFont(font_name, font_size)

        lines = simpleSplit(
            text,
            font_name,
            font_size,
            text_width
        )

        for line in lines:
            if y_position < margin + line_height:
                c.showPage()
                c.setFont(font_name, font_size)
                y_position = height - margin

            c.drawString(margin, y_position, line)
            y_position -= line_height

        c.save()

    except Exception as error:
        raise RuntimeError(
            f"Impossible de générer le fichier PDF : {error}"
        ) from error


def transcribe_audio(
    audio_path,
    output_dir,
    output_format="txt",
    language="fr-FR",
    translate_to=None,
    progress_callback=None
):
    """
    Transcrit un fichier audio en texte.

    Le fichier audio peut être dans différents formats pris en charge
    par Pydub/FFmpeg : WAV, MP3, M4A, OGG, FLAC, etc.

    Parameters
    ----------
    audio_path : str
        Chemin du fichier audio à transcrire.

    output_dir : str
        Répertoire dans lequel enregistrer le résultat.

    output_format : str
        Format de sortie : "txt" ou "pdf".

    language : str
        Langue utilisée par Google Speech Recognition.
        Exemple : "fr-FR", "en-US", "es-ES".

    progress_callback : callable, optional
        Fonction appelée avec le pourcentage d'avancement.

    Returns
    -------
    str
        Chemin du fichier généré.

    Raises
    ------
    FileNotFoundError
        Si le fichier audio n'existe pas.

    ValueError
        Si le format de sortie n'est pas supporté.

    RuntimeError
        En cas d'erreur lors de la transcription.
    """

    # Vérification du fichier d'entrée
    if not os.path.isfile(audio_path):
        raise FileNotFoundError(
            f"Le fichier audio n'existe pas : {audio_path}"
        )

    # Vérification du format de sortie
    output_format = output_format.lower()

    if output_format not in ("txt", "pdf"):
        raise ValueError(
            "Format de sortie non pris en charge. "
            "Utilisez 'txt' ou 'pdf'."
        )

    # Création du dossier de sortie si nécessaire
    os.makedirs(output_dir, exist_ok=True)

    # Nom du fichier de sortie
    base_filename = os.path.splitext(
        os.path.basename(audio_path)
    )[0]

    output_path = os.path.join(
        output_dir,
        f"{base_filename}.{output_format}"
    )

    temp_dir = _create_temp_dir()

    try:
        # Chargement de l'audio.
        # Pydub utilise FFmpeg pour les formats qui le nécessitent.
        try:
            sound = AudioSegment.from_file(audio_path)
        except Exception as error:
            raise RuntimeError(
                f"Impossible de lire le fichier audio : {error}"
            ) from error

        # Découpage en segments de 60 secondes.
        chunk_length_ms = 60_000

        chunks = [
            sound[i:i + chunk_length_ms]
            for i in range(0, len(sound), chunk_length_ms)
        ]

        total_chunks = len(chunks)

        if total_chunks == 0:
            raise RuntimeError(
                "Le fichier audio ne contient aucune donnée exploitable."
            )

        recognizer = sr.Recognizer()
        full_text = []

        # Traitement des segments
        for index, chunk in enumerate(chunks):

            chunk_number = index + 1

            # Google Speech Recognition travaille ici avec des WAV
            # temporaires générés à partir du fichier audio d'origine.
            chunk_path = os.path.join(
                temp_dir,
                f"chunk_{chunk_number}.wav"
            )

            chunk.export(
                chunk_path,
                format="wav"
            )

            try:
                with sr.AudioFile(chunk_path) as source:
                    audio_data = recognizer.record(source)

                text = recognizer.recognize_google(
                    audio_data,
                    language=language
                )

                if text:
                    full_text.append(text)

            except sr.UnknownValueError:
                full_text.append("[inaudible]")

            except sr.RequestError as error:
                raise RuntimeError(
                    "Impossible de contacter le service Google Speech Recognition. "
                    "Vérifiez votre connexion Internet.\n"
                    f"Détail : {error}"
                ) from error

            except Exception as error:
                raise RuntimeError(
                    f"Erreur pendant la transcription du segment "
                    f"{chunk_number}/{total_chunks} : {error}"
                ) from error
            
            # Mise à jour de la progression
            if progress_callback:
                progress = int(
                    (chunk_number / total_chunks) * 100
                )
                progress_callback(progress)

        # Assemblage du texte final
        final_text = " ".join(full_text).strip()
        
        # ---------------------------------------------------------
        # Traduction optionnelle
        # ---------------------------------------------------------

        if translate_to and translate_to != "none":
            try:
                final_text = translate_text(
                    final_text,
                    source_language=language.split("-")[0],
                    target_language=translate_to
                )

            except Exception as error:
                raise RuntimeError(
                    f"Erreur lors de la traduction : {error}"
                ) from error

        # Sauvegarde
        if output_format == "txt":
            _save_as_txt(
                final_text,
                output_path
            )

        elif output_format == "pdf":
            _save_as_pdf(
                final_text,
                output_path
            )

        return output_path

    finally:
        _cleanup_temp_dir(temp_dir)

