# 🎙️ MediaTranscriber

> Application de bureau permettant de convertir, transcrire et traduire des fichiers audio et vidéo.

**MediaTranscriber** est une application Windows développée en **Python** avec **Tkinter**. Elle a été conçue dans le cadre d'un projet de **narration quantifiée**, notamment pour faciliter le traitement et l'exploitation d'entretiens enregistrés.

L'application propose une chaîne de traitement simple :

```text
Audio / Vidéo
      ↓
Transcription
      ↓
Traduction
      ↓
Export
```

---

## 📌 Fonctionnalités

MediaTranscriber permet de :

- 🎙️ Transcrire automatiquement des fichiers audio
- 🌍 Traduire les transcriptions dans une autre langue
- 🎬 Extraire l'audio de fichiers vidéo
- 🎵 Convertir des fichiers audio
- 📄 Exporter les résultats au format TXT ou PDF
- 📊 Suivre la progression des traitements

L'application peut également être distribuée sous forme d'**exécutable Windows**.

---

## 🛠️ Technologies utilisées

- **Python**
- **Tkinter** — interface graphique
- **SpeechRecognition** — reconnaissance vocale
- **Google Speech Recognition** — transcription
- **googletrans** — traduction
- **MoviePy** — traitement vidéo et audio
- **pydub** — conversion audio
- **FFmpeg** — traitement multimédia
- **ReportLab** — génération de fichiers PDF
- **PyInstaller** — création de l'exécutable Windows

---

## 🏗️ Architecture

```text
Media_Transcriber/
│
├── app.py
│
├── src/
│   ├── gui/
│   │   └── application.py
│   │
│   ├── services/
│   │   ├── transcription.py
│   │   ├── translation.py
│   │   ├── audio_converter.py
│   │   └── video_converter.py
│   │
│   ├── utils/
│   │   ├── files.py
│   │   └── ffmpeg.py
│   │
│   └── config.py
│
├── assets/
│   └── media_transcriber_logo.ico
│
├── ffmpeg-bin/
│   └── ...
│
├── README.md
├── requirements.txt
└── .gitignore
```

L'application est organisée en plusieurs modules afin de séparer l'interface graphique, les traitements multimédias, la transcription, la traduction et les fonctions utilitaires.

---

## 🚀 Installation et démarrage

### 1. Cloner le projet

```bash
git clone <URL_DU_DEPOT>
cd Media_Transcriber
```

### 2. Créer un environnement virtuel

#### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

#### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer FFmpeg

L'application utilise **FFmpeg** pour lire et convertir les fichiers audio et vidéo.

Placez les fichiers nécessaires dans `ffmpeg-bin/` à la racine du projet et conservez les fichiers de licence et d'information fournis avec la build utilisée.

Exemple de structure :

```text
ffmpeg-bin/
├── bin/
├── doc/
├── presets/
├── ffmpeg.exe
├── ffprobe.exe
├── LICENSE
└── README.txt
```

La licence dépend de la build de FFmpeg utilisée. FFmpeg peut être distribué sous **LGPL**, ou sous **GPL** lorsqu'il est compilé avec certains composants GPL.

Vérifiez la licence et la configuration de compilation de la build téléchargée avant sa redistribution.

### 5. Démarrer l'application

```bash
python app.py
```

---

## ⚠️ Limitations

La transcription et la traduction utilisent des services en ligne et nécessitent donc une **connexion Internet**.

La qualité de la transcription dépend notamment de la qualité de l'enregistrement, de la clarté de la voix, du bruit ambiant et des conditions audio.

Pour les transcriptions destinées à être **exploitées, citées ou utilisées dans un travail important**, une relecture et une vérification manuelle sont recommandées.

---

## 🎯 Objectif du projet

MediaTranscriber a pour objectif de simplifier le traitement d'enregistrements audio et vidéo en regroupant plusieurs opérations au sein d'une même application : conversion, transcription, traduction et export des résultats.

Le projet vise ainsi à proposer un outil simple permettant de passer d'un fichier multimédia brut à un document exploitable, tout en conservant une organisation modulaire facilitant son évolution.
