import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBRegressor
import joblib

# Cargar dataset
df = pd.read_csv("data/complex_sales_dataset.csv")

# Convertir fecha
df["date"] = pd.to_datetime(df["date"])

# Crear variables de tiempo
df["day"] = df["date"].dt.day
df["year"] = df["date"].dt.year

# Codificar variables categóricas
le_product = LabelEncoder()
le_category = LabelEncoder()
le_region = LabelEncoder()
le_store = LabelEncoder()

df["product"] = le_product.fit_transform(df["product"])
df["category"] = le_category.fit_transform(df["category"])
df["region"] = le_region.fit_transform(df["region"])
df["store"] = le_store.fit_transform(df["store"])

# Variables predictoras
features = [
    "product",
    "category",
    "region",
    "store",
    "price",
    "promotion",
    "inventory",
    "weekday",
    "month",
    "day"
]

X = df[features]
y = df["sales"]

# Separar entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Modelo
model = XGBRegressor(
    n_estimators=200,
    learning_rate=0.05,
    max_depth=6
)

model.fit(X_train, y_train)

# Guardar modelo
joblib.dump(model, "model/demand_model.pkl")

print("Modelo entrenado y guardado.")