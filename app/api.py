from fastapi import FastAPI, HTTPException
import pickle
import numpy as np
from pydantic import BaseModel
import os

app = FastAPI(title="Virtual Diabetes Clinic Triage API")

MODEL_PATH = os.environ.get("MODEL_PATH", "app/artifacts/model.pkl")
model = None


class PatientData(BaseModel):
    features: list[float]


@app.on_event("startup")
def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
        print("✅ Model loaded successfully")
    else:
        print(f"⚠️ Model not found at {MODEL_PATH}")


@app.get("/health")
def health():
    if model is None:
        return {"status": "starting"}
    return {"status": "ok"}


@app.post("/predict")
def predict(data: PatientData):
    if model is None:
        raise HTTPException(status_code=503, detail="model not loaded")

    try:
        X = np.array(data.features).reshape(1, -1)
        y_pred = model.predict(X)
        return {"risk_score": float(y_pred[0])}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
