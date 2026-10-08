"""Entrena el pronosticador y genera métricas con una validación temporal."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "complex_sales_dataset.csv"
MODEL_DIR = ROOT / "model"
MODEL_PATH = MODEL_DIR / "demand_model.pkl"
EVALUATION_PATH = MODEL_DIR / "evaluation.json"

FEATURES = [
    "product", "category", "region", "store", "price", "promotion",
    "inventory", "weekday", "month", "day",
]
MODEL_PARAMS = {"n_estimators": 200, "learning_rate": 0.05, "max_depth": 6, "random_state": 42}


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df["day"] = df["date"].dt.day
    df = df.sort_values("date", kind="stable").reset_index(drop=True)

    # Mantiene la misma codificación alfabética que usa la aplicación al inferir.
    for column in ("product", "category", "region", "store"):
        df[column] = LabelEncoder().fit_transform(df[column].astype(str))

    dates = df["date"].drop_duplicates().sort_values().tolist()
    split_index = int(len(dates) * 0.8)
    if split_index < 1 or split_index >= len(dates):
        raise ValueError("El conjunto de datos necesita al menos dos fechas distintas.")
    test_start = dates[split_index]
    train_df = df[df["date"] < test_start]
    test_df = df[df["date"] >= test_start]
    if train_df.empty or test_df.empty:
        raise ValueError("No se pudo separar el conjunto en periodos de entrenamiento y evaluación.")

    evaluation_model = XGBRegressor(**MODEL_PARAMS)
    evaluation_model.fit(train_df[FEATURES], train_df["sales"])
    test_predictions = evaluation_model.predict(test_df[FEATURES]).clip(min=0)
    actual = test_df["sales"]
    absolute_error = (actual - test_predictions).abs()
    wape_denominator = float(actual.abs().sum())
    metrics = {
        "mae": round(float(mean_absolute_error(actual, test_predictions)), 3),
        "rmse": round(float(mean_squared_error(actual, test_predictions) ** 0.5), 3),
        "wape_percent": round(float(absolute_error.sum()) / wape_denominator * 100, 2) if wape_denominator else None,
    }

    # Una vez medida la calidad fuera de muestra, ajusta el artefacto de producción con todo el histórico.
    production_model = XGBRegressor(**MODEL_PARAMS)
    production_model.fit(df[FEATURES], df["sales"])
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(production_model, MODEL_PATH)

    evaluation = {
        "strategy": "Separación cronológica por fecha (80% inicial para entrenamiento, 20% final para evaluación)",
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "train_start": train_df["date"].min().date().isoformat(),
        "train_end": train_df["date"].max().date().isoformat(),
        "test_start": test_df["date"].min().date().isoformat(),
        "test_end": test_df["date"].max().date().isoformat(),
        "metrics": metrics,
    }
    EVALUATION_PATH.write_text(json.dumps(evaluation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Modelo guardado en: {MODEL_PATH}")
    print(f"Evaluación temporal guardada en: {EVALUATION_PATH}")
    print(f"MAE: {metrics['mae']} | RMSE: {metrics['rmse']} | WAPE: {metrics['wape_percent']}%")
    print(f"Periodo de prueba: {evaluation['test_start']} a {evaluation['test_end']} ({len(test_df)} registros)")


if __name__ == "__main__":
    main()
