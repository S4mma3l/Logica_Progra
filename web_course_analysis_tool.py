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

class WebCourseAnalyzer:
    def __init__(self, login_url, course_urls, cookies_file='cookies.pkl', obsidian_file="course_summary.md"):
        self.login_url = login_url
        self.course_urls = course_urls
        self.cookies_file = cookies_file
        self.obsidian_file = obsidian_file
        self.page_content = ""

    def fetch_content_with_selenium(self):
        # Usar GeckoDriverManager para manejar automáticamente la instalación de geckodriver
        service = FirefoxService(GeckoDriverManager().install())  # Esto maneja la instalación de geckodriver
        options = webdriver.FirefoxOptions()
        options.headless = False  # Abrir el navegador de manera visible para la interacción
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')

        # Crear la instancia del navegador
        driver = webdriver.Firefox(service=service, options=options)

        try:
            # Cargar la página de login primero
            driver.get(self.login_url)

            # Intentar cargar las cookies si existen
            self.load_cookies(driver)

            # Esperar a que la página de login cargue completamente
            WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))

            # Si no se está logueado, iniciar sesión manualmente
            if not self.is_logged_in(driver):
                print("Por favor ingresa tus credenciales en la ventana del navegador que se abrió.")
                input("Presiona Enter cuando hayas iniciado sesión...")  # Pausa el código hasta que hayas iniciado sesión manualmente

                # Guardar cookies después de iniciar sesión
                self.save_cookies(driver)

            # Espera a que la página cargue completamente después del inicio de sesión
            WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))

            # Navegar por cada URL proporcionada después de iniciar sesión
            for idx, url in enumerate(self.course_urls):
                driver.get(url)
                WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))  # Espera hasta que cargue la página

                # Captura el contenido de la página después de cargarla
                self.page_content = driver.page_source
                print(f"Contenido de la página {url} cargado con éxito.")

                # Si es la última URL, permitir selección de texto y procesarlo
                if idx == len(self.course_urls) - 1:
                    while True:  # Mantiene el ciclo hasta que el usuario decida salir
                        # Permitir al usuario seleccionar el texto de la página
                        self.extract_information_for_summary(driver)

                        # Pregunta si desea continuar con otro capítulo
                        user_input = input("¿Deseas continuar con otro capítulo? (s/n): ")
                        if user_input.lower() != 's':
                            break  # Salir del ciclo si el usuario no desea continuar
                else:
                    # Si no es la última página, continuar con la siguiente URL
                    print(f"Procesando capítulo {idx + 1} de {len(self.course_urls)}...")
                    input(f"Presiona Enter para continuar al siguiente capítulo de {url}...")

        finally:
            driver.quit()

    def load_cookies(self, driver):
        # Cargar cookies de archivo si existen
        try:
            with open(self.cookies_file, 'rb') as cookiesfile:
                cookies = pickle.load(cookiesfile)
                for cookie in cookies:
                    driver.add_cookie(cookie)
            print("Cookies cargadas correctamente.")
        except FileNotFoundError:
            print("No se encontraron cookies guardadas, iniciar sesión manualmente.")

    def save_cookies(self, driver):
        # Guardar cookies en un archivo
        cookies = driver.get_cookies()
        with open(self.cookies_file, 'wb') as cookiesfile:
            pickle.dump(cookies, cookiesfile)
        print("Cookies guardadas correctamente.")

    def is_logged_in(self, driver):
        # Comprobar si el usuario ya está logueado revisando un elemento específico de la página
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "user-profile")))  # Ajusta esto a un elemento que confirme el login
            return True
        except:
            return False

    def extract_information_for_summary(self, driver):
        """
        Extrae información importante de la última URL y genera un resumen
        """
        # Instrucciones para que el usuario seleccione texto manualmente
        print("Por favor, selecciona el texto de la página del que deseas generar el resumen y las preguntas.")
        input("Presiona Enter una vez que hayas copiado el texto...")

        # Usamos pyperclip para obtener el contenido del portapapeles
        selected_text = pyperclip.paste().strip()  # Obtiene el contenido del portapapeles

        if selected_text:
            print("Texto copiado correctamente:", selected_text[:200])  # Muestra una parte del texto copiado para verificar

            # Generamos el resumen y las preguntas a partir del texto copiado
            summary = self.summarize_content(selected_text)
            keywords = self.extract_keywords(selected_text)
            practices = self.generate_practice_questions(selected_text)

            # Escribimos los resultados en el archivo Obsidian
            self.write_to_obsidian(summary, keywords, practices)
        else:
            print("No se copió ningún texto o hubo un error al capturarlo. Intentando de nuevo.")

    def summarize_content(self, content):
        """
        Función para generar un resumen básico del contenido
        """
        # Aquí se puede usar una lógica más avanzada, como procesamiento de lenguaje natural
        # Para fines simples, podemos recortar el texto a las primeras líneas significativas
        summary = '\n'.join(content.splitlines()[:10])  # Resumen de las primeras 10 líneas del contenido
        return summary

    def extract_keywords(self, content):
        """
        Extrae palabras clave del contenido, esto es muy básico
        """
        # Usamos una expresión regular para obtener palabras significativas.
        words = re.findall(r'\b\w+\b', content.lower())
        keywords = set(words)  # Eliminar duplicados
        return keywords

    def generate_practice_questions(self, summary):
        """
        Genera preguntas prácticas basadas en el resumen.
        """
        questions = [
            f"¿Qué puntos clave se mencionan en el siguiente resumen: {summary}?",
            f"¿Cuáles son las implicaciones de los conceptos discutidos en este resumen?",
            f"Basado en este resumen, ¿cuáles son las mejores prácticas relacionadas con el tema?"
        ]
        return questions

    def write_to_obsidian(self, summary, keywords, practices):
        """
        Escribe el resumen, palabras clave y prácticas en un archivo para Obsidian.
        """
        with open(self.obsidian_file, 'a', encoding='utf-8') as file:  # Abrimos el archivo en modo append ('a')
            file.write("# Resumen del curso\n\n")
            file.write("## Resumen\n")
            file.write(f"{summary}\n\n")
            
            file.write("## Palabras clave\n")
            file.write(", ".join(keywords) + "\n\n")
            
            file.write("## Prácticas\n")
            for idx, practice in enumerate(practices, 1):
                file.write(f"{idx}. {practice}\n")
            file.write("\n---\n")  # Se agrega una línea de separación entre cada capítulo.

if __name__ == "__main__":
    login_url = "https://my.isc2.org/s/login"
    course_urls = [
        "https://my.isc2.org/s/Dashboard/MyCourses",
        "https://learn.isc2.org/d2l/home",
        "https://learn.isc2.org/d2l/home/10845",
        "https://learn.isc2.org/d2l/le/enhancedSequenceViewer/10845?url=https%3A%2F%2Fbabe4806-440f-4af0-91ac-9d7c60651b42.sequences.api.brightspace.com%2F10845%2Factivity%2F502030%3FfilterOnDatesAndDepth%3D1",
        "https://learn.isc2.org/d2l/le/enhancedSequenceViewer/10845?url=https%3A%2F%2Fbabe4806-440f-4af0-91ac-9d7c60651b42.sequences.api.brightspace.com%2F10845%2Factivity%2F502038%3FfilterOnDatesAndDepth%3D1",
        "https://learn.isc2.org/d2l/le/enhancedSequenceViewer/10845?url=https%3A%2F%2Fbabe4806-440f-4af0-91ac-9d7c60651b42.sequences.api.brightspace.com%2F10845%2Factivity%2F502092%3FfilterOnDatesAndDepth%3D1"
    ]
    analyzer = WebCourseAnalyzer(login_url, course_urls)
    analyzer.fetch_content_with_selenium()