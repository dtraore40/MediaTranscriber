# app.py - Point d'entrée principal de l'application MediaTranscriber.

from src.utils.ffmpeg import configure_ffmpeg

configure_ffmpeg()

from src.gui.application import MediaConverterApp


def main():

    application = MediaConverterApp()
    application.mainloop()


if __name__ == "__main__":
    main()



