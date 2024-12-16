import os
import subprocess
from colorama import Fore, Style, init
import sys

# Configuración UTF-8 para compatibilidad con caracteres especiales
sys.stdout.reconfigure(encoding='utf-8')

# Inicializar colorama para colores en la terminal
init(autoreset=True)

def list_ffmpeg_devices():
    """Lista los dispositivos de entrada disponibles en FFmpeg."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        print(f"{Fore.CYAN}\nDispositivos detectados:\n")
        print(result.stderr)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: FFmpeg no está instalado o no está configurado en el PATH del sistema.")
        exit(1)
    except Exception as e:
        print(f"{Fore.RED}Error al listar los dispositivos: {e}")
        exit(1)

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
    print(f"{Fore.GREEN}\nEjecutando comando FFmpeg:\n")
    print(f"{Fore.YELLOW}{' '.join(command)}")
    try:
        subprocess.run(command, check=True)
    except KeyboardInterrupt:
        print(f"{Fore.MAGENTA}\nCaptura detenida por el usuario.")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Error al ejecutar FFmpeg: {e}")
    except Exception as e:
        print(f"{Fore.RED}Ocurrió un error inesperado: {e}")

def main():
    print(f"{Fore.BLUE}=== Captura de iPhone con FFmpeg ===\n")

    print(f"{Fore.CYAN}1. Listando dispositivos disponibles en FFmpeg...\n")
    list_ffmpeg_devices()

    video_device = input(f"{Fore.YELLOW}\nIngresa el nombre exacto del dispositivo de VIDEO: ").strip()
    while not video_device:
        print(f"{Fore.RED}El nombre del dispositivo de video no puede estar vacío.")
        video_device = input(f"{Fore.YELLOW}Ingresa el nombre exacto del dispositivo de VIDEO: ").strip()

    audio_device = input(f"{Fore.YELLOW}Ingresa el nombre exacto del dispositivo de AUDIO: ").strip()
    while not audio_device:
        print(f"{Fore.RED}El nombre del dispositivo de audio no puede estar vacío.")
        audio_device = input(f"{Fore.YELLOW}Ingresa el nombre exacto del dispositivo de AUDIO: ").strip()

    resolution = input(f"{Fore.YELLOW}Ingresa la resolución (ejemplo: 1280x720): ").strip()
    while not validate_resolution(resolution):
        print(f"{Fore.RED}Resolución inválida. Debe estar en el formato 'ancho x alto' (por ejemplo, 1280x720).")
        resolution = input(f"{Fore.YELLOW}Ingresa la resolución (ejemplo: 1280x720): ").strip()

    fps = input(f"{Fore.YELLOW}Ingresa la tasa de cuadros por segundo (FPS, ejemplo: 30): ").strip()
    while not validate_fps(fps):
        print(f"{Fore.RED}FPS inválido. Debe ser un número positivo.")
        fps = input(f"{Fore.YELLOW}Ingresa la tasa de cuadros por segundo (FPS, ejemplo: 30): ").strip()

    output_file = input(f"{Fore.YELLOW}Ingresa el nombre del archivo de salida (ejemplo: output.mp4): ").strip()
    while not output_file:
        print(f"{Fore.RED}El nombre del archivo de salida no puede estar vacío.")
        output_file = input(f"{Fore.YELLOW}Ingresa el nombre del archivo de salida (ejemplo: output.mp4): ").strip()

    print(f"{Fore.GREEN}\nIniciando la captura. Presiona Ctrl+C para detener.")
    capture_iphone(video_device, audio_device, resolution, fps, output_file)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"{Fore.MAGENTA}\nPrograma terminado por el usuario.")
    except Exception as e:
        print(f"{Fore.RED}Ocurrió un error inesperado: {e}")