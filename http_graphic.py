import requests
from difflib import get_close_matches
import customtkinter as ctk
from tkinter import messagebox

# Configuración inicial de customtkinter
ctk.set_appearance_mode("Dark")  # Opciones: "System", "Light", "Dark"
ctk.set_default_color_theme("blue")  # Opciones: "blue", "green", "dark-blue"

# Función para manejar peticiones HTTP con manejo de errores
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None  # Retorna None en caso de error

# Función para obtener nombres de Pokémon desde la PokéAPI
def get_all_pokemon_names():
    url = "https://pokeapi.co/api/v2/pokemon?limit=10000"
    data = fetch_data(url)
    if data:
        return [pokemon["name"] for pokemon in data["results"]]
    return []

# Función para buscar información del Pokémon
def search_pokemon():
    pokemon_name = search_entry.get().strip().lower()
    if not pokemon_name:
        messagebox.showwarning("Entrada vacía", "Por favor, introduce un nombre o número de Pokémon.")
        return

    base_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}/"
    data = fetch_data(base_url)

    if not data:
        suggestions = suggest_names(pokemon_name, all_names)
        if suggestions:
            # Mostrar sugerencias en un menú desplegable
            suggestion_menu.configure(values=suggestions)
            suggestion_menu.set("Selecciona una sugerencia")
            suggestion_menu.grid(row=1, column=0, columnspan=3, pady=10)
        else:
            messagebox.showinfo("Sin resultados", "No se encontraron coincidencias. Intenta nuevamente.")
        return

    display_pokemon_info(data)
    get_evolution_chain(data["species"]["url"])

# Función para sugerir nombres
def suggest_names(name, all_names):
    return get_close_matches(name, all_names, n=5, cutoff=0.6)

# Función para mostrar información del Pokémon
def display_pokemon_info(data):
    info_text.delete("1.0", ctk.END)
    info_text.insert(ctk.END, f"Nombre: {data['name'].capitalize()}\n")
    info_text.insert(ctk.END, f"ID: {data['id']}\n")
    info_text.insert(ctk.END, f"Peso: {data['weight']} hg\n")
    info_text.insert(ctk.END, f"Altura: {data['height']} dm\n")
    types = ", ".join(t['type']['name'] for t in data['types'])
    info_text.insert(ctk.END, f"Tipo(s): {types}\n")

# Función para mostrar cadena de evolución
def get_evolution_chain(species_url):
    species_data = fetch_data(species_url)
    if not species_data or "evolution_chain" not in species_data:
        evolution_text.delete("1.0", ctk.END)
        evolution_text.insert(ctk.END, "No se pudo obtener la cadena de evolución.")
        return

    evolution_chain_url = species_data["evolution_chain"]["url"]
    evolution_data = fetch_data(evolution_chain_url)

    if not evolution_data:
        evolution_text.delete("1.0", ctk.END)
        evolution_text.insert(ctk.END, "No se pudo obtener la cadena de evolución.")
        return

    evolution_text.delete("1.0", ctk.END)
    evolution_text.insert(ctk.END, "Cadena de Evolución:\n")

    def get_evolves(evolution):
        evolution_text.insert(ctk.END, f"- {evolution['species']['name'].capitalize()}\n")
        for evolves_to in evolution.get("evolves_to", []):
            get_evolves(evolves_to)

    get_evolves(evolution_data["chain"])

# Función para manejar selección desde el menú desplegable
def select_suggestion(selected_name):
    search_entry.delete(0, ctk.END)
    search_entry.insert(0, selected_name)
    search_pokemon()

# Crear ventana principal
app = ctk.CTk()
app.title("PokéDex")
app.geometry("700x650")

# Cargar nombres de Pokémon
all_names = get_all_pokemon_names()

# Widgets de la aplicación
title_label = ctk.CTkLabel(app, text="PokéDex", font=("Arial", 24, "bold"))
title_label.pack(pady=10)

search_frame = ctk.CTkFrame(app)
search_frame.pack(pady=10)

search_label = ctk.CTkLabel(search_frame, text="Nombre o ID del Pokémon:")
search_label.grid(row=0, column=0, padx=10, pady=10)

search_entry = ctk.CTkEntry(search_frame, width=300, placeholder_text="Ejemplo: pikachu o 25")
search_entry.grid(row=0, column=1, padx=10, pady=10)

search_button = ctk.CTkButton(search_frame, text="Buscar", command=search_pokemon)
search_button.grid(row=0, column=2, padx=10, pady=10)

# Menú desplegable para sugerencias
suggestion_menu = ctk.CTkOptionMenu(
    search_frame, values=[], command=select_suggestion, width=300
)

info_label = ctk.CTkLabel(app, text="Información del Pokémon", font=("Arial", 18, "bold"))
info_label.pack(pady=10)

info_text = ctk.CTkTextbox(app, width=300, height=150)
info_text.pack(pady=10)

evolution_label = ctk.CTkLabel(app, text="Cadena de Evolución", font=("Arial", 18, "bold"))
evolution_label.pack(pady=10)

evolution_text = ctk.CTkTextbox(app, width=300, height=150)
evolution_text.pack(pady=10)

# Ejecutar aplicación
app.mainloop()
