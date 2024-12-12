import pyperclip  # Para acceder al contenido del portapapeles
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle  # Para guardar y cargar las cookies
import time
import re  # Para la extracción de palabras clave
import os
import customtkinter as ctk
from threading import Thread

class WebCourseAnalyzer:
    def __init__(self, login_url, course_urls, cookies_file='cookies.pkl', obsidian_file="course_summary.md"):
        self.login_url = login_url
        self.course_urls = course_urls
        self.cookies_file = cookies_file
        self.obsidian_file = obsidian_file
        self.page_content = ""

    def fetch_content_with_selenium(self, update_log):
        service = FirefoxService(GeckoDriverManager().install())
        options = webdriver.FirefoxOptions()
        options.headless = False
        driver = webdriver.Firefox(service=service, options=options)

        try:
            driver.get(self.login_url)
            self.load_cookies(driver, update_log)

            WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))

            if not self.is_logged_in(driver):
                update_log("Por favor, inicia sesión manualmente en el navegador.")
                input("Presiona Enter cuando hayas iniciado sesión...")
                self.save_cookies(driver, update_log)

            for idx, url in enumerate(self.course_urls):
                driver.get(url)
                WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
                self.page_content = driver.page_source
                update_log(f"Contenido de la página {url} cargado con éxito.")

                self.extract_information_for_summary(driver, update_log)
                if idx < len(self.course_urls) - 1:
                    update_log(f"Procesando capítulo {idx + 1} de {len(self.course_urls)}... Continuar al siguiente capítulo.")
                    input("Presiona Enter para continuar...")

        except Exception as e:
            update_log(f"Error: {e}")

        finally:
            driver.quit()

    def load_cookies(self, driver, update_log):
        try:
            with open(self.cookies_file, 'rb') as cookiesfile:
                cookies = pickle.load(cookiesfile)
                for cookie in cookies:
                    driver.add_cookie(cookie)
            update_log("Cookies cargadas correctamente.")
        except FileNotFoundError:
            update_log("No se encontraron cookies guardadas, iniciar sesión manualmente.")

    def save_cookies(self, driver, update_log):
        cookies = driver.get_cookies()
        with open(self.cookies_file, 'wb') as cookiesfile:
            pickle.dump(cookies, cookiesfile)
        update_log("Cookies guardadas correctamente.")

    def is_logged_in(self, driver):
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "user-profile")))
            return True
        except:
            return False

    def extract_information_for_summary(self, driver, update_log):
        update_log("Por favor, selecciona el texto de la página del que deseas generar el resumen y las preguntas.")
        input("Presiona Enter una vez que hayas copiado el texto...")

        selected_text = pyperclip.paste().strip()
        if selected_text:
            update_log(f"Texto copiado correctamente: {selected_text[:200]}...")
            summary = self.summarize_content(selected_text)
            keywords = self.extract_keywords(selected_text)
            practices = self.generate_practice_questions(selected_text)
            self.write_to_obsidian(summary, keywords, practices, update_log)
        else:
            update_log("No se copió ningún texto o hubo un error al capturarlo.")

    def summarize_content(self, content):
        summary = '\n'.join(content.splitlines()[:10])
        return summary

    def extract_keywords(self, content):
        words = re.findall(r'\b\w+\b', content.lower())
        keywords = set(words)
        return keywords

    def generate_practice_questions(self, summary):
        questions = [
            f"¿Qué puntos clave se mencionan en el siguiente resumen: {summary}?",
            f"¿Cuáles son las implicaciones de los conceptos discutidos en este resumen?",
            f"Basado en este resumen, ¿cuáles son las mejores prácticas relacionadas con el tema?"
        ]
        return questions

    def write_to_obsidian(self, summary, keywords, practices, update_log):
        with open(self.obsidian_file, 'a', encoding='utf-8') as file:
            file.write("# Resumen del curso\n\n")
            file.write("## Resumen\n")
            file.write(f"{summary}\n\n")
            file.write("## Palabras clave\n")
            file.write(", ".join(keywords) + "\n\n")
            file.write("## Prácticas\n")
            for idx, practice in enumerate(practices, 1):
                file.write(f"{idx}. {practice}\n")
            file.write("\n---\n")
        update_log("Resumen guardado en Obsidian correctamente.")

class WebCourseGUI:
    def __init__(self):
        self.analyzer = None
        self.root = ctk.CTk()
        self.root.title("Web Course Analyzer")
        self.root.geometry("600x500")

        self.setup_gui()

    def setup_gui(self):
        ctk.CTkLabel(self.root, text="URL de inicio de sesión:").pack(pady=5)
        self.login_url_entry = ctk.CTkEntry(self.root, width=500)
        self.login_url_entry.pack(pady=5)

        ctk.CTkLabel(self.root, text="URLs de los cursos (separadas por coma):").pack(pady=5)
        self.course_urls_entry = ctk.CTkEntry(self.root, width=500)
        self.course_urls_entry.pack(pady=5)

        self.start_button = ctk.CTkButton(self.root, text="Iniciar", command=self.start_analysis)
        self.start_button.pack(pady=20)

        self.log_text = ctk.CTkTextbox(self.root, height=200, width=500)
        self.log_text.pack(pady=10)

    def update_log(self, message):
        self.log_text.insert(ctk.END, message + "\n")
        self.log_text.see(ctk.END)

    def start_analysis(self):
        login_url = self.login_url_entry.get()
        course_urls = [url.strip() for url in self.course_urls_entry.get().split(",")]

        if not login_url or not course_urls:
            self.update_log("Por favor, proporciona la URL de inicio de sesión y al menos una URL de curso.")
            return

        self.analyzer = WebCourseAnalyzer(login_url, course_urls)
        Thread(target=self.analyzer.fetch_content_with_selenium, args=(self.update_log,)).start()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = WebCourseGUI()
    gui.run()