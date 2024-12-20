import subprocess
import time
import os
import sys
from tkinter import messagebox
import customtkinter as ctk

# Aseguramos que el sistema esté utilizando UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Función para iniciar 5kPlayer (el servidor AirPlay)
def start_5kplayer():
    """
    Inicia 5kPlayer para que funcione como servidor AirPlay.
    Asegúrate de que 5kPlayer esté instalado en el directorio correcto y sea accesible desde PATH.
    """
    try:
        # Iniciar 5kPlayer en segundo plano
        subprocess.Popen("start 5kPlayer.exe", shell=True)
        time.sleep(5)  # Esperamos a que el servidor AirPlay inicie
        print("5kPlayer iniciado como servidor AirPlay.")
    except Exception as e:
        messagebox.showerror("Error", f"Error al iniciar 5kPlayer: {e}")
        return False
    return True

# Función para capturar la transmisión de AirPlay usando FFmpeg
def capture_airplay(ip_address, port, output_file):
    """
    Captura el video y audio transmitido por AirPlay usando FFmpeg.
    :param ip_address: Dirección IP del servidor AirPlay (será localhost en este caso).
    :param port: Puerto del servidor AirPlay (normalmente, 5000 para 5kPlayer).
    :param output_file: Nombre del archivo de salida (ej. "output.mp4").
    """
    rtsp_url = f"rtsp://{ip_address}:{port}"

    command = [
        "ffmpeg",
        "-i", rtsp_url,  # URL RTSP de AirPlay
        "-c:v", "libx264",  # Códec de video
        "-c:a", "aac",      # Códec de audio
        "-preset", "ultrafast",  # Preset rápido para captura en tiempo real
        "-f", "mp4",        # Formato de salida
        output_file         # Nombre del archivo de salida
    ]

    try:
        subprocess.run(command, check=True)
        print("Captura completada exitosamente.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error al ejecutar FFmpeg: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")

# Función principal que maneja la interfaz de usuario
def main():
    """Interfaz gráfica principal usando CustomTkinter."""
    app = ctk.CTk()
    app.title("Captura AirPlay desde iPhone")
    app.geometry("600x400")

    # Etiqueta y campos de entrada
    title_label = ctk.CTkLabel(app, text="Captura AirPlay de iPhone", font=("Arial", 20))
    title_label.pack(pady=10)

    ip_label = ctk.CTkLabel(app, text="Dirección IP del servidor AirPlay:")
    ip_label.pack()
    ip_entry = ctk.CTkEntry(app, placeholder_text="Por defecto: 127.0.0.1")
    ip_entry.pack(pady=5)
    ip_entry.insert(0, "127.0.0.1")

    port_label = ctk.CTkLabel(app, text="Puerto del servidor AirPlay:")
    port_label.pack()
    port_entry = ctk.CTkEntry(app, placeholder_text="Por defecto: 5000")
    port_entry.pack(pady=5)
    port_entry.insert(0, "5000")

    output_label = ctk.CTkLabel(app, text="Archivo de salida (ejemplo: output.mp4):")
    output_label.pack()
    output_entry = ctk.CTkEntry(app, placeholder_text="Nombre del archivo de salida")
    output_entry.pack(pady=5)

    # Función que ejecuta la captura cuando el usuario presiona "Iniciar Captura"
    def start_capture():
        ip_address = ip_entry.get()
        port = port_entry.get()
        output_file = output_entry.get()

        if not output_file:
            messagebox.showerror("Error", "El nombre del archivo de salida no puede estar vacío.")
            return

        # Iniciar 5kPlayer (servidor AirPlay)
        if not start_5kplayer():
            return

        # Capturar la transmisión de AirPlay usando FFmpeg
        capture_airplay(ip_address, port, output_file)

    # Botón para iniciar la captura
    start_button = ctk.CTkButton(app, text="Iniciar Captura", command=start_capture)
    start_button.pack(pady=20)

    app.mainloop()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error inesperado: {e}")