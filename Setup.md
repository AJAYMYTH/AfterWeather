# ⚙️ AfterWeather Setup Guide

This guide will walk you through setting up AfterWeather on your local machine for a clean installation.

## Prerequisites
- Python 3.8 or higher.
- Git (optional, for cloning).

---

## 🛠️ Installation Steps

### Step 1: Clone the Repository
Clone the repository to your local computer:
```bash
git clone https://github.com/AJAYMYTH/AfterWeather.git
cd AfterWeather
```

### Step 2: Set Up a Virtual Environment (Recommended)
It's recommended to install dependencies inside a fresh virtual environment:
```bash
# On Windows
python -m venv .venv
.venv\Scripts\activate

# On Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install the Package
To make the `afterweather` command accessible anywhere on your computer, install the package in **editable mode**:
```bash
pip install -e .
```

### Step 4: Verify Installation
Verify that the `afterweather` command works correctly by checking the help documentation:
```bash
afterweather --help
```

---

## 💻 Usage Examples

Run AfterWeather interactively or query directly using arguments:

```bash
# Interactive Mode
afterweather

# Direct City Target
afterweather -c "London"
```
