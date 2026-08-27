# src/gui/application.py

import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import traceback
import webbrowser

from src.services.transcription import transcribe_audio
from src.services.audio_converter import convert_audio_format
from src.services.video_converter import convert_video_to_audio
from src.config import APP_NAME, APP_VERSION, APP_DESCRIPTION, APP_CONTEXTE

class MediaConverterApp(tk.Tk):
    """Fenêtre principale de l'application."""

    def __init__(self):
        super().__init__()

        self.title("Media Transcriber")
        self.geometry("650x650")
        self.minsize(600, 600)
        self.iconbitmap("assets/media_transcriber_logo.ico")

        # ---------------------------------------------------------
        # État de l'application
        # ---------------------------------------------------------

        self.selected_files = []
        self.output_directory = ""

        self.current_action = tk.StringVar(value="transcribe")

        # ---------------------------------------------------------
        # Langues disponibles
        # ---------------------------------------------------------

        self.supported_languages = {
            "auto": "Détection automatique",
            "fr-FR": "Français (France)",
            "en-US": "Anglais (États-Unis)",
            "en-GB": "Anglais (Royaume-Uni)",
            "es-ES": "Espagnol",
            "de-DE": "Allemand",
            "it-IT": "Italien",
            "pt-BR": "Portugais (Brésil)",
        }

        self.translation_languages = {
            "none": "Ne pas traduire",
            "fr": "Français",
            "en": "Anglais",
            "es": "Espagnol",
            "de": "Allemand",
            "it": "Italien",
            "pt": "Portugais",
        }

        self.audio_formats = [
            "mp3",
            "wav",
            "ogg",
            "flac",
            "adts",
        ]

        # ---------------------------------------------------------
        # Construction de l'interface
        # ---------------------------------------------------------

        self.create_widgets()
        self.update_options_ui()

    # =============================================================
    # INTERFACE
    # =============================================================

    def create_widgets(self):
        """Construit l'ensemble des composants graphiques."""

        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(expand=True, fill=tk.BOTH)

        # ---------------------------------------------------------
        # Barre inférieure
        # ---------------------------------------------------------

        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(
            side=tk.BOTTOM,
            fill=tk.X,
            padx=10,
            pady=5,
        )

        help_button = ttk.Button(
            bottom_frame,
            text="À propos",
            command=self.show_about,
        )
        help_button.pack(side=tk.RIGHT)

        # ---------------------------------------------------------
        # 1. Action
        # ---------------------------------------------------------

        action_frame = ttk.LabelFrame(
            main_frame,
            text="1. Choisir une action",
            padding=10,
        )
        action_frame.pack(fill=tk.X, pady=5)

        ttk.Radiobutton(
            action_frame,
            text="Transcrire un média (vidéo / audio)",
            variable=self.current_action,
            value="transcribe",
            command=self.update_options_ui,
        ).pack(anchor=tk.W)

        ttk.Radiobutton(
            action_frame,
            text="Convertir une vidéo en audio",
            variable=self.current_action,
            value="video_to_audio",
            command=self.update_options_ui,
        ).pack(anchor=tk.W)

        ttk.Radiobutton(
            action_frame,
            text="Convertir un format audio",
            variable=self.current_action,
            value="audio_to_audio",
            command=self.update_options_ui,
        ).pack(anchor=tk.W)

        # ---------------------------------------------------------
        # 2. Fichiers
        # ---------------------------------------------------------

        files_frame = ttk.LabelFrame(
            main_frame,
            text="2. Fichiers d'entrée",
            padding=10,
        )
        files_frame.pack(expand=True, fill=tk.BOTH, pady=5)

        list_frame = ttk.Frame(files_frame)
        list_frame.pack(expand=True, fill=tk.BOTH)

        self.listbox_files = tk.Listbox(
            list_frame,
            selectmode=tk.EXTENDED,
            height=6,
        )
        self.listbox_files.pack(
            side=tk.LEFT,
            expand=True,
            fill=tk.BOTH,
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient=tk.VERTICAL,
            command=self.listbox_files.yview,
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox_files.config(
            yscrollcommand=scrollbar.set
        )

        add_button = ttk.Button(
            files_frame,
            text="Ajouter des fichiers...",
            command=self.add_files,
        )
        add_button.pack(
            fill=tk.X,
            pady=(8, 0),
        )

        # ---------------------------------------------------------
        # 3. Dossier de sortie
        # ---------------------------------------------------------

        output_frame = ttk.LabelFrame(
            main_frame,
            text="3. Dossier de sortie",
            padding=10,
        )
        output_frame.pack(fill=tk.X, pady=5)

        self.lbl_output_dir = ttk.Label(
            output_frame,
            text="Dossier actuel : dossier du premier fichier",
        )
        self.lbl_output_dir.pack(
            side=tk.LEFT,
            padx=(0, 10),
            expand=True,
            fill=tk.X,
        )

        select_output_button = ttk.Button(
            output_frame,
            text="Choisir...",
            command=self.select_output_dir,
        )
        select_output_button.pack(side=tk.RIGHT)

        # ---------------------------------------------------------
        # 4. Options
        # ---------------------------------------------------------

        self.options_frame = ttk.LabelFrame(
            main_frame,
            text="4. Options",
            padding=10,
        )
        self.options_frame.pack(fill=tk.X, pady=5)

        # ---------------------------------------------------------
        # Contrôle / progression
        # ---------------------------------------------------------

        control_frame = ttk.Frame(
            main_frame,
            padding=10,
        )
        control_frame.pack(fill=tk.X, pady=5)

        self.btn_start = ttk.Button(
            control_frame,
            text="Démarrer",
            command=self.start_processing,
        )
        self.btn_start.pack(
            side=tk.LEFT,
            padx=(0, 10),
        )

        self.progress_bar = ttk.Progressbar(
            control_frame,
            orient=tk.HORIZONTAL,
            mode="determinate",
        )
        self.progress_bar.pack(
            side=tk.LEFT,
            expand=True,
            fill=tk.X,
        )

        self.lbl_status = ttk.Label(
            main_frame,
            text="Prêt.",
        )
        self.lbl_status.pack(
            fill=tk.X,
            pady=(5, 0),
        )

    # =============================================================
    # OPTIONS
    # =============================================================

    def update_options_ui(self):
        """Met à jour les options selon l'action sélectionnée."""

        for widget in self.options_frame.winfo_children():
            widget.destroy()

        action = self.current_action.get()

        if action == "transcribe":
            self.create_transcription_options()

        elif action == "video_to_audio":
            self.create_audio_conversion_options(
                "Options de conversion vidéo → audio"
            )

        elif action == "audio_to_audio":
            self.create_audio_conversion_options(
                "Options de conversion audio → audio"
            )

        self.update_idletasks()

    def create_transcription_options(self):
        """Crée les options liées à la transcription."""

        self.options_frame.config(
            text="4. Options de transcription"
        )

        # Langue
        lang_frame = ttk.Frame(self.options_frame)
        lang_frame.pack(fill=tk.X, pady=3)

        ttk.Label(
            lang_frame,
            text="Langue du média :",
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.lang_var = tk.StringVar(value="fr-FR")

        language_values = [
            f"{code} ({name})"
            for code, name in self.supported_languages.items()
        ]

        self.lang_combo = ttk.Combobox(
            lang_frame,
            textvariable=self.lang_var,
            values=language_values,
            state="readonly",
            width=30,
        )
        self.lang_combo.pack(side=tk.LEFT)

        default_value = (
            f"fr-FR ({self.supported_languages['fr-FR']})"
        )

        self.lang_combo.set(default_value)

        # Format de sortie
        format_frame = ttk.Frame(self.options_frame)
        format_frame.pack(fill=tk.X, pady=3)

        ttk.Label(
            format_frame,
            text="Format de sortie :",
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.output_text_format_var = tk.StringVar(
            value="txt"
        )

        self.output_text_format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.output_text_format_var,
            values=["txt", "pdf"],
            state="readonly",
            width=10,
        )
        self.output_text_format_combo.pack(side=tk.LEFT)
        self.output_text_format_combo.set("txt")

        # Traduction
        translation_frame = ttk.Frame(
            self.options_frame
        )
        translation_frame.pack(fill=tk.X, pady=3)

        ttk.Label(
            translation_frame,
            text="Traduire en :",
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.translate_var = tk.StringVar(value="none")

        translation_values = [
            f"{code} ({name})"
            for code, name in self.translation_languages.items()
        ]

        self.translate_combo = ttk.Combobox(
            translation_frame,
            textvariable=self.translate_var,
            values=translation_values,
            state="readonly",
            width=30,
        )
        self.translate_combo.pack(side=tk.LEFT)

        self.translate_combo.set(
            f"none ({self.translation_languages['none']})"
        )

    def create_audio_conversion_options(self, title):
        """Crée les options de conversion audio."""

        self.options_frame.config(text=title)

        format_frame = ttk.Frame(
            self.options_frame
        )
        format_frame.pack(fill=tk.X, pady=3)

        ttk.Label(
            format_frame,
            text="Format audio de sortie :",
        ).pack(side=tk.LEFT, padx=(0, 5))

        self.output_audio_format_var = tk.StringVar(
            value="mp3"
        )

        self.output_audio_format_combo = ttk.Combobox(
            format_frame,
            textvariable=self.output_audio_format_var,
            values=self.audio_formats,
            state="readonly",
            width=10,
        )
        self.output_audio_format_combo.pack(side=tk.LEFT)
        self.output_audio_format_combo.set("mp3")

    # =============================================================
    # FICHIERS
    # =============================================================

    def add_files(self):
        """Permet à l'utilisateur de sélectionner des fichiers."""

        action = self.current_action.get()

        if action == "transcribe":
            filetypes = [
                (
                    "Fichiers média",
                    "*.mp4 *.avi *.mov *.mkv "
                    "*.mp3 *.wav *.ogg *.flac *.adts *.m4a",
                ),
                ("Tous les fichiers", "*.*"),
            ]

        elif action == "video_to_audio":
            filetypes = [
                (
                    "Fichiers vidéo",
                    "*.mp4 *.avi *.mov *.mkv",
                ),
                ("Tous les fichiers", "*.*"),
            ]

        else:
            filetypes = [
                (
                    "Fichiers audio",
                    "*.mp3 *.wav *.ogg *.flac "
                    "*.adts *.m4a",
                ),
                ("Tous les fichiers", "*.*"),
            ]

        files = filedialog.askopenfilenames(
            title="Sélectionner un ou plusieurs fichiers",
            filetypes=filetypes,
        )

        if not files:
            return

        # Remplacer la sélection précédente
        self.listbox_files.delete(0, tk.END)
        self.selected_files = []

        for file_path in files:
            self.listbox_files.insert(
                tk.END,
                os.path.basename(file_path),
            )
            self.selected_files.append(file_path)

        self.log_message(
            f"{len(files)} fichier(s) sélectionné(s)."
        )

        if self.selected_files and not self.output_directory:
            self.set_default_output_dir(
                self.selected_files[0]
            )

    def select_output_dir(self):
        """Permet de sélectionner le dossier de sortie."""

        directory = filedialog.askdirectory(
            title="Choisir le dossier de sortie"
        )

        if not directory:
            return

        self.output_directory = directory

        self.lbl_output_dir.config(
            text=f"Dossier : {directory}"
        )

        self.log_message(
            f"Dossier de sortie défini : {directory}"
        )

    def set_default_output_dir(self, file_path):
        """Définit le dossier du premier fichier comme sortie."""

        self.output_directory = os.path.dirname(
            file_path
        )

        self.lbl_output_dir.config(
            text=(
                "Dossier : "
                f"{self.output_directory}"
            )
        )

    # =============================================================
    # OPTIONS
    # =============================================================

    def get_current_options(self):
        """Récupère les options sélectionnées dans l'interface."""

        action = self.current_action.get()

        options = {
            "action": action
        }

        try:
            if action == "transcribe":

                selected_language = self.lang_var.get()

                options["language"] = (
                    selected_language.split(" ")[0]
                )

                options["output_format"] = (
                    self.output_text_format_var.get()
                )

                selected_translation = (
                    self.translate_var.get()
                )

                translation_code = (
                    selected_translation.split(" ")[0]
                )

                options["translate_to"] = (
                    None
                    if translation_code == "none"
                    else translation_code
                )

            elif action in (
                "video_to_audio",
                "audio_to_audio",
            ):
                options["output_format"] = (
                    self.output_audio_format_var.get()
                )

        except AttributeError as error:
            messagebox.showerror(
                "Erreur interne",
                (
                    "Impossible de récupérer les options.\n\n"
                    f"{error}"
                ),
            )
            return None

        return options

    # =============================================================
    # TRAITEMENT
    # =============================================================

    def start_processing(self):
        """Lance le traitement dans un thread séparé."""

        if not self.selected_files:
            messagebox.showwarning(
                "Aucun fichier",
                "Veuillez sélectionner au moins un fichier.",
            )
            return

        if not self.output_directory:
            self.set_default_output_dir(
                self.selected_files[0]
            )

        if not os.path.exists(self.output_directory):
            try:
                os.makedirs(
                    self.output_directory,
                    exist_ok=True,
                )
            except OSError as error:
                messagebox.showerror(
                    "Erreur",
                    (
                        "Impossible de créer le dossier "
                        f"de sortie :\n{error}"
                    ),
                )
                return

        options = self.get_current_options()

        if options is None:
            return

        self.btn_start.config(
            state=tk.DISABLED
        )

        self.update_progress(0)
        self.update_status(
            "Traitement en cours..."
        )

        files = list(self.selected_files)

        self.processing_thread = threading.Thread(
            target=self.process_files_thread,
            args=(
                files,
                self.output_directory,
                options,
            ),
            daemon=True,
        )

        self.processing_thread.start()

    def process_files_thread(
        self,
        files_to_process,
        output_dir,
        options,
    ):
        """
        Traite les fichiers en utilisant les services
        de l'application.
        """

        action = options.get("action")

        total_files = len(files_to_process)
        processed = 0
        errors = 0

        try:
            for index, file_path in enumerate(
                files_to_process,
                start=1,
            ):

                filename = os.path.basename(file_path)

                self.safe_update_status(
                    f"Traitement de {filename} "
                    f"({index}/{total_files})..."
                )

                self.safe_update_progress(0)

                try:

                    if action == "transcribe":

                        result = self.process_transcription(
                            file_path,
                            output_dir,
                            options,
                        )

                    elif action == "video_to_audio":

                        result = (
                            self.process_video_conversion(
                                file_path,
                                output_dir,
                                options,
                            )
                        )

                    elif action == "audio_to_audio":

                        result = (
                            self.process_audio_conversion(
                                file_path,
                                output_dir,
                                options,
                            )
                        )

                    else:
                        raise ValueError(
                            f"Action inconnue : {action}"
                        )

                    if result:
                        processed += 1

                        self.safe_log_message(
                            "Succès : "
                            f"{filename} → "
                            f"{os.path.basename(result)}"
                        )

                    else:
                        errors += 1

                except Exception as error:
                    errors += 1
                    
                    traceback.print_exc()

                    self.safe_show_error(
                        "Erreur inattendue",
                        str(error)
                    )

                    self.safe_update_status(
                        "Erreur pendant le traitement."
                    )

                    self.safe_log_message(
                        f"Erreur pour {filename} : {error}"
                    )

            # -----------------------------------------------------
            # Résultat global
            # -----------------------------------------------------

            if errors == 0:

                message = (
                    f"Terminé ! {processed}/"
                    f"{total_files} fichier(s) traité(s)."
                )

                self.safe_show_info(
                    "Traitement terminé",
                    message,
                )

            else:

                message = (
                    f"Traitement terminé avec des erreurs.\n\n"
                    f"Succès : {processed}/{total_files}\n"
                    f"Erreurs : {errors}"
                )

                self.safe_show_warning(
                    "Traitement terminé",
                    message,
                )

            self.safe_update_status(message)

        except Exception as error:
            
            traceback.print_exc()

            self.safe_log_message(
                f"Erreur inattendue : {error}"
            )

            self.safe_show_error(
                "Erreur",
                (
                    "Une erreur inattendue est survenue :\n\n"
                    f"{error}"
                ),
            )

            self.safe_update_status(
                "Erreur pendant le traitement."
            )

        finally:

            self.after(
                0,
                self.enable_start_button,
            )

    # =============================================================
    # SERVICES
    # =============================================================

    def process_transcription(
        self,
        file_path,
        output_dir,
        options,
    ):
        """
        Prépare le fichier audio puis appelle le service
        de transcription.

        La logique détaillée de transcription reste dans
        services/transcription.py.
        """

        extension = (
            os.path.splitext(file_path)[1]
            .lower()
        )

        video_extensions = {
            ".mp4",
            ".avi",
            ".mov",
            ".mkv",
        }

        audio_extensions = {
            ".mp3",
            ".wav",
            ".ogg",
            ".flac",
            ".adts",
            ".m4a",
        }

        # Le service de transcription peut gérer directement
        # les formats compatibles.
        if extension not in (
            video_extensions | audio_extensions
        ):
            raise ValueError(
                f"Format non supporté : {extension}"
            )

        self.safe_update_status(
            f"Transcription de {os.path.basename(file_path)}..."
        )

        return transcribe_audio(
            file_path,
            output_dir,
            output_format=options.get(
                "output_format",
                "txt",
            ),
            language=options.get(
                "language",
                "fr-FR",
            ),
            translate_to=options.get(
                "translate_to"
            ),
            progress_callback=(
                self.safe_update_progress
            ),
        )

    def process_video_conversion(
        self,
        file_path,
        output_dir,
        options,
    ):
        """Appelle le service de conversion vidéo → audio."""

        self.safe_update_status(
            "Conversion vidéo → audio..."
        )

        return convert_video_to_audio(
            file_path,
            output_dir,
            options.get(
                "output_format",
                "mp3",
            ),
            progress_callback=(
                self.safe_update_progress
            ),
        )

    def process_audio_conversion(
        self,
        file_path,
        output_dir,
        options,
    ):
        """Appelle le service de conversion audio → audio."""

        output_format = options.get(
            "output_format",
            "mp3",
        ).lower()

        input_format = (
            os.path.splitext(file_path)[1]
            .lower()
            .replace(".", "")
        )

        # Aucun traitement nécessaire
        if input_format == output_format:

            self.safe_log_message(
                f"{os.path.basename(file_path)} "
                f"est déjà au format {output_format.upper()}."
            )

            return file_path

        self.safe_update_status(
            "Conversion audio..."
        )

        return convert_audio_format(
            file_path,
            output_dir,
            output_format,
            progress_callback=(
                self.safe_update_progress
            ),
        )

    # =============================================================
    # INTERFACE / THREAD
    # =============================================================

    def update_status(self, message):
        """Met à jour le texte de statut."""

        self.lbl_status.config(
            text=message
        )

    def update_progress(self, value):
        """Met à jour la barre de progression."""

        self.progress_bar["value"] = value

    def log_message(self, message):
        """Affiche un message dans la barre de statut."""

        self.update_status(message)

    def enable_start_button(self):
        """Réactive le bouton de démarrage."""

        self.btn_start.config(
            state=tk.NORMAL
        )

    def safe_update_status(self, message):
        """Met à jour le statut depuis un thread."""

        self.after(
            0,
            self.update_status,
            message,
        )

    def safe_update_progress(self, value):
        """Met à jour la progression depuis un thread."""

        self.after(
            0,
            self.update_progress,
            value,
        )

    def safe_log_message(self, message):
        """Affiche un message depuis un thread."""

        self.after(
            0,
            self.log_message,
            message,
        )

    def safe_show_error(self, title, message):
        """Affiche une erreur depuis un thread."""

        self.after(
            0,
            messagebox.showerror,
            title,
            message,
        )

    def safe_show_warning(self, title, message):
        """Affiche un avertissement depuis un thread."""

        self.after(
            0,
            messagebox.showwarning,
            title,
            message,
        )

    def safe_show_info(self, title, message):
        """Affiche une information depuis un thread."""

        self.after(
            0,
            messagebox.showinfo,
            title,
            message,
        )

    # =============================================================
    # À PROPOS
    # =============================================================

    def show_about(self):
        about_window = tk.Toplevel(self)
        about_window.title("À propos de MediaTranscriber")
        about_window.geometry("500x300")
        about_window.resizable(False, False)

        # Garder la fenêtre au premier plan
        about_window.transient(self)
        about_window.grab_set()

        # Titre
        ttk.Label(
            about_window,
            text= APP_NAME,
            font=("TkDefaultFont", 16, "bold")
        ).pack(pady=(25, 10))

        # Description
        ttk.Label(
            about_window,
            text=APP_DESCRIPTION,
            justify="center"
        ).pack(pady=5)

        # Contexte du projet
        ttk.Label(
            about_window,
            text=APP_CONTEXTE,
            justify="center"
        ).pack(pady=(10, 5))

        # Version
        ttk.Label(about_window, text=f"Version {APP_VERSION}").pack(pady=(5, 10))

        # GitHub
        ttk.Label(about_window, 
                  text="Projet disponible sur GitHub :").pack(pady=(5, 2))

        github_url = "https://github.com/dtraore40/MediaTranscriber.git"

        git_link = ttk.Label(
            about_window,
            text=github_url,
            foreground="blue",
            cursor="hand2"
        )
        git_link.pack()

        git_link.bind(
            "<Button-1>",
            lambda event: webbrowser.open(github_url)
        )

        # Bouton fermer
        ttk.Button(about_window, text="Fermer", 
                   command=about_window.destroy).pack(pady=20)
        
        # --------------------------------------------------
        # Centrage de la fenêtre par rapport à l'application
        # --------------------------------------------------
        about_window.update_idletasks()

        window_width = about_window.winfo_width()
        window_height = about_window.winfo_height()

        main_width = self.winfo_width()
        main_height = self.winfo_height()

        main_x = self.winfo_x()
        main_y = self.winfo_y()

        x = main_x + (main_width - window_width) // 2
        y = main_y + (main_height - window_height) // 2

        about_window.geometry(
            f"{window_width}x{window_height}+{x}+{y}"
        )


