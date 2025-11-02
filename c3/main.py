from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os
import pandas as pd
import logging

from traffic_accident_risk import TrafficAccidentRiskPredictor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Traffic Accident Risk API")

# Add CORS middleware so the frontend running on localhost:3000 can call this API
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use data folder relative to project root (c3)
BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
WEATHER_CSV = os.path.join(DATA_DIR, "weatherstats_vancouver_daily.csv")
ACCIDENT_CSV = os.path.join(DATA_DIR, "wsdotTrafficCollisionsFS.csv")


class PredictRequest(BaseModel):
    selected_date: str  # dd-mm-yyyy


@app.on_event("startup")
def startup_event():
    """Train the predictor once at startup and store on app state."""
    if not os.path.exists(WEATHER_CSV) or not os.path.exists(ACCIDENT_CSV):
        logger.error("CSV files not found in data/ folder; API will fail on requests until present.")
        app.state.predictor = None
        return

    try:
        predictor = TrafficAccidentRiskPredictor(WEATHER_CSV, ACCIDENT_CSV)
        predictor.load_data()
        predictor.preprocess()
        predictor.train_model()
        app.state.predictor = predictor
        logger.info(f"Model trained at startup. Best accuracy: {predictor.best_accuracy:.3f}")
    except Exception as e:
        logger.exception("Failed to train predictor on startup")
        app.state.predictor = None


@app.post("/api/predict_risk")
def predict_risk(req: PredictRequest):
    # Validate date format
    try:
        selected = pd.to_datetime(req.selected_date, dayfirst=True)
    except Exception:
        raise HTTPException(status_code=400, detail="selected_date must be in dd-mm-yyyy format")

    predictor: Optional[TrafficAccidentRiskPredictor] = getattr(app.state, "predictor", None)
    if predictor is None:
        raise HTTPException(status_code=500, detail="Predictor not available. Check server logs.")

    try:
        # Fetch latest forecast and predict
        forecast = predictor.fetch_forecast()
        forecast_with_risk = predictor.predict_risk(forecast)
        window = predictor.show_risk_near_date(forecast_with_risk, selected.strftime('%Y-%m-%d'))

        # Convert to JSON-serializable dict
        result = window.copy()
        result['date'] = result['date'].dt.strftime('%Y-%m-%d')
        return result.to_dict(orient='records')
    except Exception as e:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=str(e))
