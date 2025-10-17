# CHANGELOG

## v0.1 — Baseline (SVR Regressor)  — 2025-10-17
Model: Support Vector Regressor (RBF kernel) + StandardScaler

Test RMSE: *65.810* 

Configuration:
- C = 1.0, epsilon = 0.2, kernel = "rbf"
- Train/test split 80/20, n_train = 353, n_test = 89, random_state = 42

Notes:
- Baseline SVR pipeline using sklearn.Pipeline.
- Model and metrics saved as artifacts (model.pkl, metrics.json).