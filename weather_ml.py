import os
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split

MODEL_DIR = "models"
MODEL_FILE = os.path.join(MODEL_DIR, "weather_model.pkl")

class WeatherML:
    def __init__(self):
        self.clf = None
        self.reg = None
        self.is_trained = False
        os.makedirs(MODEL_DIR, exist_ok=True)
        self.weather_labels = {
            0: "Sunny/Clear",
            1: "Cloudy",
            2: "Rainy",
            3: "Stormy/Thunder"
        }

    def generate_synthetic_data(self, num_days=365):
        """Generates realistic synthetic data for a single location."""
        np.random.seed(42)
        records = []
        
        # Monthly baselines for a generic specific location
        monthly_temp = [12, 14, 18, 22, 26, 30, 32, 31, 28, 24, 18, 14]
        monthly_humidity = [65, 60, 55, 50, 45, 55, 65, 70, 60, 55, 60, 65]
        
        for day in range(num_days):
            month = (day // 30) % 12 + 1
            base_temp = monthly_temp[month - 1]
            base_humidity = monthly_humidity[month - 1]
            
            for hour in range(24):
                # Hourly variations
                hour_offset = -4 * np.cos((hour - 4) * np.pi / 12)  # cooler at night, warmer at 4 PM
                temp = base_temp + hour_offset + np.random.normal(0, 2)
                
                # Humidity varies inversely with temperature
                humidity = base_humidity - (hour_offset * 1.5) + np.random.normal(0, 5)
                humidity = np.clip(humidity, 10, 100)
                
                # Wind speed
                wind_speed = 10 + np.abs(np.random.normal(0, 5)) + (5 if month in [6, 7, 8] else 0)
                
                # Assign condition based on temperature, humidity, and month (e.g., monsoon months 6,7,8)
                if humidity > 85 and temp > 28:
                    condition = 3  # Stormy/Thunder
                elif humidity > 70:
                    condition = 2  # Rainy
                elif humidity > 50:
                    condition = 1  # Cloudy
                else:
                    condition = 0  # Sunny/Clear
                
                records.append({
                    "month": month,
                    "hour": hour,
                    "temperature": temp,
                    "humidity": humidity,
                    "wind_speed": wind_speed,
                    "condition": condition,
                    "next_hour_temp": temp + np.random.normal(0, 0.5)
                })
                
        return pd.DataFrame(records)

    def train_and_save(self, df=None):
        """Train models on synthetic or imported data, then save to pkl."""
        if df is None:
            df = self.generate_synthetic_data()
            
        X = df[["month", "hour", "temperature", "humidity", "wind_speed"]].values
        y_cond = df["condition"].values
        y_temp = df["next_hour_temp"].values
        
        self.clf = RandomForestClassifier(n_estimators=100, random_state=42)
        self.reg = RandomForestRegressor(n_estimators=100, random_state=42)
        
        self.clf.fit(X, y_cond)
        self.reg.fit(X, y_temp)
        self.is_trained = True
        
        with open(MODEL_FILE, "wb") as f:
            pickle.dump({"clf": self.clf, "reg": self.reg}, f)

    def load_model(self):
        """Load trained model or auto-train if missing."""
        if os.path.exists(MODEL_FILE):
            try:
                with open(MODEL_FILE, "rb") as f:
                    data = pickle.load(f)
                    self.clf = data["clf"]
                    self.reg = data["reg"]
                    self.is_trained = True
            except Exception:
                self.train_and_save()
        else:
            self.train_and_save()

    def predict(self, month, hour, temp, humidity, wind_speed):
        """Predict current condition code/label and future temperature."""
        if not self.is_trained:
            self.load_model()
            
        features = np.array([[month, hour, temp, humidity, wind_speed]])
        cond_id = self.clf.predict(features)[0]
        predicted_cond = self.weather_labels.get(cond_id, "Sunny/Clear")
        predicted_next_temp = self.reg.predict(features)[0]
        
        return predicted_cond, cond_id, predicted_next_temp
