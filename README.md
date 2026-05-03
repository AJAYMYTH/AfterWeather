# 🌩️ AfterWeather

AfterWeather is a stunning real-time CLI weather tracking tool that combines live meteorological data from Open-Meteo with continuous, localized Machine Learning patterns.

## ✨ Features

- **Dynamic Visuals**: Beautifully styled terminal panels, interactive Claude-style startup loaders, and text shimmer effects built with `Rich`.
- **Live Weather**: Connects to Open-Meteo API for ultra-accurate, localized forecast streaming.
- **On-Device ML**: Predicts future weather categories and conditions locally using localized pattern algorithms.
- **Global Access**: Installable via pip as a console command executable from any terminal.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher

### Installation
Clone the repository and install it locally in editable mode:
```bash
# Install dependencies and link the CLI executable locally
pip install -e .
```

### Usage

Run AfterWeather from your terminal to begin interactive location tracking, or use the `--city` command option:

```bash
# View the help menu
afterweather --help

# Interactively search for any city
afterweather

# Query for a specific city directly
afterweather -c "Mumbai"
```

---
*Stay safe in the weather with AfterWeather.*
