import os
import re
import yt_dlp
import subprocess
import speech_recognition as sr
from googletrans import Translator
from transformers import pipeline
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer

# --- Configuración ---
output_folder = "output"
os.makedirs(output_folder, exist_ok=True)

# --- Funciones ---

def download_audio(youtube_url):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'output/%(title)s.%(ext)s',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(youtube_url, download=True)
            audio_path = ydl.prepare_filename(info_dict)
            return audio_path, info_dict.get('title', 'Título desconocido')
    except Exception as e:
        raise RuntimeError(f"Error al descargar el audio: {str(e)}")

def convert_to_mp3(audio_path):
    try:
        mp3_path = audio_path.rsplit(".", 1)[0] + ".mp3"
        subprocess.run(['ffmpeg', '-i', audio_path, '-vn', '-acodec', 'libmp3lame', '-ab', '192k', mp3_path], check=True)
        return mp3_path
    except subprocess.CalledProcessError:
        raise RuntimeError("Error al convertir el archivo a MP3.")

def convert_to_wav(mp3_path):
    try:
        wav_path = mp3_path.rsplit(".", 1)[0] + ".wav"
        subprocess.run(['ffmpeg', '-i', mp3_path, '-ar', '16000', '-ac', '1', wav_path], check=True)
        if not os.path.exists(wav_path):
            raise FileNotFoundError(f"El archivo WAV no se creó correctamente: {wav_path}")
        return wav_path
    except subprocess.CalledProcessError:
        raise RuntimeError("Error al convertir el archivo a WAV.")

def transcribe_audio(audio_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Error: No se pudo entender el audio"
    except sr.RequestError:
        return "Error: Problema con la solicitud de reconocimiento de voz"
    except Exception as e:
        return f"Error inesperado: {str(e)}"

def translate_text(text, target_language="es"):
    try:
        translator = Translator()
        translation = translator.translate(text, dest=target_language)
        return translation.text
    except Exception as e:
        return f"Error al traducir texto: {str(e)}"

def summarize_text(text):
    try:
        summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
        max_len = min(len(text.split()) + 20, 150)
        return summarizer(text, max_length=max_len, min_length=20, do_sample=False)[0]['summary_text']
    except Exception as e:
        return f"Error al resumir texto: {str(e)}"

def extract_keywords(text, num_keywords=10):
    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=num_keywords)
        tfidf_matrix = vectorizer.fit_transform([text])
        return vectorizer.get_feature_names_out()
    except ValueError:
        return ["Texto demasiado corto para extraer palabras clave."]

def create_obsidian_note(title, summary, keywords, original_text, language):
    try:
        title_cleaned = re.sub(r'[<>:"/\\|?*]', '', title)
        title_cleaned = title_cleaned[:100]  # Limitar longitud
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        note_content = f"""
# {title_cleaned}

**Fecha:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Resumen
{summary}

## Palabras clave
- {', '.join(keywords)}

## Texto Original ({language})
{original_text}
        """
        note_path = os.path.join(output_folder, f"{title_cleaned}_{timestamp}.md")
        with open(note_path, "w", encoding="utf-8") as f:
            f.write(note_content)
        return note_path
    except Exception as e:
        raise RuntimeError(f"Error al crear la nota: {str(e)}")

# --- Flujo Principal ---
if __name__ == "__main__":
    try:
        youtube_url = input("Introduce la URL de YouTube: ").strip()
        print("\nDescargando audio...")
        audio_path, yt_title = download_audio(youtube_url)

        print("\nConvirtiendo el audio a mp3...")
        mp3_path = convert_to_mp3(audio_path)

        print("\nConvirtiendo el audio a WAV...")
        wav_path = convert_to_wav(mp3_path)

        print("\nTranscribiendo audio...")
        original_text = transcribe_audio(wav_path)
        if "Error" in original_text:
            raise ValueError(f"Fallo en la transcripción: {original_text}")

        print("\nTraduciendo texto...")
        translated_text = translate_text(original_text)

        print("\nResumiendo texto...")
        summary = summarize_text(translated_text)

        print("\nExtrayendo palabras clave...")
        keywords = extract_keywords(translated_text)

        print("\nCreando nota para Obsidian...")
        note_path = create_obsidian_note(yt_title, summary, keywords, translated_text, "es")
        print(f"Nota creada: {note_path}")

    except Exception as e:
        print(f"\nError en el flujo principal: {str(e)}")