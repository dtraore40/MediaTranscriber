# src/services/translation.py
# Services de traduction de texte et de fichiers.

import os
import asyncio
from googletrans import Translator


class TranslationError(Exception):
    """Exception levée lorsqu'une traduction échoue."""
    pass


async def _translate_chunks(
    chunks,
    source_language,
    target_language,
    progress_callback=None
):
    """
    Effectue réellement les traductions avec googletrans.

    Cette fonction est asynchrone car googletrans 4.x utilise
    une API async.
    """

    translated_chunks = []
    total_chunks = len(chunks)

    async with Translator() as translator:

        for index, chunk in enumerate(chunks):

            if not chunk.strip():
                translated_chunks.append(chunk)
                continue

            result = await translator.translate(
                chunk,
                src=source_language,
                dest=target_language
            )

            translated_chunks.append(result.text)

            if progress_callback:
                progress = int(
                    ((index + 1) / total_chunks) * 100
                )
                progress_callback(progress)

    return translated_chunks


def translate_text(
    text,
    source_language,
    target_language,
    progress_callback=None,
    chunk_size=4000
):
    """
    Traduit un texte vers une langue cible.

    Parameters
    ----------
    text : str
        Texte à traduire.

    source_language : str
        Langue source, par exemple "fr", "en", "es".

    target_language : str
        Langue cible, par exemple "fr", "en", "es".

    progress_callback : callable, optional
        Fonction appelée avec le pourcentage d'avancement.

    chunk_size : int
        Taille maximale approximative des morceaux envoyés
        au service de traduction.

    Returns
    -------
    str
        Texte traduit.

    Raises
    ------
    ValueError
        Si les paramètres sont invalides.

    TranslationError
        Si la traduction échoue.
    """

    if not text or not text.strip():
        raise ValueError("Le texte à traduire est vide.")

    if not source_language:
        raise ValueError("La langue source doit être indiquée.")

    if not target_language:
        raise ValueError("La langue cible doit être indiquée.")

    # Si les langues sont identiques, aucune traduction
    # n'est nécessaire.
    if source_language.lower() == target_language.lower():

        if progress_callback:
            progress_callback(100)

        return text

    try:
        # Découpage du texte en morceaux.
        chunks = [
            text[i:i + chunk_size]
            for i in range(0, len(text), chunk_size)
        ]

        # googletrans 4.x est asynchrone.
        # On exécute donc la coroutine depuis cette fonction
        # qui reste synchrone pour le reste de l'application.
        translated_chunks = asyncio.run(
            _translate_chunks(
                chunks=chunks,
                source_language=source_language,
                target_language=target_language,
                progress_callback=progress_callback
            )
        )

        return " ".join(translated_chunks)

    except Exception as error:
        raise TranslationError(
            f"Impossible de traduire le texte : {error}"
        ) from error


def translate_file(
    input_path,
    output_path,
    source_language,
    target_language,
    progress_callback=None
):
    """
    Traduit le contenu d'un fichier texte et sauvegarde
    le résultat dans un nouveau fichier.

    Parameters
    ----------
    input_path : str
        Chemin du fichier texte source.

    output_path : str
        Chemin du fichier texte traduit.

    source_language : str
        Langue source.

    target_language : str
        Langue cible.

    progress_callback : callable, optional
        Fonction appelée avec le pourcentage d'avancement.

    Returns
    -------
    str
        Chemin du fichier traduit.
    """

    if not os.path.isfile(input_path):
        raise FileNotFoundError(
            f"Le fichier source n'existe pas : {input_path}"
        )

    try:
        with open(
            input_path,
            "r",
            encoding="utf-8"
        ) as file:
            text = file.read()

    except OSError as error:
        raise TranslationError(
            f"Impossible de lire le fichier : {error}"
        ) from error

    translated_text = translate_text(
        text=text,
        source_language=source_language,
        target_language=target_language,
        progress_callback=progress_callback
    )

    try:
        output_directory = os.path.dirname(output_path)

        if output_directory:
            os.makedirs(
                output_directory,
                exist_ok=True
            )

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(translated_text)

    except OSError as error:
        raise TranslationError(
            f"Impossible d'enregistrer le fichier traduit : {error}"
        ) from error

    return output_path
