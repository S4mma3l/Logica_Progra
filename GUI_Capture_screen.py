import os
import subprocess
import sys
import customtkinter as ctk
from tkinter import messagebox

# Configuración UTF-8 para compatibilidad con caracteres especiales
sys.stdout.reconfigure(encoding='utf-8')

# Configuración de CustomTkinter
ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue")

def list_ffmpeg_devices():
    """Lista los dispositivos de entrada de video y audio disponibles en FFmpeg."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        video_devices = []
        audio_devices = []
        for line in result.stderr.splitlines():
            if "DirectShow video device" in line:
                video_devices.append(line.split('"')[1])
            elif "DirectShow audio device" in line:
                audio_devices.append(line.split('"')[1])

        if not video_devices:
            raise ValueError("No se encontraron dispositivos de video disponibles.")
        if not audio_devices:
            raise ValueError("No se encontraron dispositivos de audio disponibles.")
            
        return video_devices, audio_devices
    except FileNotFoundError:
        messagebox.showerror("Error", "FFmpeg no está instalado o no está configurado en el PATH del sistema.")
        return [], []
    except ValueError as e:
        messagebox.showerror("Error", str(e))
        return [], []
    except Exception as e:
        messagebox.showerror("Error", f"Error al listar los dispositivos: {e}")
        return [], []

def validate_resolution(resolution):
    """Valida que la resolución ingresada esté en el formato correcto."""
    if not resolution:
        return False
    parts = resolution.split("x")
    return len(parts) == 2 and all(p.isdigit() for p in parts)

def validate_fps(fps):
    """Valida que el FPS sea un número positivo."""
    return fps.isdigit() and int(fps) > 0

def capture_iphone(video_device, audio_device, resolution, fps, output_file):
    """Inicia la captura del iPhone con FFmpeg."""
    command = [
        "ffmpeg",
        "-f", "dshow",
        "-video_size", resolution,
        "-framerate", str(fps),
        "-i", f"video={video_device}:audio={audio_device}",
        "-c:v", "libx264",
        "-preset", "ultrafast",
        "-c:a", "aac",
        "-strict", "experimental",
        output_file,
    ]
    try:
        subprocess.run(command, check=True)
    except KeyboardInterrupt:
        messagebox.showinfo("Información", "Captura detenida por el usuario.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al ejecutar FFmpeg: {e.stderr}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

def main():
    """Interfaz gráfica principal."""
    def start_capture():
        video_device = video_option.get()
        audio_device = audio_option.get()
        resolution = resolution_entry.get()
        fps = fps_entry.get()
        output_file = output_entry.get()

        if not video_device or not audio_device:
            messagebox.showerror("Error", "Los dispositivos de video y audio no pueden estar vacíos.")
            return

        if not validate_resolution(resolution):
            messagebox.showerror("Error", "Resolución inválida. Debe estar en el formato 'ancho x alto' (por ejemplo, 1280x720).")
            return

        if not validate_fps(fps):
            messagebox.showerror("Error", "FPS inválido. Debe ser un número positivo.")
            return

        if not output_file:
            messagebox.showerror("Error", "El nombre del archivo de salida no puede estar vacío.")
            return

        capture_iphone(video_device, audio_device, resolution, fps, output_file)

    app = ctk.CTk()
    app.title("Captura de Pantalla")
    app.geometry("600x800")

    # Obtener dispositivos disponibles
    video_devices, audio_devices = list_ffmpeg_devices()

    if not video_devices or not audio_devices:
        messagebox.showerror("Error", "No se encontraron dispositivos de video o audio disponibles.")
        return

    # Widgets de la interfaz
    title_label = ctk.CTkLabel(app, text="Captura de Pantalla", font=("Arial", 20))
    title_label.pack(pady=10)

    video_label = ctk.CTkLabel(app, text="Dispositivo de Video:")
    video_label.pack()
    video_option = ctk.CTkOptionMenu(app, values=video_devices)
    video_option.pack(pady=5)

    audio_label = ctk.CTkLabel(app, text="Dispositivo de Audio:")
    audio_label.pack()
    audio_option = ctk.CTkOptionMenu(app, values=audio_devices)
    audio_option.pack(pady=5)

    resolution_label = ctk.CTkLabel(app, text="Resolución (ejemplo: 1280x720):")
    resolution_label.pack()
    resolution_entry = ctk.CTkEntry(app, placeholder_text="Resolución de captura")
    resolution_entry.pack(pady=5)

    fps_label = ctk.CTkLabel(app, text="FPS (ejemplo: 30):")
    fps_label.pack()
    fps_entry = ctk.CTkEntry(app, placeholder_text="Cuadros por segundo")
    fps_entry.pack(pady=5)

    output_label = ctk.CTkLabel(app, text="Archivo de salida (ejemplo: output.mp4):")
    output_label.pack()
    output_entry = ctk.CTkEntry(app, placeholder_text="Nombre del archivo de salida")
    output_entry.pack(pady=5)

    start_button = ctk.CTkButton(app, text="Iniciar Captura", command=start_capture)
    start_button.pack(pady=20)

    app.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")