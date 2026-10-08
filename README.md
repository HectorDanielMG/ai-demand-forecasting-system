# AI Demand Forecast

Aplicación web de pronóstico de demanda e inventario. Usa un modelo XGBoost para estimar ventas diarias durante los próximos 7, 14, 30 o 60 días, a partir del producto, su categoría, la región, la tienda, el precio, la promoción y el inventario actual. La proyección comienza mañana para representar días futuros completos.

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

El entrenamiento usa `data/complex_sales_dataset.csv` y guarda el modelo de producción en `model/demand_model.pkl`. Antes de entrenar el artefacto final, reserva el 20% de las fechas más recientes como prueba, entrena una copia con el periodo anterior y calcula MAE, RMSE y WAPE. Las métricas y el rango evaluado se guardan en `model/evaluation.json` y aparecen en el tablero. Las categorías se codifican en orden alfabético; la aplicación obtiene los mismos códigos del conjunto de datos para mantener la codificación alineada.

La separación por fecha simula mejor un pronóstico real que una división aleatoria: el modelo se evalúa con registros posteriores a los que vio durante esa fase. Después, el modelo que usa la aplicación se reentrena con todo el histórico. MAE y RMSE se expresan en unidades de venta; WAPE expresa el error absoluto total como porcentaje de la demanda real del periodo de prueba. Vuelve a ejecutar `python train_model.py` después de cambiar los datos para actualizar tanto el modelo como sus métricas.

## Uso

1. Selecciona producto, categoría, región y tienda.
2. Indica precio, inventario disponible y si hay una promoción activa.
3. Elige el horizonte de 7, 14, 30 o 60 días.
4. Genera el pronóstico para consultar demanda diaria, demanda total, ingresos estimados, inventario restante y alertas del periodo elegido.

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
