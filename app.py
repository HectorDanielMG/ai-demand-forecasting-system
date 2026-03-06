from flask import Flask, render_template, request
from forecast import forecast_next_days

app = Flask(__name__)

# MAPEO DE VALORES DEL FORMULARIO

product_map = {
    "Laptop": 0,
    "Mouse": 1,
    "Teclado": 2,
    "Monitor": 3,
    "Audifonos": 4
}

category_map = {
    "Electronica": 0,
    "Accesorios": 1
}

region_map = {
    "Norte": 0,
    "Centro": 1,
    "Sur": 2
}

store_map = {
    "Tienda 1": 0,
    "Tienda 2": 1,
    "Tienda 3": 2,
    "Tienda 4": 3
}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard", methods=["POST"])
def dashboard():

    # DATOS DEL USUARIO

    product_data = {
        "product": product_map[request.form["product"]],
        "category": category_map[request.form["category"]],
        "region": region_map[request.form["region"]],
        "store": store_map[request.form["store"]],
        "price": float(request.form["price"]),
        "promotion": int(request.form["promotion"]),
        "inventory": int(request.form["inventory"])
    }

    # PREDICCION DEL MODELO

    predictions = forecast_next_days(product_data)

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
        alerts=alerts,
        recommendations=recommendations
    )


if __name__ == "__main__":
    app.run(debug=True)