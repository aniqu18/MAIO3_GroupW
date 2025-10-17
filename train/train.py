#!/usr/bin/env python3
import argparse
import json
import pickle
import numpy as np
from pathlib import Path

from sklearn.datasets import load_diabetes
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.utils import check_random_state


def train_and_evaluate(X, y, random_state=42):
    """
    Train an linear regression model on diabetes data and evaluate RMSE.
    """
    # train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state
    )

    # build pipeline: scaler + linear regression
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("regressor", LinearRegression())
    ])

    # fit model
    pipeline.fit(X_train, y_train)

    # predict on test set
    y_pred = pipeline.predict(X_test)

    # evaluate
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))

    metrics = {
        "rmse": float(rmse),
        "n_train": len(X_train),
        "n_test": len(X_test),
        "model_type": "LinearRegression",
    }

    return pipeline, metrics


def save_model(model, output_path: Path):
    """
    Save trained model to pickle.
    """
    with open(output_path, "wb") as f:
        pickle.dump(model, f)


def save_metrics(metrics: dict, output_path: Path):
    """
    Save metrics to JSON.
    """
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Train baseline LR diabetes model")
    parser.add_argument("--model-out", type=str, default="app/artifacts/model.pkl",
                        help="Path to save trained model pickle")
    parser.add_argument("--metrics-out", type=str, default="app/artifacts/metrics.json",
                        help="Path to save evaluation metrics JSON")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    args = parser.parse_args()

    # set random seed
    rng = check_random_state(args.seed)
    np.random.seed(args.seed)

    # load dataset
    data = load_diabetes(as_frame=True, scaled=False)
    X = data.frame.drop(columns=["target"]) # type: ignore
    y = data.frame["target"] # type: ignore

    # train + eval
    model, metrics = train_and_evaluate(X, y, random_state=args.seed)

    # prepare output paths
    model_path = Path(args.model_out)
    metrics_path = Path(args.metrics_out)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)

    # save artifacts
    save_model(model, model_path)
    save_metrics(metrics, metrics_path)

    print(f" Training complete. RMSE={metrics['rmse']:.4f}")
    print(f" Model saved to: {model_path.resolve()}")
    print(f" Metrics saved to: {metrics_path.resolve()}")


if __name__ == "__main__":
    main()
