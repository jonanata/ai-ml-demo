"""Traffic accident risk predictor module (copied to c3).

This is a copy of the reusable class encapsulating loading, preprocessing,
training a RandomForestClassifier, fetching forecasts and predicting accident risk.
"""

from typing import Optional
import pandas as pd
import numpy as np
import requests
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt


class TrafficAccidentRiskPredictor:
    """Encapsulate data load, preprocess, train, forecast fetch and prediction.

    Usage:
        prep = TrafficAccidentRiskPredictor(weather_csv, accident_csv)
        prep.load_data()
        prep.preprocess()
        prep.train_model()
        forecast = prep.fetch_forecast()
        forecast = prep.predict_risk(forecast)

    Notes:
        - Methods avoid side-effects where practical and return DataFrames.
        - Trained model is stored in `self.model` after `train_model()`.
    """

    def __init__(
        self,
        weather_csv: str,
        accident_csv: str,
        target_accuracy: float = 0.85,
        max_attempts: int = 100,
        random_state: Optional[int] = 42,
    ):
        self.weather_csv = weather_csv
        self.accident_csv = accident_csv
        self.target_accuracy = target_accuracy
        self.max_attempts = max_attempts
        self.random_state = random_state

        self.weather_df: Optional[pd.DataFrame] = None
        self.accident_df: Optional[pd.DataFrame] = None
        self.merged_df: Optional[pd.DataFrame] = None
        self.features: Optional[pd.DataFrame] = None
        self.target: Optional[pd.Series] = None

        self.model: Optional[RandomForestClassifier] = None
        self.best_accuracy: float = 0.0

    def load_data(self) -> None:
        """Load CSV files into DataFrames and store them on the instance."""
        self.weather_df = pd.read_csv(self.weather_csv, parse_dates=["date"]) 
        self.accident_df = pd.read_csv(self.accident_csv, parse_dates=["Collision Date"]) 

    def preprocess(self, year_start: int = 2023, year_end_exclusive: int = 2025) -> pd.DataFrame:
        """Filter by years, aggregate accidents per day, merge with weather, and create features.

        Returns the merged DataFrame.
        """
        if self.weather_df is None or self.accident_df is None:
            raise RuntimeError("Data not loaded. Call load_data() first.")

        weather_df = self.weather_df.copy()
        accident_df = self.accident_df.copy()

        weather_df = weather_df[(weather_df["date"].dt.year >= year_start) & (weather_df["date"].dt.year < year_end_exclusive)]
        accident_df = accident_df[(accident_df["Collision Date"].dt.year >= year_start) & (accident_df["Collision Date"].dt.year < year_end_exclusive)]

        accident_daily = accident_df.groupby(accident_df["Collision Date"].dt.date).size().reset_index(name="accident_count")
        accident_daily["date"] = pd.to_datetime(accident_daily["Collision Date"]) 

        merged_df = pd.merge(weather_df, accident_daily[["date", "accident_count"]], on="date", how="left")
        merged_df["accident_count"] = merged_df["accident_count"].fillna(0)

        merged_df["is_rainy"] = merged_df.get("rain", 0) > 1
        merged_df["is_snowy"] = merged_df.get("snow", 0) > 0
        merged_df["temp_category"] = pd.cut(merged_df.get("avg_temperature", 0), bins=[-10, 0, 10, 20, 30], labels=["Freezing", "Cold", "Mild", "Warm"]) 

        self.merged_df = merged_df
        self.features = merged_df[["avg_temperature", "is_rainy", "is_snowy"]]
        self.target = (merged_df["accident_count"] > 0).astype(int)

        return merged_df

    def plot_accidents_by_temp_category(self) -> None:
        """Simple Matplotlib bar chart of average accidents per temperature category."""
        if self.merged_df is None:
            raise RuntimeError("No merged data. Run preprocess() first.")

        plt.figure(figsize=(8, 5))
        self.merged_df.groupby("temp_category")["accident_count"].mean().plot(kind="bar", color="skyblue")
        plt.title("Average Daily Accidents by Temperature Category")
        plt.ylabel("Average Accident Count")
        plt.xlabel("Temperature Category")
        plt.tight_layout()
        plt.show()

    def train_model(self, test_size: float = 0.2) -> RandomForestClassifier:
        """Train RandomForestClassifier with random hyperparameter search until target accuracy or max_attempts.

        Returns the best trained model.
        """
        if self.features is None or self.target is None:
            raise RuntimeError("Features/target not prepared. Run preprocess() first.")

        X_train, X_test, y_train, y_test = 
        train_test_split(self.features, self.target, test_size=test_size, random_state=self.random_state)

        best_accuracy = 0.0
        best_model: Optional[RandomForestClassifier] = None
        attempts = 0

        rng = np.random.default_rng(self.random_state)

        while best_accuracy < self.target_accuracy and attempts < self.max_attempts:
            attempts += 1
            n_estimators = int(rng.integers(100, 200))
            max_depth = rng.choice([None, 10, 20, 30])
            max_features = rng.choice(["sqrt", "log2", None])

            model = RandomForestClassifier(
                n_estimators=n_estimators,
                max_depth=max_depth,
                max_features=max_features,
                random_state=attempts,
            )
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            accuracy = float(accuracy_score(y_test, y_pred))

            if accuracy > best_accuracy:
                best_accuracy = accuracy
                best_model = model

        if best_model is None:
            # fallback: train a default model
            best_model = RandomForestClassifier(random_state=self.random_state)
            best_model.fit(X_train, y_train)
            best_accuracy = float(accuracy_score(y_test, best_model.predict(X_test)))

        self.model = best_model
        self.best_accuracy = best_accuracy
        return best_model

    def fetch_forecast(self, latitude: float = 49.2827, longitude: float = -123.1207) -> pd.DataFrame:
        """Fetch 14-day forecast from Open-Meteo and return a DataFrame with features.

        Returns columns: date, avg_temperature, is_rainy, is_snowy
        """
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "America/Vancouver",
        }
        resp = requests.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        df = pd.DataFrame(data.get("daily", {}))
        if df.empty:
            return pd.DataFrame(columns=["date", "avg_temperature", "is_rainy", "is_snowy"])

        df["avg_temperature"] = (df["temperature_2m_max"] + df["temperature_2m_min"]) / 2
        df["is_rainy"] = df["precipitation_sum"] > 1
        df["is_snowy"] = False
        df["date"] = pd.to_datetime(df["time"]) 
        return df[["date", "avg_temperature", "is_rainy", "is_snowy"]]

    def predict_risk(self, forecast_df: pd.DataFrame) -> pd.DataFrame:
        """Predict accident risk (0/1) for a forecast DataFrame using trained model.

        Returns a new DataFrame with an `accident_risk` column.
        """
        if self.model is None:
            raise RuntimeError("Model not trained. Call train_model() first.")

        features = forecast_df[["avg_temperature", "is_rainy", "is_snowy"]]
        preds = self.model.predict(features)
        out = forecast_df.copy()
        out["accident_risk"] = preds
        return out

    def show_risk_near_date(self, forecast_df: pd.DataFrame, selected_date: str) -> pd.DataFrame:
        """Return a 3-day window centered on `selected_date` from the forecast DataFrame."""
        selected = pd.to_datetime(selected_date)
        mask = (forecast_df["date"] >= selected - pd.Timedelta(days=1)) & (forecast_df["date"] <= selected + pd.Timedelta(days=1))
        return forecast_df.loc[mask, ["date", "avg_temperature", "is_rainy", "accident_risk"]]

    def plot_risk_window(self, df: pd.DataFrame) -> None:
        """Plot accident risk, temperature and annotate rain for a small DataFrame."""
        if df.empty:
            print("No data to plot")
            return

        dates = df["date"].dt.strftime("%b %d")
        risks = df["accident_risk"]
        temps = df["avg_temperature"]
        rain_flags = df["is_rainy"]

        fig, ax1 = plt.subplots(figsize=(10, 5))
        bars = ax1.bar(dates, risks, color=["red" if r else "green" for r in risks])
        ax1.set_ylabel("Accident Risk (1=High, 0=Low)")
        ax1.set_ylim(0, 1.5)
        ax1.set_title("Traffic Accident Risk Around Selected Date")

        ax2 = ax1.twinx()
        ax2.plot(dates, temps, color="blue", marker="o", label="Avg Temp (°C)")
        ax2.set_ylabel("Avg Temperature (°C)", color="blue")
        ax2.tick_params(axis="y", labelcolor="blue")

        for i, rain in enumerate(rain_flags):
            if rain:
                ax1.text(i, 1.05, "Rain", ha="center", fontsize=10, color="gray")

        plt.tight_layout()
        plt.show()
