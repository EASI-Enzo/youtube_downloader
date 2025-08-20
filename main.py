import os
from yt_dlp import YoutubeDL

def download_video(url, path="downloads", audio_only=False):
    # Crée le dossier s'il n'existe pas
    if not os.path.exists(path):
        os.makedirs(path)

    # Options de téléchargement
    ydl_opts = {
        'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
        'quiet': False,
        'noplaylist': True,
    }

    if audio_only:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
        })

    with YoutubeDL(ydl_opts) as ydl:
        # Récupère les infos sans télécharger
        info_dict = ydl.extract_info(url, download=False)
        print(f"Titre : {info_dict.get('title')}")
        print(f"Auteur : {info_dict.get('uploader')}")
        print(f"Vues : {info_dict.get('view_count')}")
        # Téléchargement
        ydl.download([url])
        print("Téléchargement terminé !")

# Utilisation
url = input("Entrez l'URL YouTube : ")
mode = input("Voulez-vous seulement l'audio ? (o/n) : ").lower()
download_video(url, audio_only=(mode == "o"))
