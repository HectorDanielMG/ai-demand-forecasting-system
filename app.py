import csv
import json
import math
from pathlib import Path

from flask import Flask, render_template, request
from forecast import forecast_next_days

app = Flask(__name__)

ROOT = Path(__file__).resolve().parent
DATASET_PATH = ROOT / "data" / "complex_sales_dataset.csv"
EVALUATION_PATH = ROOT / "model" / "evaluation.json"
FORM_VALUES = {
    "product": {"Laptop": "laptop", "Mouse": "mouse", "Teclado": "keyboard", "Monitor": "monitor", "Audifonos": "headphones"},
    "category": {"Accesorios": "accessories", "Audio": "audio", "Computación": "computers", "Pantallas": "displays"},
    "region": {"Centro": "center", "Norte": "north", "Sur": "south"},
    "store": {f"Tienda {number}": f"store_{number}" for number in range(1, 5)},
}


def load_category_codes() -> dict[str, dict[str, int]]:
    """Replica el orden alfabético que LabelEncoder usa durante el entrenamiento."""
    categories = {column: set() for column in FORM_VALUES}
    with DATASET_PATH.open(encoding="utf-8", newline="") as dataset:
        for row in csv.DictReader(dataset):
            for column in categories:
                categories[column].add(row[column])
    return {column: {value: index for index, value in enumerate(sorted(values))}
            for column, values in categories.items()}


CATEGORY_CODES = load_category_codes()
PRODUCT_CATEGORY = {
    "Laptop": "Computación", "Mouse": "Accesorios", "Teclado": "Accesorios",
    "Monitor": "Pantallas", "Audifonos": "Audio",
}


def form_code(column: str, selected: str) -> int:
    value = FORM_VALUES[column].get(selected)
    if value is None or value not in CATEGORY_CODES[column]:
        raise ValueError("Selecciona una opción válida para todos los campos.")
    return CATEGORY_CODES[column][value]


def load_model_evaluation() -> dict | None:
    try:
        return json.loads(EVALUATION_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard", methods=["POST"])
def dashboard():
    try:
        product_data = {
            column: form_code(column, request.form[column])
            for column in FORM_VALUES
        }
        product_data.update({
            "price": float(request.form["price"]),
            "promotion": int(request.form["promotion"]),
            "inventory": int(request.form["inventory"]),
        })
        horizon_days = int(request.form["horizon_days"])
        if horizon_days not in {7, 14, 30, 60}:
            raise ValueError("Selecciona un horizonte de 7, 14, 30 o 60 días.")
        if not math.isfinite(product_data["price"]) or product_data["price"] < 0 or product_data["inventory"] < 0:
            raise ValueError("El precio y el inventario deben ser mayores o iguales a cero.")
        if product_data["promotion"] not in {0, 1}:
            raise ValueError("La promoción debe ser Sí o No.")
        if request.form["category"] != PRODUCT_CATEGORY[request.form["product"]]:
            raise ValueError("La categoría seleccionada no corresponde al producto.")
    except (KeyError, TypeError, ValueError) as exc:
        return render_template("index.html", error=str(exc) or "Revisa los datos ingresados."), 400

    # PREDICCION DEL MODELO

    predictions = forecast_next_days(product_data, days=horizon_days)

    dates = [p["date"] for p in predictions]
    sales = [p["predicted_sales"] for p in predictions]

    # ANALISIS DE NEGOCIO

    total_demand = sum(sales)

    avg_demand = total_demand / len(sales)

    demand_peak = max(sales)

    inventory = product_data["inventory"]

    remaining_inventory = inventory - total_demand

    revenue_prediction = total_demand * product_data["price"]

    # ALERTAS INTELIGENTES

    alerts = []

    if remaining_inventory < 0:
        alerts.append(
            "⚠ Riesgo crítico de desabasto. La demanda proyectada supera el inventario disponible."
        )

    if remaining_inventory < inventory * 0.2:
        alerts.append(
            "⚠ Inventario bajo. Se recomienda planificar reabastecimiento."
        )

    if avg_demand > 50:
        alerts.append(
            "📈 Alta demanda detectada. Se recomienda aumentar inventario o producción."
        )

    if demand_peak > avg_demand * 1.5:
        alerts.append(
            "📊 Se detecta un pico de demanda significativo. Esto puede indicar estacionalidad o impacto de marketing."
        )

    if product_data["promotion"] == 1:
        alerts.append(
            "🔥 Promoción activa. Esto puede aumentar considerablemente la demanda."
        )

    if not alerts:
        alerts.append(
            "✅ El sistema no detecta riesgos inmediatos."
        )

    # RECOMENDACIONES INTELIGENTES

    recommendations = []

    if remaining_inventory < 0:
        recommendations.append(
            "Aumentar inventario inmediatamente para evitar pérdida de ventas."
        )

    if avg_demand > 40:
        recommendations.append(
            "Considerar aumentar producción o realizar pedidos adicionales a proveedores."
        )

    if demand_peak > avg_demand * 1.5:
        recommendations.append(
            "Analizar el origen del pico de demanda para optimizar campañas o abastecimiento."
        )

    if product_data["promotion"] == 1:
        recommendations.append(
            "Aprovechar la promoción activa para incrementar marketing y ventas."
        )

    if remaining_inventory > total_demand * 2:
        recommendations.append(
            "El inventario es alto respecto a la demanda proyectada. Considerar promociones o estrategias de venta."
        )

    # ENVIAR DATOS AL DASHBOARD

    return render_template(
        "dashboard.html",
        dates=dates,
        sales=sales,
        total_demand=round(total_demand, 2),
        avg_demand=round(avg_demand, 2),
        remaining_inventory=round(remaining_inventory, 2),
        revenue_prediction=round(revenue_prediction, 2),
        demand_peak=round(demand_peak, 2),
        horizon_days=horizon_days,
        evaluation=load_model_evaluation(),
        alerts=alerts,
        recommendations=recommendations
    )


if __name__ == "__main__":
    app.run(debug=True)
