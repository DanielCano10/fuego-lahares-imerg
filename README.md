# fuego-lahares-imerg

Código, datos y modelos del trabajo de graduación **"Uso de modelos de clasificación supervisada para estimar la ocurrencia de lahares secundarios en el Volcán de Fuego, Guatemala, a partir de precipitación acumulada estimada por GPM/IMERG"**. Daniel Alexander Cano Pérez, Ingeniería en Ciencias y Sistemas, Universidad de San Carlos de Guatemala.

El modelo estima, para cada día, la probabilidad de que ocurra un lahar secundario en el Volcán de Fuego usando solo la lluvia estimada por satélite (NASA GPM/IMERG), que es gratuita y cubre todo el volcán. Se entrega como una librería de Python, **`lahares_fuego`**, que trae los datos y los modelos de la tesis.

## Para Instalación

```bash
pip install git+https://github.com/DanielCano10/fuego-lahares-imerg.git
```

## Uso

### Predecir con el modelo de la tesis

```python
import lahares_fuego as lf

lluvia = lf.leer_lluvia("mi_descarga_giovanni.csv")   # CSV de Giovanni, CSV con fecha y lluvia_mm, o DataFrame
modelo = lf.cargar_modelo()                           # bosque aleatorio de la tesis
modelo.predecir(lluvia)                               # fecha, lluvia, probabilidad y alerta por día
```

`cargar_modelo("regresion_logistica")` usa la ecuación de la tesis y `cargar_modelo("svm_rbf")` la máquina de vectores de soporte.

### Entrenar o ajustar con datos propios

Se necesita la lluvia y una tabla de etiquetas con columnas `fecha` (día local) y `y` (1 si hubo lahar, 0 si no).

```python
etiquetas = pd.read_csv("mis_lahares.csv")

# ajustar: agrega los datos nuevos a los de la tesis (2019-2023) y vuelve a entrenar
m = lf.ModeloLahares("bosque_aleatorio").entrenar(lluvia, etiquetas, incluir_datos=True)

# o entrenar solo con los datos propios
m = lf.ModeloLahares("regresion_logistica").entrenar(lluvia, etiquetas)

m.evaluar(lluvia_prueba, etiquetas_prueba)   # PR-AUC, ROC-AUC, sensibilidad, precisión, matriz de confusión
m.guardar("mi_modelo.joblib")
m = lf.ModeloLahares.cargar("mi_modelo.joblib")
```

Al entrenar se buscan los hiperparámetros con validación cruzada temporal y el umbral se elige para detectar al menos el 80 % de los lahares, igual que en la tesis.

### Desde la terminal

```bash
lahares-fuego predecir --lluvia mi_descarga.csv --salida predicciones.csv
lahares-fuego entrenar --lluvia lluvia.csv --etiquetas etiquetas.csv --incluir-datos --salida mi_modelo.joblib
lahares-fuego evaluar  --lluvia lluvia.csv --etiquetas etiquetas.csv --modelo mi_modelo.joblib
lahares-fuego ecuacion
```

### Sin programar: la ecuación

La regresión logística se puede aplicar a mano o en Excel. Los coeficientes están en `modelos/ECUACION.md`:

$$p = \frac{1}{1 + e^{-z}}, \qquad z = b_0 + \sum_{i=1}^{13} w_i \, x_i$$

### Condiciones de uso

La lluvia debe ser IMERG diaria de la misma celda (caja −90.95, 14.45, −90.85, 14.55, descargada en NASA Giovanni con *Time Series, Area-Averaged*) y debe incluir al menos los 30 días anteriores a las fechas que interesan. Con lluvia de otra zona o de un pluviómetro el modelo no es válido, porque aprendió con el sesgo propio del satélite.

**Es un resultado de investigación y no un sistema de alerta oficial.** Las alertas oficiales son las del INSIVUMEH y la CONRED.

## Resultados de la tesis

| Evaluación | Lluvia | PR-AUC (azar) | ROC-AUC |
|---|---|---|---|
| Prueba, enero 2024 a septiembre 2025 | IMERG Final | 0.49 a 0.53 (0.235) | 0.82 a 0.83 |
| Operativa, octubre 2025 a septiembre 2026 | IMERG Late | 0.72 a 0.76 (0.205) | 0.88 a 0.90 |

Modelos comparados: regresión logística, bosque aleatorio y máquina de vectores de soporte, entrenados con 2019 a 2023. Modelo elegido: bosque aleatorio.

## Reproducir la tesis

```bash
git clone https://github.com/DanielCano10/fuego-lahares-imerg.git
cd fuego-lahares-imerg
python -m venv .venv
.venv\Scripts\activate            # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
pip install -e .
jupyter lab                       # abrir lahares_fuego.ipynb y usar Run → Run All Cells
```

El notebook hace todo el experimento paso por paso, genera las tablas y figuras en `resultados/`, y vuelve a guardar los modelos y los datos que trae la librería. Los resultados se obtuvieron con Python 3.10.7 y las versiones de `requirements.txt`; con otras versiones de scikit-learn el bosque aleatorio puede dar métricas un poco distintas.

## Contenido

```
├── src/lahares_fuego/     la librería
│   ├── variables.py       lectura de la lluvia y las 13 variables
│   ├── modelo.py          ModeloLahares: entrenar, ajustar, predecir, evaluar, guardar
│   ├── cli.py             comandos de terminal
│   └── datos/             conjunto de datos y resumen de los modelos de la tesis
├── lahares_fuego.ipynb    el experimento de la tesis, explicado paso por paso
├── modelos/               modelos entrenados (.joblib) y la ecuación de la regresión logística
├── data/                  lluvia IMERG, catálogos de lahares, tabla diaria y pluviómetro (ver data/LEEME.md)
├── tests/                 pruebas de la librería (python -m pytest tests)
├── pyproject.toml         configuración del paquete
└── requirements.txt       versiones exactas usadas en la tesis
```

## Datos y licencias

El código tiene licencia MIT. Los datos derivados se publican bajo CC BY 4.0, y los de terceros conservan las condiciones de su fuente; el detalle está en `data/README.md`. Los boletines del INSIVUMEH se obtuvieron por la Ley de Acceso a la Información Pública (resolución UIP-INSIVUMEH-2026-9-561); sus PDF originales no se incluyen.

## Cita

Ver `CITATION.cff`.
