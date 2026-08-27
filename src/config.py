# src/config.py - Configuration générale de MediaTranscriber.

from pathlib import Path


APP_NAME = "🎙️MediaTranscriber"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Application de transcription, traduction et conversion de fichiers audio et vidéo."
APP_CONTEXTE = "Projet réalisé en 2025 dans le cadre d'un projet\n" "de narration quantifiée."

# Répertoire racine du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# Répertoire contenant les ressources de l'application
ASSETS_DIR = BASE_DIR / "assets"

# Répertoire contenant FFmpeg lorsqu'il est fourni avec l'application
FFMPEG_DIR = BASE_DIR / "ffmpeg-bin"


# Formats audio supportés
AUDIO_FORMATS = [
    "mp3",
    "wav",
    "ogg",
    "flac",
    "adts",
]


# Formats vidéo acceptés
VIDEO_FORMATS = [
    ".mp4",
    ".avi",
    ".mov",
    ".mkv",
]


# Formats audio acceptés
INPUT_AUDIO_FORMATS = [
    ".mp3",
    ".wav",
    ".ogg",
    ".flac",
    ".adts",
    ".m4a",
]


# Langues disponibles pour la transcription
SUPPORTED_LANGUAGES = {
    "auto": "Automatique (français par défaut)",
    "fr-FR": "Français (France)",
    "en-US": "Anglais (US)",
    "en-GB": "Anglais (UK)",
    "es-ES": "Espagnol (Espagne)",
    "de-DE": "Allemand (Allemagne)",
    "it-IT": "Italien (Italie)",
    "pt-BR": "Portugais (Brésil)",
}


# Langues disponibles pour la traduction
TRANSLATION_LANGUAGES = {
    "none": "Ne pas traduire",
    "fr": "Français",
    "en": "Anglais",
    "es": "Espagnol",
    "de": "Allemand",
    "it": "Italien",
    "pt": "Portugais",
}


# Durée des segments utilisés pour la transcription
TRANSCRIPTION_CHUNK_LENGTH_MS = 60_000


# Formats de sortie texte
TEXT_OUTPUT_FORMATS = [
    "txt",
    "pdf",
]

