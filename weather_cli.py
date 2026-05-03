import os
import sys
import time
import requests
import numpy as np
from datetime import datetime
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.columns import Columns
from rich.text import Text
from rich.align import Align
from rich.live import Live

# Ensure proper standard output encoding on Windows terminals
if sys.platform == "win32":
    try:
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    except Exception:
        pass

# Import ML component
from weather_ml import WeatherML

console = Console()

# Static frame patterns for weather conditions
ART_ANIMATIONS = {
    0: """
[yellow]     \\   :   /
      .-"-.
    -(     )-
      '-._.-'
     /   :   \\
[/yellow]""",
    1: """
[white]       .--.
    .-(    ).
   (___.__)__)[/white]
""",
    2: """
[cyan]       .--.
    .-(    ).
   (___.__)__)
     '  '  '  '
    '  '  '  '[/cyan]
""",
    3: """
[bold red]       .--.
    .-(    ).
   (___.__)__)
      /  /
     /_ /
      /[/bold red]
"""
}

def search_city(city_name):
    """Resolve city name to coordinates via free Open-Meteo Geocoding API."""
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city_name, "count": 1, "language": "en", "format": "json"}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        results = response.json().get("results", [])
        if results:
            res = results[0]
            return res.get("latitude"), res.get("longitude"), res.get("name")
    except Exception as e:
        pass
    return None, None, None

def fetch_weather(lat, lon):
    """Fetch live & forecast data from free Open-Meteo API."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "timezone": "auto",
        "forecast_days": 1
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

def map_weather_code(code):
    """Maps Open-Meteo weather codes to our simpler 0-3 categories."""
    if code in [0, 1]:
        return 0  # Sunny/Clear
    elif code in [2, 3, 45, 48]:
        return 1  # Cloudy
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return 2  # Rainy
    else:
        return 3  # Stormy/Thunder

def shimmer_text(text, frame):
    """Generate a smooth shimmer effect where colors rotate across the characters."""
    colors = ["bold red", "bold yellow", "bold red", "bold yellow"]
    res = []
    for idx, c in enumerate(text):
        if c.isspace():
            res.append(c)
        else:
            col = colors[(idx + frame) % len(colors)]
            res.append(f"[{col}]{c}[/{col}]")
    return "".join(res)


def wave_text(text, frame):
    """Gentle color wave on text only—emoji pass through untouched."""
    colors = ["bold bright_cyan", "bold cyan"]
    # Split but keep emoji-tagged segments uncolored
    result = []
    words = text.split()
    
    for idx, word in enumerate(words):
        # Skip coloring any word that contains non-ASCII (emoji will be untouched)
        is_ascii = all(ord(c) < 128 for c in word)
        if is_ascii:
            wave = frame % 2
            color = colors[wave]
            result.append(f"[{color}]{word}[/{color}]")
        else:
            result.append(word)
    return " ".join(result)


def pulse_icon(icon_frames, frame):
    """Cycles through icon frames for subtle pulsing."""
    return icon_frames[frame % len(icon_frames)]


# Animated branding frames - rotating weather/tech symbols
BRAND_ICONS = [
    "[bold bright_yellow]⛅[/bold bright_yellow]",
    "[bold bright_cyan]🌤️[/bold bright_cyan]",
    "[bold bright_magenta]🌦️[/bold bright_magenta]",
    "[bold bright_blue]🌩️[/bold bright_blue]"
]

# Pulse dots for loading indicator
PULSE_DOTS = [
    "[bold green]●[/bold green]",
    "[bold green]○[/bold green]",
    "[bold green]◐[/bold green]",
    "[bold green]○[/bold green]"
]


# AI Brain Icon Frames - animated ASCII brain/neural network effect
AI_ICON_FRAMES = [
    """
    [bold cyan]   ╔═╗┬ ┬┌─┐┌─┐
    ║  ├─┤├┤ │ │
    ╚═╝┴ ┴└─┘└─┘[/bold cyan]
    """,
    """
    [bold cyan]   ╔═╗┌─┐┬─┐
    ║  │ │├┬┘
    ╚═╝└─┘┴└─[/bold cyan]
    """,
    """
    [bold cyan]   ╔══╗ ┌─┐
    ║╔╗║ │ │
    ╚╝╚╝ └─┘[/bold cyan]
    """,
    """
    [bold cyan]   ╔══╗ ╔═╗
    ║╔╗║ ║ ║
    ╚╝╚╝ ╚═╝[/bold cyan]
    """
]

# Neural network pulse effect for ML loading
NEURAL_FRAMES = [
    "[bold magenta]● ○ ○ ○[/bold magenta]",
    "[bold magenta]○ ● ○ ○[/bold magenta]",
    "[bold magenta]○ ○ ● ○[/bold magenta]",
    "[bold magenta]○ ○ ○ ●[/bold magenta]"
]

# Location resolution animation frames
LOCATION_FRAMES = [
    "[bold blue]🌍[/bold blue]",
    "[bold blue]📍[/bold blue]",
    "[bold blue]🗺️ [/bold blue]",
    "[bold blue]⚡[/bold blue]"
]

class AILoadingAnimator:
    """Sophisticated loading animation with AI-themed icon and status progression."""
    
    def __init__(self, console, city_name):
        self.console = console
        self.city_name = city_name
        self.frame_index = 0
        self.ml_frame_index = 0
        self.location_frame_index = 0
        
    def get_ai_icon(self):
        """Get current AI icon frame."""
        frame = AI_ICON_FRAMES[self.frame_index % len(AI_ICON_FRAMES)]
        self.frame_index += 1
        return frame
    
    def get_neural_pulse(self):
        """Get current neural network pulse frame."""
        pulse = NEURAL_FRAMES[self.ml_frame_index % len(NEURAL_FRAMES)]
        self.ml_frame_index += 1
        return pulse
    
    def get_location_icon(self):
        """Get current location tracking icon."""
        icon = LOCATION_FRAMES[self.location_frame_index % len(LOCATION_FRAMES)]
        self.location_frame_index += 1
        return icon
    
    def create_loading_screen(self, phase, subtext=""):
        """Create a rich Live-renderable loading screen."""
        ai_icon = self.get_ai_icon()
        neural = self.get_neural_pulse()
        loc_icon = self.get_location_icon()
        
        from rich.align import Align
        from rich.panel import Panel
        from rich.text import Text
        
        # Main loading content
        loading_text = f"\n[bold cyan]AfterWeather AI[/bold cyan]\n"
        loading_text += f"[dim]{subtext}[/dim]\n\n"
        loading_text += f"{ai_icon}\n\n"
        loading_text += f"{neural}  [bold white]Processing neural patterns...[/bold white]\n"
        loading_text += f"{loc_icon}  [bold blue]Resolving: {self.city_name}[/bold blue]"
        
        return Panel(
            Align.center(loading_text),
            title="[bold green]● AI FORECAST ENGINE[/bold green]",
            border_style="bright_cyan",
            padding=(1, 2)
        )
    
    def create_phase_screen(self, phase, message, icon=""):
        """Create a phase-specific loading screen."""
        shimmer_title = shimmer_text("AfterWeather AI Loading", self.frame_index)
        
        content = f"\n{icon} [bold white]{message}[/bold white]\n"
        if phase == "geocoding":
            content += f"\n[dim]Converting location to coordinates...[/dim]"
            content += f"\n[dim]Querying Open-Meteo Geocoding API[/dim]"
        elif phase == "ml_load":
            content += f"\n[dim]Loading RandomForest models...[/dim]"
            content += f"\n[dim]Restoring weather pattern weights[/dim]"
        elif phase == "init":
            content += f"\n[dim]Preparing real-time forecast loop...[/dim]"
            content += f"\n[dim]Connecting to live weather streams[/dim]"
        
        return Panel(
            Align.center(content),
            title=f"[bold yellow]{shimmer_title}[/bold yellow]",
            border_style="cyan",
            padding=(1, 2)
        )


import argparse

def main():
    parser = argparse.ArgumentParser(
        description="AfterWeather: Stunning real-time tracking combined with local machine learning",
        add_help=True
    )
    parser.add_argument("-c", "--city", type=str, default=None, help="City name to track")
    args, unknown = parser.parse_known_args()
    
    city_name_input = args.city
    
    if not city_name_input:
        console.clear()
        
        # Static banner on startup
        console.print(Panel(Align.center(
            f"[bold cyan]*** AfterWeather ***[/bold cyan]\n"
            "[dim]Stunning real-time tracking combined with local machine learning[/dim]"
        ), border_style="cyan"))
        
        city_name_input = Prompt.ask("Enter city name to fetch (e.g., San Francisco)")
        if not city_name_input:
            city_name_input = "Mumbai"
    
    # Initialize AI loading animator
    animator = AILoadingAnimator(console, city_name_input)
    
    with Live(refresh_per_second=10) as live:
        # Phase 0: Initial AI activation screen
        for _ in range(8):
            live.update(animator.create_loading_screen("init", "Initializing AI Weather Engine..."))
            time.sleep(0.15)
        
        # Step 1: Resolving location - animated phase screen
        for _ in range(12):
            live.update(animator.create_phase_screen(
                "geocoding",
                f"Resolving location for '{city_name_input}'",
                icon="[bold blue]🔍[/bold blue]"
            ))
            time.sleep(0.12)
        
        found_lat, found_lon, found_name = search_city(city_name_input)
        
        if found_lat is not None and found_lon is not None:
            lat, lon, loc_name = found_lat, found_lon, found_name
            loc_status = f"[bold green]✓[/bold green] [bold white]Location resolved: {loc_name} ({lat:.2f}°, {lon:.2f}°)[/bold white]"
        else:
            lat, lon, loc_name = 19.076, 72.877, "Mumbai"
            loc_status = "[bold red]✗[/bold red] [bold white]Could not resolve city. Using Mumbai as default.[/bold white]"
        
        # Step 2: Loading ML patterns with animated neural pulse
        for _ in range(15):
            neural_icon = animator.get_neural_pulse()
            ml_loading = Panel(
                Align.center(
                    f"\n{neural_icon}  [bold yellow]Loading localized Machine Learning patterns...[/bold yellow]\n"
                    f"[dim]Training RandomForest on weather history...[/dim]"
                ),
                title="[bold magenta]NEURAL NETWORK ACTIVE[/bold magenta]",
                border_style="bright_magenta",
                padding=(1, 2)
            )
            live.update(Group(loc_status, ml_loading))
            time.sleep(0.1)
        
        ml = WeatherML()
        ml.load_model()
        
        ml_status = f"[bold green]✓[/bold green] [bold white]ML model loaded—pattern recognition ready[/bold white]"
        
        # Step 3: Final initialization
        for _ in range(10):
            init_icon = "[bold cyan]⚡[/bold cyan]" if _ % 2 == 0 else "[bold cyan]🔄[/bold cyan]"
            final_loading = Panel(
                Align.center(
                    f"\n{init_icon}  [bold cyan]Initializing real-time forecast loop...[/bold cyan]\n"
                    f"[dim]Connecting to Open-Meteo API streams...[/dim]"
                ),
                title="[bold green]SYSTEM READY[/bold green]",
                border_style="green",
                padding=(1, 2)
            )
            live.update(Group(loc_status, ml_status, final_loading))
            time.sleep(0.15)

    frame_index = 0
    cached_api_data = None
    last_fetch_time = 0

    # Continuously display live results with refreshing/animated UI
    with Live(console=console, screen=True, refresh_per_second=2) as live:
        while True:
            current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Fetch real-time API data every 60 seconds or initially
            now_ts = time.time()
            if not cached_api_data or (now_ts - last_fetch_time > 60):
                new_data = fetch_weather(lat, lon)
                if new_data:
                    cached_api_data = new_data
                    last_fetch_time = now_ts

            if not cached_api_data:
                live.update(Panel("[bold red]Weather data fetching failed. Retrying...[/bold red]"))
                time.sleep(1)
                continue

            curr = cached_api_data.get("current", {})
            live_temp = curr.get("temperature_2m", 0)
            live_humidity = curr.get("relative_humidity_2m", 0)
            live_wind = curr.get("wind_speed_10m", 0)
            live_code = curr.get("weather_code", 0)

            month = datetime.now().month
            hour = datetime.now().hour

            # Predict local condition using ML model
            predicted_cond, cond_id, predicted_next_temp = ml.predict(month, hour, live_temp, live_humidity, live_wind)

            # Map the direct API weather code to our category
            api_cond_id = map_weather_code(live_code)
            api_cond_label = ml.weather_labels.get(api_cond_id, "Clear")

            # Retrieve direct static weather art frames
            live_art = ART_ANIMATIONS.get(api_cond_id, ART_ANIMATIONS[0])
            ml_art = ART_ANIMATIONS.get(cond_id, ART_ANIMATIONS[0])

            # Prepare real-time visual output Panel
            live_text = f"\n[bold yellow]Condition:[/bold yellow] {api_cond_label}\n" \
                        f"[bold cyan]Temperature:[/bold cyan] {live_temp}°C\n" \
                        f"[bold magenta]Humidity:[/bold magenta] {live_humidity}%\n" \
                        f"[bold blue]Wind Speed:[/bold blue] {live_wind} km/h\n"

            live_panel = Panel(Columns([Align.center(live_art), Align.center(live_text)]), 
                               title=f"[bold green]LIVE WEATHER NOW[/bold green]", 
                               border_style="green", expand=True)

            ml_text = f"\n[bold yellow]ML Predicted Behavior:[/bold yellow] {predicted_cond}\n" \
                      f"[bold cyan]Next Hour Temp Estimate:[/bold cyan] {predicted_next_temp:.1f}°C\n" \
                      f"[bold white]Localized Features & Factors:[/bold white]\n" \
                      f" • Current Month: {month}\n" \
                      f" • Current Hour: {hour}:00\n"

            ml_panel = Panel(Columns([Align.center(ml_art), Align.center(ml_text)]), 
                             title="[bold magenta]MACHINE LEARNING FORECAST (LOCALIZED)[/bold magenta]", 
                             border_style="magenta", expand=True)

            # Hourly 24h table display
            table = Table(title_style="bold underline", 
                          border_style="cyan", 
                          show_lines=True)
            table.add_column("Time", style="dim", justify="center")
            table.add_column("Temp (°C)", style="cyan", justify="center")
            table.add_column("Humidity (%)", style="magenta", justify="center")
            table.add_column("Wind (km/h)", style="blue", justify="center")
            table.add_column("Forecast (API)", style="yellow", justify="center")
            table.add_column("Local ML Forecast", style="bold green", justify="center")

            hourly = cached_api_data.get("hourly", {})
            if hourly:
                times = hourly.get("time", [])
                temps = hourly.get("temperature_2m", [])
                humidities = hourly.get("relative_humidity_2m", [])
                winds = hourly.get("wind_speed_10m", [])
                codes = hourly.get("weather_code", [])

                for i in range(0, min(24, len(times)), 3):
                    t_str = times[i].split("T")[-1] if "T" in times[i] else times[i]
                    api_c = codes[i] if i < len(codes) else 0
                    api_cat = ml.weather_labels.get(map_weather_code(api_c), "Clear")

                    ml_p_cond, _, _ = ml.predict(month, int(t_str.split(":")[0]), temps[i], humidities[i], winds[i])
                    table.add_row(
                        t_str, 
                        f"{temps[i]}", 
                        f"{humidities[i]}", 
                        f"{winds[i]}", 
                        api_cat, 
                        ml_p_cond
                    )

            # Combined interactive Live Console Display containing clock on top
            # Animated branding with icon pulse
            brand_icon = pulse_icon(BRAND_ICONS, frame_index // 5)
            brand_wave = wave_text("AfterWeather REAL-TIME FORECAST", frame_index)
            pulse_dot = pulse_icon(PULSE_DOTS, frame_index // 3)
            
            # Animated top header with dynamic timestamp color
            time_color = "bold bright_yellow" if frame_index % 10 < 5 else "bold yellow"
            header_content = Group(
                Text.from_markup(f"{brand_icon}  {brand_wave}", justify="center"),
                Text.from_markup(f"{pulse_dot}  [{time_color}]Current Time:[/{time_color}] {current_time_str}  │  [bold bright_green]Location:[/bold bright_green] {loc_name}", justify="center")
            )
            top_header = Panel(
                header_content,
                border_style="bright_cyan",
                padding=(0, 2),
                expand=True
            )

            # Final live display group
            combined_display = Group(
                top_header,
                live_panel,
                ml_panel,
                Align.center(table),
                Text("Refreshing real-time & forecast data continuously. Press Ctrl+C to terminate.", style="dim", justify="center")
            )

            live.update(combined_display)

            frame_index += 1
            time.sleep(0.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]CLI terminated by user. Stay safe in the weather![/bold red]")
