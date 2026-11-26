import glob
import os
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp


def buscar_ffmpeg():
  """Devuelve la carpeta que contiene ffmpeg.exe, o None si no se encuentra.

  Busca primero en el PATH y luego en las rutas típicas de instalación
  (winget, C:\\ffmpeg), por si el PATH del proceso no está actualizado.
  """
  en_path = shutil.which("ffmpeg")
  if en_path:
    return os.path.dirname(en_path)

  local = os.environ.get("LOCALAPPDATA", "")
  patrones = [
      os.path.join(local, "Microsoft", "WinGet", "Packages", "*FFmpeg*", "*", "bin"),
      os.path.join(local, "Microsoft", "WinGet", "Links"),
      r"C:\ffmpeg\bin",
      r"C:\Program Files\ffmpeg\bin",
  ]
  for patron in patrones:
    for carpeta in glob.glob(patron):
      if os.path.isfile(os.path.join(carpeta, "ffmpeg.exe")):
        return carpeta
  return None


class DescargadorApp:

  def __init__(self, root):
    self.root = root
    self.root.title("YT-DLP Modern Downloader")
    self.root.geometry("620x560")
    self.root.resizable(False, False)

    # Definición de la Paleta de Colores (Estilo Dark / Profesional)
    self.bg_dark = "#121212"  # Fondo principal
    self.bg_card = "#1e1e1e"  # Fondo de secciones/marcos
    self.fg_text = "#e0e0e0"  # Texto principal claro
    self.fg_muted = "#aaaaaa"  # Texto secundario
    self.accent_color = "#10b981"  # Verde esmeralda moderno
    self.accent_hover = "#059669"  # Verde un poco más oscuro para hover
    self.entry_bg = "#2d2d2d"  # Fondo de inputs

    self.root.configure(bg=self.bg_dark)
    self.configurar_estilos_ttk()

    # Variables de control
    self.url_var = tk.StringVar()
    self.ruta_var = tk.StringVar(value=os.path.expanduser("~/Downloads"))
    self.tipo_var = tk.StringVar(value="video")
    self.playlist_var = tk.StringVar(value="no")

    self.crear_widgets()

  def configurar_estilos_ttk(self):
    """Configura los estilos oscuros para los widgets nativos de ttk (barra de progreso)"""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure(
        "TProgressbar",
        troughcolor=self.entry_bg,
        background=self.accent_color,
        borderwidth=0,
        thickness=8,
    )

  def crear_widgets(self):
    # Contenedor principal con padding
    main_frame = tk.Frame(self.root, bg=self.bg_dark)
    main_frame.pack(fill="both", expand=True, padx=25, pady=20)

    # Título principal
    lbl_titulo = tk.Label(
        main_frame,
        text="YOUTUBE DOWNLOADER",
        font=("Segoe UI", 16, "bold"),
        bg=self.bg_dark,
        fg=self.fg_text,
    )
    lbl_titulo.pack(anchor="w", pady=(0, 15))

    # Marco URL
    frame_url = tk.Frame(main_frame, bg=self.bg_dark)
    frame_url.pack(fill="x", pady=5)

    tk.Label(
        frame_url,
        text="Enlace de YouTube o Playlist",
        font=("Segoe UI", 9, "bold"),
        bg=self.bg_dark,
        fg=self.fg_muted,
    ).pack(anchor="w", pady=(0, 4))

    self.entry_url = tk.Entry(
        frame_url,
        textvariable=self.url_var,
        font=("Segoe UI", 10),
        bg=self.entry_bg,
        fg=self.fg_text,
        insertbackground="white",
        relief="flat",
        bd=0,
    )
    self.entry_url.pack(fill="x", ipady=8, ipadx=8)

    # Marco Ruta de Guardado
    frame_ruta = tk.Frame(main_frame, bg=self.bg_dark)
    frame_ruta.pack(fill="x", pady=10)

    tk.Label(
        frame_ruta,
        text="Carpeta de Destino",
        font=("Segoe UI", 9, "bold"),
        bg=self.bg_dark,
        fg=self.fg_muted,
    ).pack(anchor="w", pady=(0, 4))

    sub_frame_ruta = tk.Frame(frame_ruta, bg=self.bg_dark)
    sub_frame_ruta.pack(fill="x")

    self.entry_ruta = tk.Entry(
        sub_frame_ruta,
        textvariable=self.ruta_var,
        font=("Segoe UI", 10),
        bg=self.entry_bg,
        fg=self.fg_text,
        insertbackground="white",
        relief="flat",
        bd=0,
    )
    self.entry_ruta.pack(
        side="left", fill="x", expand=True, ipady=8, ipadx=8, padx=(0, 8)
    )

    self.btn_explorar = tk.Button(
        sub_frame_ruta,
        text="Examinar",
        font=("Segoe UI", 9, "bold"),
        bg="#333333",
        fg=self.fg_text,
        activebackground="#444444",
        activeforeground=self.fg_text,
        relief="flat",
        bd=0,
        padx=12,
        command=self.seleccionar_carpeta,
    )
    self.btn_explorar.pack(side="right", ipady=5)

    # Marco Opciones (Formato y Playlist agrupados en tarjetas)
    frame_opciones = tk.Frame(main_frame, bg=self.bg_dark)
    frame_opciones.pack(fill="x", pady=10)

    # Tarjeta Formato
    card_formato = tk.Frame(frame_opciones, bg=self.bg_card, padx=12, pady=12)
    card_formato.pack(side="left", fill="both", expand=True, padx=(0, 6))

    tk.Label(
        card_formato,
        text="FORMATO",
        font=("Segoe UI", 8, "bold"),
        bg=self.bg_card,
        fg=self.accent_color,
    ).pack(anchor="w", pady=(0, 8))

    self.crear_radio(
        card_formato, "Video completo (MP4)", self.tipo_var, "video"
    )
    self.crear_radio(card_formato, "Solo Audio (MP3)", self.tipo_var, "audio")

    # Tarjeta Playlist
    card_playlist = tk.Frame(frame_opciones, bg=self.bg_card, padx=12, pady=12)
    card_playlist.pack(side="right", fill="both", expand=True, padx=(6, 0))

    tk.Label(
        card_playlist,
        text="LISTA DE REPRODUCCIÓN",
        font=("Segoe UI", 8, "bold"),
        bg=self.bg_card,
        fg=self.accent_color,
    ).pack(anchor="w", pady=(0, 8))

    self.crear_radio(
        card_playlist, "Solo este video", self.playlist_var, "no"
    )
    self.crear_radio(
        card_playlist, "Playlist completa", self.playlist_var, "si"
    )

    # Botón Descargar Principal
    self.btn_descargar = tk.Button(
        main_frame,
        text="INICIAR DESCARGA",
        font=("Segoe UI", 10, "bold"),
        bg=self.accent_color,
        fg="#121212",
        activebackground=self.accent_hover,
        activeforeground="#121212",
        relief="flat",
        bd=0,
        command=self.iniciar_descarga,
    )
    self.btn_descargar.pack(fill="x", ipady=12, pady=15)

    # Sección de Progreso e Información
    frame_progreso = tk.Frame(
        main_frame, bg=self.bg_card, padx=12, pady=10
    )
    frame_progreso.pack(fill="x", pady=5)

    self.lbl_estado = tk.Label(
        frame_progreso,
        text="Listo para descargar",
        font=("Segoe UI", 9),
        bg=self.bg_card,
        fg=self.fg_text,
        anchor="w",
    )
    self.lbl_estado.pack(fill="x", pady=(0, 6))

    self.barra_progreso = ttk.Progressbar(
        frame_progreso, orient="horizontal", mode="determinate"
    )
    self.barra_progreso.pack(fill="x", pady=(0, 6))

    self.lbl_detalles = tk.Label(
        frame_progreso,
        text="",
        font=("Segoe UI", 8),
        bg=self.bg_card,
        fg=self.fg_muted,
        anchor="w",
    )
    self.lbl_detalles.pack(fill="x")

  def crear_radio(self, parent, text, variable, value):
    """Ayudante para crear Radiobuttons estilizados para el modo oscuro"""
    rb = tk.Radiobutton(
        parent,
        text=text,
        variable=variable,
        value=value,
        font=("Segoe UI", 9),
        bg=self.bg_card,
        fg=self.fg_text,
        selectcolor=self.bg_dark,
        activebackground=self.bg_card,
        activeforeground=self.fg_text,
        bd=0,
        highlightthickness=0,
    )
    rb.pack(anchor="w", pady=4)
    return rb

  def seleccionar_carpeta(self):
    carpeta = filedialog.askdirectory(initialdir=self.ruta_var.get())
    if carpeta:
      self.ruta_var.set(carpeta)

  def iniciar_descarga(self):
    url = self.url_var.get().strip()
    if not url:
      messagebox.showerror(
          "Error", "Por favor ingresa un enlace de YouTube válido."
      )
      return

    self.btn_descargar.config(state="disabled", bg="#333333", fg="#777777")
    self.barra_progreso["value"] = 0
    self.lbl_estado.config(text="Conectando con YouTube...", fg=self.accent_color)

    hilo = threading.Thread(target=self.proceso_descarga, args=(url,))
    hilo.start()

  def hook_progreso(self, d):
    if d["status"] == "downloading":
      pcent_str = d.get("_percent_str", "0%").strip().replace("%", "")
      try:
        pcent = float(pcent_str)
        self.root.after(0, lambda: self.barra_progreso.configure(value=pcent))
      except ValueError:
        pass

      filename = os.path.basename(d.get("filename", "Archivo"))
      speed = d.get("_speed_str", "N/A")
      eta = d.get("_eta_str", "N/A")

      texto_estado = f"Descargando: {filename}"
      texto_detalles = f"Progreso: {pcent_str}%  •  Velocidad: {speed}  •  Restante: {eta}"

      self.root.after(
          0, lambda: self.lbl_estado.config(text=texto_estado, fg=self.fg_text)
      )
      self.root.after(0, lambda: self.lbl_detalles.config(text=texto_detalles))

    elif d["status"] == "finished":
      self.root.after(
          0,
          lambda: self.lbl_estado.config(
              text="Procesando y uniendo archivos...", fg="#f59e0b"
          ),
      )
      self.root.after(0, lambda: self.barra_progreso.configure(value=100))

  def proceso_descarga(self, url):
    output_path = self.ruta_var.get()
    tipo = self.tipo_var.get()
    es_playlist = self.playlist_var.get()

    ydl_opts = {
        "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
        "progress_hooks": [self.hook_progreso],
        "no_color": True,
    }

    ffmpeg_dir = buscar_ffmpeg()
    if ffmpeg_dir:
      ydl_opts["ffmpeg_location"] = ffmpeg_dir

    if es_playlist == "no":
      ydl_opts["noplaylist"] = True

    if tipo == "video":
      ydl_opts.update({
          "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
          "merge_output_format": "mp4",
      })
    else:
      ydl_opts.update({
          "format": "bestaudio/best",
          "postprocessors": [{
              "key": "FFmpegExtractAudio",
              "preferredcodec": "mp3",
              "preferredquality": "192",
          }],
      })

    try:
      with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
      self.root.after(
          0,
          lambda: messagebox.showinfo(
              "¡Éxito!", "¡Descarga completada con éxito!"
          ),
      )
      self.root.after(
          0,
          lambda: self.lbl_estado.config(
              text="Descarga finalizada correctamente", fg=self.accent_color
          ),
      )
      self.root.after(0, lambda: self.lbl_detalles.config(text=""))
    except Exception as e:
      self.root.after(
          0, lambda: messagebox.showerror("Error", f"Ocurrió un error:\n{str(e)}")
      )
      self.root.after(
          0,
          lambda: self.lbl_estado.config(
              text="Error en la descarga", fg="#ef4444"
          ),
      )
      self.root.after(0, lambda: self.lbl_detalles.config(text=""))
    finally:
      self.root.after(
          0,
          lambda: self.btn_descargar.config(
              state="normal", bg=self.accent_color, fg="#121212"
          ),
      )


if __name__ == "__main__":
  root = tk.Tk()
  app = DescargadorApp(root)
  root.mainloop()