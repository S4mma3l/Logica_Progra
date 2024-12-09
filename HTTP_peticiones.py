import requests
from difflib import get_close_matches
from rich import print
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Función para manejar peticiones HTTP con manejo de errores
def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error al realizar la petición: {e}[/red]")
        return None

# Función para obtener nombres de Pokémon desde la PokéAPI
def get_all_pokemon_names():
    url = "https://pokeapi.co/api/v2/pokemon?limit=10000"
    data = fetch_data(url)
    if data:
        return [pokemon["name"] for pokemon in data["results"]]
    return []

# Función para sugerir nombres en caso de error
def suggest_names(name, all_names):
    suggestions = get_close_matches(name, all_names, n=5, cutoff=0.6)
    return suggestions

# Función para mostrar información del Pokémon
def display_pokemon_info(data):
    table = Table(title=f"[bold green]{data['name'].capitalize()}[/bold green]", title_style="bold cyan")
    table.add_column("Atributo", style="bold magenta")
    table.add_column("Valor", style="bold yellow")

    table.add_row("ID", str(data['id']))
    table.add_row("Peso", f"{data['weight']} hg")
    table.add_row("Altura", f"{data['height']} dm")
    types = ", ".join(t['type']['name'] for t in data['types'])
    table.add_row("Tipo(s)", types)

    console.print(table)

# Función para mostrar la cadena de evolución
def display_evolution_chain(chain):
    evolution_text = []

    def get_evolves(evolution):
        evolution_text.append(f"[bold cyan]- {evolution['species']['name'].capitalize()}[/bold cyan]")
        for evolves_to in evolution.get('evolves_to', []):
            get_evolves(evolves_to)

    get_evolves(chain)
    console.print(Panel("\n".join(evolution_text), title="[magenta]Cadena de Evolución[/magenta]", expand=False))

# Función principal para obtener información básica del Pokémon
def get_pokemon_info(pokemon, all_names):
    console.print(f"\n[cyan]Buscando información sobre '{pokemon}'...[/cyan]\n")
    base_url = f"https://pokeapi.co/api/v2/pokemon/{pokemon}/"
    data = fetch_data(base_url)

    if not data:
        suggestions = suggest_names(pokemon, all_names)
        if suggestions:
            console.print("\n[bold yellow]¿Quisiste decir?[/bold yellow]")
            for idx, suggestion in enumerate(suggestions, 1):
                console.print(f"[bold green]{idx}. {suggestion.capitalize()}[/bold green]")

            choice = console.input("\n[cyan]Selecciona una sugerencia o escribe '0' para intentar nuevamente: [/cyan]")
            if choice.isdigit() and 0 < int(choice) <= len(suggestions):
                pokemon = suggestions[int(choice) - 1]
                get_pokemon_info(pokemon, all_names)
        else:
            console.print("[red]No se encontraron sugerencias. Intenta nuevamente.[/red]")
        return

    # Mostrar información básica
    display_pokemon_info(data)

    # Obtener y mostrar cadena de evolución
    species_url = f"https://pokeapi.co/api/v2/pokemon-species/{pokemon}/"
    species_data = fetch_data(species_url)

    if species_data and 'evolution_chain' in species_data:
        evolution_chain_url = species_data['evolution_chain']['url']
        evolution_data = fetch_data(evolution_chain_url)

        if evolution_data:
            display_evolution_chain(evolution_data['chain'])

# Main: Solicitar entrada al usuario con una interfaz interactiva
if __name__ == "__main__":
    console.print("[bold magenta]Cargando lista de Pokémon, por favor espera...[/bold magenta]\n")
    all_names = get_all_pokemon_names()

    if not all_names:
        console.print("[bold red]Error al cargar la lista de Pokémon. Intenta más tarde.[/bold red]")
    else:
        while True:
            pokemon = console.input("\n[bold cyan]Introduce el nombre o número del Pokémon a buscar (o escribe 'salir' para terminar): [/bold cyan]").strip().lower()
            if pokemon == "salir":
                console.print("[bold green]¡Gracias por usar el programa! Hasta luego.[/bold green]")
                break
            get_pokemon_info(pokemon, all_names)
