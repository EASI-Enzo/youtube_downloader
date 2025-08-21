import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from yt_dlp import YoutubeDL

# --- Interface principale ---
root = tk.Tk()
root.title("Téléchargeur YouTube Pro")
root.geometry("600x350")
root.configure(bg="#222222")
root.resizable(False, False)

# --- Styles ---
style = ttk.Style(root)
style.theme_use('clam')
style.configure("TProgressbar", troughcolor="#333333", background="#00b300", thickness=20)
style.configure("Audio.TCheckbutton",
                background="#222222",
                foreground="white")
style.map("Audio.TCheckbutton",
          foreground=[("selected", "#00b300")],
          background=[("selected", "#222222")])

# --- URL ---
tk.Label(root, text="URL YouTube :", bg="#222222", fg="white", font=("Arial", 12)).pack(pady=5)
entry_url = tk.Entry(root, width=60, font=("Arial", 12))
entry_url.pack(pady=5)

# --- Dossier ---
frame_path = tk.Frame(root, bg="#222222")
frame_path.pack(pady=5)
entry_path = tk.Entry(frame_path, width=45, font=("Arial", 12))
entry_path.pack(side=tk.LEFT, padx=5)

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, folder)

btn_browse = tk.Button(frame_path, text="Parcourir", command=choose_folder, bg="#333", fg="white")
btn_browse.pack(side=tk.LEFT, padx=5)

# --- Audio seulement ---
var_audio = tk.BooleanVar()
audio_check = ttk.Checkbutton(root, text="Audio seulement (MP3)",
                              variable=var_audio, style="Audio.TCheckbutton")
audio_check.pack(pady=5)

# --- Barre de progression ---
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100, length=500, style="TProgressbar")
progress_bar.pack(pady=10)

# --- Label statut ---
status_label = tk.Label(root, text="En attente...", bg="#222222", fg="white", font=("Arial", 11))
status_label.pack(pady=5)

# --- Boutons ---
frame_btns = tk.Frame(root, bg="#222222")
frame_btns.pack(pady=10)

def reset_fields():
    # Réinitialise seulement l'URL et le choix audio
    entry_url.delete(0, tk.END)
    var_audio.set(False)
    progress_var.set(0)
    status_label.config(text="En attente...")
    # Supprimer les boutons Réinitialiser et Fermer
    for widget in frame_btns.winfo_children():
        if widget not in [btn_download]:
            widget.destroy()
    # Réafficher le bouton Télécharger
    btn_download.pack(side=tk.LEFT, padx=5)

def close_app():
    root.destroy()

# --- Téléchargement ---
def start_download():
    url = entry_url.get().strip()
    audio_only = var_audio.get()
    path = entry_path.get().strip()
    if not url:
        messagebox.showwarning("Attention", "Entrez une URL YouTube")
        return
    if not path:
        messagebox.showwarning("Attention", "Choisissez un dossier de téléchargement")
        return

    progress_var.set(0)
    status_label.config(text="Démarrage...")

    # Masquer le bouton Télécharger pendant le téléchargement
    btn_download.pack_forget()

    threading.Thread(target=download_video, args=(url, path, audio_only), daemon=True).start()

def download_video(url, path, audio_only):
    try:
        if not os.path.exists(path):
            os.makedirs(path)

        finished_once = False

        def progress_hook(d):
            nonlocal finished_once
            if d['status'] == 'downloading':
                total = d.get('total_bytes') or d.get('total_bytes_estimate')
                downloaded = d.get('downloaded_bytes', 0)
                if total:
                    percent = downloaded / total * 100
                    root.after(0, lambda: progress_var.set(percent))
                    root.after(0, lambda: status_label.config(text=f"Téléchargement : {percent:.1f}%"))
            elif d['status'] == 'finished':
                # Ignore ce finished initial, on attend le postprocessor final
                root.after(0, lambda: status_label.config(text="Téléchargement en cours de traitement..."))

        def postprocessor_hook(d):
            nonlocal finished_once
            if not finished_once and d.get('status') == 'finished':
                finished_once = True
                root.after(0, lambda: progress_var.set(100))
                root.after(0, lambda: status_label.config(text="Téléchargement terminé !"))
                root.after(0, create_finish_buttons)

        def create_finish_buttons():
            btn_reset = tk.Button(frame_btns, text="Réinitialiser", font=("Arial", 12),
                                  bg="#555555", fg="white", width=12, command=reset_fields)
            btn_close = tk.Button(frame_btns, text="Fermer", font=("Arial", 12),
                                  bg="#aa0000", fg="white", width=12, command=close_app)
            btn_reset.pack(side=tk.LEFT, padx=5)
            btn_close.pack(side=tk.LEFT, padx=5)

        ydl_opts = {
            'outtmpl': os.path.join(path, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'progress_hooks': [progress_hook],
            'postprocessor_hooks': [postprocessor_hook],
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
            ydl.download([url])

    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Erreur", str(e)))
        root.after(0, lambda: status_label.config(text="Erreur lors du téléchargement"))
        root.after(0, lambda: progress_var.set(0))
        root.after(0, lambda: btn_download.pack(side=tk.LEFT, padx=5))

# --- Bouton Télécharger ---
btn_download = tk.Button(frame_btns, text="Télécharger", font=("Arial", 12, "bold"), bg="#00b300",
                         fg="white", width=12, command=start_download)
btn_download.pack(side=tk.LEFT, padx=5)

# --- Lancer l'interface ---
root.mainloop()
