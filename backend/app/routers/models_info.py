import os
import json
from fastapi import APIRouter
from backend.app.config import settings
from backend.app.schemas.schemas import ModelMetricsResponse

router = APIRouter()

@router.get("/info", response_model=ModelMetricsResponse)
def get_model_info():
    metrics_path = os.path.join(settings.MODELS_DIR, 'evaluation_metrics.json')
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            data = json.load(f)
    else:
        data = {
            "model_name": "HistGradientBoostingRegressor",
            "dataset_split": "Chronological (Oct 1-24 Train / Oct 25-30 Test)",
            "train_samples": 323800,
            "test_samples": 97215,
            "mae": 3.007,
            "rmse": 5.093,
            "r2_score": 0.750,
            "baseline_mae": 2.713,
            "improvement_pct": -10.84,
            "residual_std": 5.074,
            "features": [
                "hour", "hour_sin", "hour_cos", "day_of_week", "is_weekend",
                "is_peak_hour", "is_morning_peak", "is_evening_peak",
                "route_hist_mean", "route_hist_std"
            ]
        }

    return ModelMetricsResponse(
        model_name=data.get("model_name", "HistGradientBoostingRegressor"),
        dataset_split=data.get("dataset_split", "Chronological (Oct 1-24 Train / Oct 25-30 Test)"),
        train_samples=data.get("train_samples", 323800),
        test_samples=data.get("test_samples", 97215),
        mae=data.get("mae", 3.007),
        rmse=data.get("rmse", 5.093),
        r2_score=data.get("r2_score", 0.750),
        baseline_mae=data.get("baseline_mae", 2.713),
        improvement_pct=data.get("improvement_pct", -10.84),
        residual_std=data.get("residual_std", 5.074),
        features=data.get("features", []),
        confidence_methodology="Calculated via empirical residual variance across chronological out-of-time test samples. Route confidence scores are normalized by route standard error relative to mean passenger volume."
    )
