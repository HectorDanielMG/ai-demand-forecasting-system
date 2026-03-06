import pandas as pd
import joblib
from datetime import datetime, timedelta

model = joblib.load("model/demand_model.pkl")

def forecast_next_days(product_data, days=30):

    today = datetime.today()

    predictions = []

    for i in range(days):

        future_date = today + timedelta(days=i)

        input_data = product_data.copy()

        input_data["weekday"] = future_date.weekday()
        input_data["month"] = future_date.month
        input_data["day"] = future_date.day

        df = pd.DataFrame([input_data])

        pred = model.predict(df)[0]

        predictions.append({
            "date": future_date.strftime("%Y-%m-%d"),
            "predicted_sales": float(pred)
        })

    return predictions


def inventory_recommendation(predictions, current_inventory):

    total_demand = sum([p["predicted_sales"] for p in predictions])

    recommended_inventory = int(total_demand * 1.2)

    if current_inventory < total_demand:
        risk = "ALTO"
    elif current_inventory < recommended_inventory:
        risk = "MEDIO"
    else:
        risk = "BAJO"

    return {
        "predicted_demand": int(total_demand),
        "recommended_inventory": recommended_inventory,
        "risk_level": risk
    }