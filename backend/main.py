from fastapi import FastAPI
from pydantic import BaseModel

from src.inference.predict import predict_latest as predict_latest_from_data
from src.inference.predict import predict_risk


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Mine Subsidence AI API",
    description="Real-time mine subsidence risk prediction API",
    version="1.0"
)


# ============================================================
# INPUT SCHEMA
# ============================================================

class SensorData(BaseModel):

    tilt: float

    displacement: float

    crack_width: float

    strain: float


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def home():

    return {
        "system": "Mine Subsidence AI",
        "status": "running",
        "model": "XGBoost"
    }


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

# POST /predict accepts a JSON object containing all 18 FEATURES fields,
# validates them with SensorData, then passes them to predict_risk().
# The current Wokwi client instead calls GET /predict/latest below.
@app.post("/predict")
def predict(data: SensorData):

    input_data = data.model_dump()

    result = predict_risk(
        input_data
    )

    return result


# GET /predict/latest -> src/inference/predict.py -> raw InSAR CSV -> model
# probabilities/risk response -> esp32/main.py -> Wokwi LEDs and buzzer.
@app.get("/predict/latest")
def predict_latest():
    return predict_latest_from_data()


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model": "XGBoost"
    }