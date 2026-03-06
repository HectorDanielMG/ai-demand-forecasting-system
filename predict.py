import joblib
import pandas as pd

model = joblib.load("model/demand_model.pkl")

def predict_sales(data):

    df = pd.DataFrame([data])

    prediction = model.predict(df)

    return float(prediction[0])