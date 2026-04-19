# Traffic Accident Risk Predictor 

This folder contains a copy of the predictor module and demo.

Files:
- `traffic_accident_risk.py` — class implementation
- `run_demo.py` — runner that looks for `data/` relative to this folder
- `requirements.txt` — dependency list (same as project root)
- `.venv/README.txt` — explanation about virtualenv copying

How to use:

1. Create a virtual environment in this folder:

```
cd <your_project_path>/ai-ml-demo/c3
python -m venv .venv
./.venv/Scripts/Activate.ps1
pip install -r requirements.txt
```

2. Ensure the `data` folder exists under `c3` with the CSV files:
   - `data/weatherstats_vancouver_daily.csv`
   - `data/wsdotTrafficCollisionsFS.csv`

3. Run the demo:

```
./.venv/Scripts/python.exe run_demo.py
```

Train-once server behavior
--------------------------

The FastAPI server (`main.py`) trains the `TrafficAccidentRiskPredictor` once at application startup and caches the trained predictor in memory. This makes requests much faster because the heavy training step is not repeated per request. On startup the server will log the best training accuracy. If CSV files are missing at startup, the predictor will not be available and requests will return a 500 error — check the server logs for details.

Run the FastAPI server (recommended for development):

```
cd <your_project_path>/ai-ml-demo/c3
./.venv/Scripts/python.exe -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API endpoint
------------

POST /api/predict_risk

Request JSON body:

{
   "selected_date": "dd-mm-yyyy"
}

Example curl ():

```
curl -X POST "http://127.0.0.1:8000/api/predict_risk" -H "Content-Type: application/json" -d '{"selected_date":"24-09-2025"}'
```

Response: JSON array of rows from `show_risk_near_date`, e.g.:

[
   {"date": "2025-09-23", "avg_temperature": 15.2, "is_rainy": false, "accident_risk": 0},
   {"date": "2025-09-24", "avg_temperature": 14.1, "is_rainy": true, "accident_risk": 1},
   {"date": "2025-09-25", "avg_temperature": 13.8, "is_rainy": false, "accident_risk": 0}
]

Docker
------

The provided `Dockerfile` creates an image and runs the app with Uvicorn. The `data/` folder is excluded from the image via `.dockerignore` so you should bind-mount your host `data/` into the container at runtime.

Build image:

```
cd <your_project_path>/ai-ml-demo/c3
docker build -t accident-risk-api:latest .
```

Run (bind-mount host `data/`):

```
docker run -p 8000:8000 -v <your_project_path>/ai-ml-demo/c3/data:/app/data accident-risk-api:latest
```

This ensures the container sees the CSV files at `/app/data` and the startup training uses the host data.

Troubleshooting
---------------
- If startup logs show "CSV files not found", verify the `data/` path and filenames.
- If startup training takes long, consider precomputing and saving a serialized model; I can add save/load logic if desired.
