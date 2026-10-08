# AI Demand Forecast

Aplicación web de pronóstico de demanda e inventario. Usa un modelo XGBoost para estimar ventas diarias durante los próximos 30 días a partir del producto, su categoría, la región, la tienda, el precio, la promoción y el inventario actual.

## Ejecutar localmente

Requiere Python 3.10 o superior. Desde la carpeta del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Abre [http://127.0.0.1:5000](http://127.0.0.1:5000). El proyecto incluye el modelo entrenado en `model/demand_model.pkl` y el conjunto de datos en `data/complex_sales_dataset.csv`.

## Entrenar el modelo

```bash
python train_model.py
```

El entrenamiento usa `data/complex_sales_dataset.csv` y guarda el modelo en `model/demand_model.pkl`. Las categorías se codifican en orden alfabético; la aplicación obtiene los mismos códigos del conjunto de datos para que las predicciones usen la codificación aprendida.

## Uso

1. Selecciona producto, categoría, región y tienda.
2. Indica precio, inventario disponible y si hay una promoción activa.
3. Genera el pronóstico para consultar demanda diaria, demanda total, ingresos estimados, inventario restante y alertas.

La categoría debe corresponder al producto. El sistema valida las selecciones y evita aceptar precios o inventarios negativos. Las predicciones de ventas se limitan a cero como mínimo, ya que no existe demanda negativa.

## Estructura

| Archivo | Propósito |
| --- | --- |
| `app.py` | Aplicación web y validación del formulario |
| `train_model.py` | Entrenamiento del modelo de demanda |
| `forecast.py` | Pronóstico diario y recomendación de inventario |
| `predict.py` | Predicción individual |
| `data/complex_sales_dataset.csv` | Datos de entrenamiento |
| `model/demand_model.pkl` | Modelo entrenado |
