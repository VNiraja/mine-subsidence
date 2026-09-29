# AI-Enabled Mine Subsidence Monitoring System

An AI-based system for monitoring, predicting and providing
early warnings for underground mine subsidence.

## Architecture

The live Wokwi demo follows this path:

`data/raw/insar/subsidence_raw.csv`
-> `src/data/load_data.py` (`load_insar`)
-> `src/features/feature_engineering.py` (`prepare_features`)
-> `src/inference/predict.py` (`predict_latest`, XGBoost/Random Forest/Attention)
-> `backend/main.py` (`GET /predict/latest`)
-> `esp32/main.py` (polls risk every 5 seconds)
-> Wokwi LEDs and buzzer.

The seismic file is loaded for response metadata only; it is not used by the
current trained models. The ESP32 currently displays the prediction from the
existing InSAR CSV; it does not submit Wokwi sensor measurements.

The separate offline training-data path is:

`data/raw/insar/*.csv`
-> `src/data/preprocess.py`
-> `data/processed/insar_cleaned.csv`
-> `src/features/feature_engineering.py`
-> `data/features/features.csv`
-> training scripts under `src/training/`.


## Models

1. Random Forest
2. XGBoost
3. Attention / Transformer


## Data

The system uses:

- InSAR data
- Seismic data
- IoT sensor data for live/demo inference


## Running

Install dependencies:

pip install -r requirements.txt


Run preprocessing:

python src/data/preprocess.py


Create features:

python src/features/feature_engineering.py


Train Random Forest:

python src/training/train_random_forest.py


Train XGBoost:

python src/training/train_xgboost.py


Train Attention model:

python src/training/train_attention.py


Start API:

uvicorn backend.main:app --reload


Start dashboard:

streamlit run dashboard/app.py

## Run the Wokwi Demo

Run these commands from the `mine_subsidence_ai` project directory. The API
and model files must be available before starting the ESP32 simulation.

1. Start FastAPI in a terminal:

        `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`

2. Check `http://127.0.0.1:8000/predict/latest`. A successful response
        includes `risk`, `confidence`, and `probabilities`. The current inference
        reads the latest observation from `data/raw/insar/subsidence_raw.csv`.

3. Wokwi runs in the browser, so expose the local API with a tunnel, for
        example `npx localtunnel --port 8000`. Keep the tunnel process running.
        Copy its HTTPS URL and replace the host in `SERVER_URL` in
        `esp32/main.py`, keeping `/predict/latest` at the end.

4. Open a Wokwi MicroPython ESP32 project, use the code from
        `esp32/main.py`, and wire active-high LEDs to GPIO 12 (green), GPIO 14
        (yellow), GPIO 27 (red), and a buzzer to GPIO 26. Connect LED cathodes and
        the buzzer ground to GND; use a current-limiting resistor for each LED.

5. Start the Wokwi simulation. It connects to `Wokwi-GUEST`, requests the
        latest API prediction every 5 seconds, and prints the risk/confidence in
        the simulator console. LOW lights green, MEDIUM lights yellow, and HIGH
        lights red and turns on the buzzer. A failed request leaves the outputs off.

For manual model input, `POST /predict` expects all 18 numeric fields listed
in `FEATURES` in `src/features/feature_engineering.py`. The current Wokwi code
does not call that endpoint; it calls `GET /predict/latest` instead. Do not
use a public tunnel for sensitive or production data.