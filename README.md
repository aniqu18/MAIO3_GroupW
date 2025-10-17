# MAIO-3 — Virtual Diabetes Clinic Triage

This repository contains a small example ML project for a virtual diabetes clinic triage. It trains a simple SVR model on the scikit-learn diabetes dataset, exposes a small FastAPI model-serving API, and includes CI/CD workflows that lint, train, test, build a container, and publish releases.

## Contents

- `app/` — FastAPI application and packaged artifacts (model, metrics).
	- `app/api.py` — FastAPI application (endpoints: `/health`, `/predict`).
	- `app/main.py` — convenience runner for local development.
	- `app/artifacts/` — default place for `model.pkl` and `metrics.json` used by the API.
- `train/train.py` — training script that produces `artifacts/model.pkl` and `artifacts/metrics.json`.
- `.github/workflows/ci.yml` — GitHub Actions workflow: lint -> train -> test -> build docker image (see notes below).
- `.github/workflows/release.yml` — GitHub Actions release workflow: retrain for release, build & push container, run smoke tests and create a GitHub Release.
- `dockerfile` — multi-stage Dockerfile used to build a production image.
- `test/` — integration tests targeting the running API (adjust `BASE_URL` before running locally).
- 'changelog.md' - 

## Quick Setup 

Run the following command

```bash
docker run -p 8000:8000 ghcr.io/ally-ha/MAIO3_GroupW:v1
```

## Full local Setup

Requirements

- Python 3.11 (the CI and Dockerfile use 3.11)
- pip

Install dependencies

```bash
python -m pip install -r app/requirements.txt
```

Train the model (creates model and metrics)

```bash
# from repository root
python train/train.py --model-out app/artifacts/model.pkl --metrics-out app/artifacts/metrics.json
```

The training script trains an SVR on the scikit-learn diabetes dataset and writes two artifacts:

- `app/artifacts/model.pkl` — the pickled sklearn pipeline used by the API
- `app/artifacts/metrics.json` — evaluation metrics (RMSE, train/test sizes, hyperparams)

Serve the model API

Start the API with uvicorn (recommended):

```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
```

By default the API looks for the model at `app/artifacts/model.pkl`.

Health and prediction examples

Check health:

```bash
curl http://localhost:8000/health
# => {"status": "ok"}
```

Make a prediction (JSON body must include a `features` array of floats):

```bash
curl -X POST http://localhost:8000/predict \
	-H "Content-Type: application/json" \
	-d '{"features": [0.05,0.05,0.02,0.01,-0.03,-0.04,-0.04,-0.02,0.01,0.02]}'
# => {"risk_score": 123.45}, response 200
```

Note: the API will return HTTP 503 if the model is not yet loaded.

## Docker

Build the image (uses the repository `dockerfile`):

```bash
docker build -t diabetes-api .
```

Run the container (make sure the container has access to the model):

```bash
# If model is in app/artifacts inside the image, this is enough:
docker run -p 8000:8000 diabetes-api
```

The Dockerfile exposes port `8000` and defines a healthcheck that queries `/health`.

## Testing

Integration tests live in `test/` and are written to target a running API instance. The tests use a `BASE_URL` constant — update it to point at your locally running server (for example, `http://localhost:8000`) before running tests locally.

Run tests with pytest:

```bash
# update BASE_URL in test/tests_api.py to http://localhost:8000 (or set an environment-aware test)
pytest test/tests_api.py
```

Because the repository tests are integration-style, CI starts the API (or runs the container) and then runs the tests against it.

## CI / Release workflows

- `.github/workflows/ci.yml` (GitHub Actions) performs these stages:
	1. Lint with `flake8`.
	2. Install dependencies and train the model (artifact verification).
	3. Start the API and run the `test/` suite.
	4. Build a Docker image and run a container smoke test.

- `.github/workflows/release.yml` triggers on version tags (`v*.*`). It retrains the model for the release tag, displays metrics, builds and pushes a container image to the GitHub Container Registry, runs smoke tests against the pushed image, and creates a GitHub Release including `metrics.json` in the release assets.

These workflows run on Python 3.11 and rely on the repository producing `model.pkl` and `metrics.json` as verification steps.

## Project structure (summary)

```
.
├─ app/
│  ├─ api.py          # FastAPI app
│  ├─ main.py         # optional runner
│  └─ artifacts/      # model.pkl, metrics.json
├─ train/
│  └─ train.py        # training script
├─ test/
│  └─ tests_api.py    # integration tests (configure BASE_URL)
├─ dockerfile         # multi-stage Dockerfile
├─ .github/workflows/
│  ├─ ci.yml
│  └─ release.yml
├─ CHANGELOG.md
├─ README.md
```

## Notes & troubleshooting

- If the API reports the model is not loaded, check `MODEL_PATH` and ensure `model.pkl` exists at the expected path.