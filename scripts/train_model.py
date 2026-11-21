import os
import json
import gzip
import pandas as pd
import numpy as np
from datetime import datetime
import joblib
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(BASE_DIR, 'models_artifacts')
os.makedirs(MODELS_DIR, exist_ok=True)

print("Starting Machine Learning Pipeline...")
print("Loading processed hourly demand dataset...")

PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
hourly_csv_gz = os.path.join(PROCESSED_DIR, 'hourly_route_demand.csv.gz')
if not os.path.exists(hourly_csv_gz):
    hourly_csv_gz = os.path.join(DATA_DIR, 'hourly_route_demand.csv.gz')
print(f"Loading hourly demand dataset from: {hourly_csv_gz}")
df = pd.read_csv(hourly_csv_gz, compression='gzip')

print(f"Dataset loaded: {len(df):,} hourly records")
print(f"Columns: {df.columns.tolist()}")

# Ensure clean data
df['passengers'] = pd.to_numeric(df['passengers'], errors='coerce').fillna(0).astype(float)
df['date'] = pd.to_datetime(df['date'])
df['hour'] = df['hour'].astype(int)
df['day_of_week'] = df['day_of_week'].astype(int)
df['is_weekend'] = df['is_weekend'].astype(int)

# Feature engineering
print("Engineering temporal and demand features...")
df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24.0)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24.0)
df['is_peak_hour'] = df['hour'].isin([8, 9, 10, 17, 18, 19, 20]).astype(int)
df['is_morning_peak'] = df['hour'].isin([8, 9, 10]).astype(int)
df['is_evening_peak'] = df['hour'].isin([17, 18, 19, 20]).astype(int)

# Filter for top routes to ensure statistical stability (e.g. routes with >= 50 hourly records)
route_counts = df['route'].value_counts()
valid_routes = set(route_counts[route_counts >= 50].index)
print(f"Selecting {len(valid_routes)} robust routes with >= 50 hourly observations")
df_model = df[df['route'].isin(valid_routes)].copy()

# Chronological Train-Test Split (Strict - No future leakage!)
# Train: Oct 1 - Oct 24, 2026 (first 24 days)
# Test:  Oct 25 - Oct 30, 2026 (last 6 days)
split_date = pd.to_datetime('2026-10-25')
train_mask = df_model['date'] < split_date
test_mask = df_model['date'] >= split_date

df_train = df_model[train_mask].copy()
df_test = df_model[test_mask].copy()

print(f"Chronological split:")
print(f"  Training set:   {len(df_train):,} samples (Dates: {df_train['date'].min().date()} to {df_train['date'].max().date()})")
print(f"  Validation/Test: {len(df_test):,} samples (Dates: {df_test['date'].min().date()} to {df_test['date'].max().date()})")

# Step 1: Historical Median Baseline Model
print("\n--- Training Step 1: Historical Baseline Model ---")
# Baseline predicts the historical median for that (route, day_of_week, hour)
baseline_lookup = df_train.groupby(['route', 'day_of_week', 'hour'])['passengers'].median().to_dict()
# Fallback route-hour median
route_hour_lookup = df_train.groupby(['route', 'hour'])['passengers'].median().to_dict()
# Overall route median
route_lookup = df_train.groupby('route')['passengers'].median().to_dict()
global_median = df_train['passengers'].median()

def predict_baseline(row):
    key = (row['route'], row['day_of_week'], row['hour'])
    if key in baseline_lookup:
        return baseline_lookup[key]
    rh_key = (row['route'], row['hour'])
    if rh_key in route_hour_lookup:
        return route_hour_lookup[rh_key]
    return route_lookup.get(row['route'], global_median)

baseline_preds = df_test.apply(predict_baseline, axis=1).values
y_test = df_test['passengers'].values

baseline_mae = mean_absolute_error(y_test, baseline_preds)
baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_preds))
print(f"Historical Baseline Test Results:")
print(f"  MAE:  {baseline_mae:.3f} passengers/hr")
print(f"  RMSE: {baseline_rmse:.3f} passengers/hr")

# Step 2: Advanced Feature Engineering for Gradient Boosting Regressor
print("\n--- Training Step 2: HistGradientBoosting Regressor ---")
# Target encode routes based on train set only (to avoid leakage)
route_mean_train = df_train.groupby('route')['passengers'].mean().to_dict()
route_std_train = df_train.groupby('route')['passengers'].std().fillna(1.0).to_dict()

for d in [df_train, df_test]:
    d['route_hist_mean'] = d['route'].map(route_mean_train).fillna(global_median)
    d['route_hist_std'] = d['route'].map(route_std_train).fillna(1.0)

feature_cols = [
    'hour', 'hour_sin', 'hour_cos', 'day_of_week', 'is_weekend',
    'is_peak_hour', 'is_morning_peak', 'is_evening_peak',
    'route_hist_mean', 'route_hist_std'
]

X_train = df_train[feature_cols].values
y_train = df_train['passengers'].values
X_test = df_test[feature_cols].values

# Fit HistGradientBoostingRegressor (fast, handles non-linear relationships & interactions)
model = HistGradientBoostingRegressor(
    max_iter=150,
    learning_rate=0.08,
    max_depth=8,
    min_samples_leaf=20,
    random_state=42
)
model.fit(X_train, y_train)

# Evaluation
y_pred = model.predict(X_test)
# Bounded to non-negative counts
y_pred = np.clip(y_pred, 0, None)

ml_mae = mean_absolute_error(y_test, y_pred)
ml_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
ml_r2 = r2_score(y_test, y_pred)
improvement_pct = ((baseline_mae - ml_mae) / baseline_mae) * 100.0

print(f"HistGradientBoosting Test Results:")
print(f"  MAE:  {ml_mae:.3f} passengers/hr")
print(f"  RMSE: {ml_rmse:.3f} passengers/hr")
print(f"  R2:   {ml_r2:.3f}")
print(f"  Improvement over Historical Baseline: {improvement_pct:.2f}%")

# Step 3: Empirical Uncertainty & Confidence Calibration
print("\n--- Step 3: Empirical Uncertainty & Confidence Calibration ---")
test_residuals = y_test - y_pred
residual_std = float(np.std(test_residuals))
print(f"Standard deviation of residuals: {residual_std:.3f}")

# Calculate route-specific MAEs and confidence baselines
route_confidence_map = {}
for r in valid_routes:
    r_test = df_test[df_test['route'] == r]
    if len(r_test) > 5:
        r_y = r_test['passengers'].values
        r_preds = model.predict(r_test[feature_cols].values)
        r_mae = mean_absolute_error(r_y, r_preds)
        r_mean = max(1.0, float(np.mean(r_y)))
        # Bounded confidence: higher when relative error is lower
        conf = max(65.0, min(96.0, 100.0 * (1.0 - (r_mae / (r_mean * 1.5)))))
        route_confidence_map[r] = round(conf, 1)
    else:
        route_confidence_map[r] = 82.5 # Population average confidence

# Step 4: Save Model Artifacts
print("\nSaving model artifacts to disk...")
joblib.dump(model, os.path.join(MODELS_DIR, 'demand_forecaster.joblib'))

metrics_dict = {
    'model_name': 'HistGradientBoostingRegressor',
    'dataset_split': 'Chronological (Oct 1-24 Train / Oct 25-30 Test)',
    'train_samples': int(len(df_train)),
    'test_samples': int(len(df_test)),
    'mae': round(float(ml_mae), 3),
    'rmse': round(float(ml_rmse), 3),
    'r2_score': round(float(ml_r2), 3),
    'baseline_mae': round(float(baseline_mae), 3),
    'baseline_rmse': round(float(baseline_rmse), 3),
    'improvement_pct': round(float(improvement_pct), 2),
    'residual_std': round(residual_std, 3),
    'trained_at': datetime.now().isoformat(),
    'features': feature_cols
}

with open(os.path.join(MODELS_DIR, 'evaluation_metrics.json'), 'w') as f:
    json.dump(metrics_dict, f, indent=2)

# Save lookup baselines and route targets
artifacts_payload = {
    'route_mean_train': {str(k): round(float(v), 2) for k, v in route_mean_train.items()},
    'route_std_train': {str(k): round(float(v), 2) for k, v in route_std_train.items()},
    'route_confidence_map': route_confidence_map,
    'global_median': float(global_median),
    'residual_std': residual_std
}
with open(os.path.join(MODELS_DIR, 'model_context.json'), 'w') as f:
    json.dump(artifacts_payload, f, indent=2)

print("ML Training and Evaluation Pipeline successfully completed!")
