"""
Aquí está el modelo como tal. Con la clase ModeloLahares se puede entrenar con datos propios,
ajustar el modelo de la tesis agregándole datos nuevos, predecir, evaluar y guardar el modelo.
"""
import json
from importlib import resources
import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (average_precision_score, confusion_matrix, fbeta_score, precision_recall_curve,
                             precision_score, recall_score, roc_auc_score)
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from .variables import VARIABLES, calcular_variables, leer_lluvia

ALGORITMOS = ("regresion_logistica", "bosque_aleatorio", "svm_rbf")
NOMBRES = {"regresion_logistica": "Regresión logística", "bosque_aleatorio": "Bosque aleatorio", "svm_rbf": "SVM (kernel RBF)"}
SEMILLA = 42
SENSIBILIDAD_OBJETIVO = 0.80

# Son los mismos valores que se probaron en la búsqueda en cuadrícula de la tesis (tabla 7)
GRILLAS = {
    "regresion_logistica": {"logisticregression__C": [0.01, 0.1, 1, 10]},
    "bosque_aleatorio": {"n_estimators": [300], "max_depth": [3, 5, 8, None], "min_samples_leaf": [1, 5, 20]},
    "svm_rbf": {"svc__C": [0.1, 1, 10], "svc__gamma": ["scale", 0.01, 0.1]},
}

"""
Devuelve el modelo de scikit-learn todavía sin entrenar. Los tres usan class_weight="balanced",
ya que hay muchos más días sin lahar que con lahar, y así el modelo le da más peso a los días con lahar.
La regresión logística y la SVM llevan estandarización, debido a que son sensibles a la escala de las variables.
"""
def construir(algoritmo, semilla=SEMILLA):
    if algoritmo == "regresion_logistica":
        return make_pipeline(StandardScaler(), LogisticRegression(class_weight="balanced", max_iter=5000))
    if algoritmo == "bosque_aleatorio":
        return RandomForestClassifier(class_weight="balanced", random_state=semilla, n_jobs=-1)
    if algoritmo == "svm_rbf":
        return make_pipeline(StandardScaler(), SVC(kernel="rbf", class_weight="balanced", probability=True, random_state=semilla))
    raise ValueError(f"No conozco el algoritmo '{algoritmo}', las opciones son: {ALGORITMOS}")

"""
Busca el umbral más alto con el que todavía se detecta al menos el porcentaje 'objetivo' de los lahares.
Por defecto es el 80 %, porque en este problema es más grave no avisar de un lahar que dar una falsa alarma.
"""
def umbral_por_sensibilidad(y, p, objetivo=SENSIBILIDAD_OBJETIVO):
    _, rec, thr = precision_recall_curve(y, p)
    ok = np.where(rec[:-1] >= objetivo)[0]
    return float(thr[ok[-1]]) if len(ok) else 0.5

"""Calcula las métricas que se usaron en la tesis, con la matriz de confusión (VP, FP, FN y VN)."""
def metricas(y, p, umbral):
    y = np.asarray(y); yhat = (np.asarray(p) >= umbral).astype(int)
    vn, fp, fn, vp = confusion_matrix(y, yhat, labels=[0, 1]).ravel()
    return {"n": int(len(y)), "con_lahar": int(y.sum()), "azar": round(float(y.mean()), 3),
            "pr_auc": round(float(average_precision_score(y, p)), 3), "roc_auc": round(float(roc_auc_score(y, p)), 3),
            "umbral": round(float(umbral), 3), "sensibilidad": round(float(recall_score(y, yhat, zero_division=0)), 3),
            "especificidad": round(float(vn / (vn + fp)), 3) if (vn + fp) else None,
            "precision": round(float(precision_score(y, yhat, zero_division=0)), 3),
            "f2": round(float(fbeta_score(y, yhat, beta=2, zero_division=0)), 3),
            "VP": int(vp), "FP": int(fp), "FN": int(fn), "VN": int(vn)}

"""
Une la lluvia con la tabla de etiquetas, la cual debe tener las columnas fecha y y (1 si hubo lahar, 0 si no).
La fecha de las etiquetas es el día local, y se une con el día UTC del mismo número, es decir,
con la lluvia hasta las 18:00 hora local, igual que en la tesis, para no usar lluvia que cayó después.
"""
def unir(lluvia, etiquetas):
    X = calcular_variables(leer_lluvia(lluvia))
    e = etiquetas.copy()
    if "fecha" not in e.columns or "y" not in e.columns:
        raise ValueError("A las etiquetas les faltan columnas, deben tener 'fecha' y 'y' (1 = hubo lahar, 0 = no hubo)")
    e["fecha"] = pd.to_datetime(e["fecha"]).dt.normalize()
    d = e[["fecha", "y"]].merge(X, left_on="fecha", right_on="fecha_utc", how="inner")
    return d.dropna(subset=VARIABLES + ["y"])[["fecha", "y"] + VARIABLES].sort_values("fecha").reset_index(drop=True)

"""
La regresión logística de la tesis escrita como ecuación, p = 1 / (1 + exp(-(b0 + suma(w_i * x_i)))).
Con esto no hace falta entrenar nada para usarla.
"""
class _Ecuacion:
    def __init__(self, b0, w):
        self.b0, self.w = float(b0), np.asarray(w, dtype=float)

    def predict_proba(self, X):
        p = 1 / (1 + np.exp(-(self.b0 + np.asarray(X, dtype=float) @ self.w)))
        return np.column_stack([1 - p, p])

"""
Modelo para estimar la ocurrencia de lahares secundarios en el Volcán de Fuego a partir de la lluvia diaria de IMERG.
Por ejemplo:
    m = ModeloLahares("bosque_aleatorio").entrenar(lluvia, etiquetas)                       # solo con datos propios
    m = ModeloLahares("bosque_aleatorio").entrenar(lluvia, etiquetas, incluir_datos=True)   # agregando los datos de la tesis
    m.predecir(lluvia_nueva)
"""
class ModeloLahares:
    def __init__(self, algoritmo="bosque_aleatorio", hiperparametros=None, sensibilidad_objetivo=SENSIBILIDAD_OBJETIVO, semilla=SEMILLA):
        if algoritmo not in ALGORITMOS:
            raise ValueError(f"No conozco el algoritmo '{algoritmo}', las opciones son: {ALGORITMOS}")
        self.algoritmo, self.hiperparametros = algoritmo, hiperparametros
        self.sensibilidad_objetivo, self.semilla = sensibilidad_objetivo, semilla
        self.estimador, self.umbral, self.info = None, None, {}

    def __repr__(self):
        estado = f"umbral={self.umbral:.3f}" if self.umbral is not None else "sin entrenar"
        return f"ModeloLahares({self.algoritmo}, {estado})"

    # -------------------------------------- entrenamiento
    """
        Entrena el modelo y define el umbral de decisión.
        --------------------------------------------------
        Se le puede dar la información de dos formas:
          - lluvia y etiquetas: la lluvia diaria (CSV de Giovanni, CSV propio o DataFrame) y una tabla con fecha y y.
          - datos: un DataFrame que ya tiene fecha, y y las 13 variables calculadas.
        incluir_datos=True le agrega los días de entrenamiento de la tesis (2019 a 2023), es decir, sirve para
        ajustar el modelo de la tesis con datos nuevos. También se puede usar solo, para entrenar con los datos de la tesis.
        buscar_hiperparametros=True hace la búsqueda en cuadrícula con validación cruzada temporal. Si no se indica,
        solo se busca cuando no se le dieron hiperparámetros al crear el modelo.

        El umbral se elige con predicciones fuera de pliegue, por lo que nunca se usa el mismo dato para entrenar
        y para escoger el umbral.
    """
    def entrenar(self, lluvia=None, etiquetas=None, datos=None, incluir_datos=False,
                 buscar_hiperparametros=None, n_pliegues=5):
        partes = []
        if datos is not None:
            partes.append(datos[["fecha", "y"] + VARIABLES])
        if lluvia is not None and etiquetas is not None:
            partes.append(unir(lluvia, etiquetas))
        if incluir_datos:
            partes.append(datos_tesis("entrenamiento")[["fecha", "y"] + VARIABLES])
        if not partes:
            raise ValueError("No hay datos para entrenar, se necesita lluvia y etiquetas, datos, o incluir_datos=True")
        d = pd.concat(partes).assign(fecha=lambda x: pd.to_datetime(x.fecha))
        d = d.drop_duplicates("fecha", keep="first").sort_values("fecha").reset_index(drop=True)
        X, y = d[VARIABLES], d.y.astype(int).values
        if y.sum() < 10:
            raise ValueError("Hay muy pocos días con lahar, se necesitan por lo menos 10 para entrenar")
        # Siempre se entrena con el pasado y se valida con lo que sigue
        cv = TimeSeriesSplit(n_splits=n_pliegues)    
        base = construir(self.algoritmo, self.semilla)
        buscar = (self.hiperparametros is None) if buscar_hiperparametros is None else buscar_hiperparametros
        if buscar:
            gs = GridSearchCV(base, GRILLAS[self.algoritmo], scoring="average_precision", cv=cv, n_jobs=-1).fit(X, y)
            self.hiperparametros, pr_cv = gs.best_params_, float(gs.best_score_)
        else:
            pr_cv = None
        est = clone(base).set_params(**(self.hiperparametros or {}))
        idx, p_oof = [], []
        # Predicciones fuera de pliegue, sin ver el futuro
        for tr, te in cv.split(X):                   
            m = clone(est).fit(X.iloc[tr], y[tr])
            idx.extend(te); p_oof.extend(m.predict_proba(X.iloc[te])[:, 1])
        idx, p_oof = np.array(idx), np.array(p_oof)
        self.umbral = umbral_por_sensibilidad(y[idx], p_oof, self.sensibilidad_objetivo)
        # El modelo final se entrena con todos los días
        self.estimador = est.fit(X, y)              
        self.info = {"dias": int(len(d)), "con_lahar": int(y.sum()), "desde": str(d.fecha.min().date()),
                     "hasta": str(d.fecha.max().date()), "hiperparametros": self.hiperparametros,
                     "pr_auc_validacion_cruzada": pr_cv, "validacion_cruzada": metricas(y[idx], p_oof, self.umbral)}
        return self

    # ------------- Para el uso
    def _revisar(self):
        if self.estimador is None:
            raise RuntimeError("El modelo todavía no está entrenado, primero hay que usar entrenar() o cargar_modelo()")
        
    """Calcula la probabilidad de lahar de cada día que tenga por lo menos 30 días de lluvia antes."""
    def probabilidad(self, lluvia):
        self._revisar()
        X = calcular_variables(leer_lluvia(lluvia)).dropna(subset=VARIABLES)
        return X.assign(probabilidad=self.estimador.predict_proba(X[VARIABLES])[:, 1])
    """
    Devuelve una tabla con la fecha, la lluvia del día, el acumulado de 3 días, la probabilidad y la alerta,
    la cual es 1 cuando la probabilidad llega al umbral. Si no se le da un umbral, usa el del entrenamiento.
    """
    def predecir(self, lluvia, umbral=None):
        X = self.probabilidad(lluvia)
        u = self.umbral if umbral is None else umbral
        return pd.DataFrame({"fecha": X.fecha_utc.dt.date, "lluvia_mm": X.lluvia_mm.round(2), "acum_3d": X.acum_3d.round(2),
                             "probabilidad": X.probabilidad.round(3), "alerta": (X.probabilidad >= u).astype(int)}).reset_index(drop=True)

    """Compara las predicciones contra etiquetas que ya se conocen y devuelve las métricas."""
    def evaluar(self, lluvia=None, etiquetas=None, datos=None, umbral=None):
        self._revisar()
        d = datos if datos is not None else unir(lluvia, etiquetas)
        p = self.estimador.predict_proba(d[VARIABLES])[:, 1]
        return metricas(d.y.astype(int).values, p, self.umbral if umbral is None else umbral)
    
    """
    Devuelve el intercepto y los coeficientes de la regresión logística, ya en las unidades de cada variable
    (mm, días, etc.), para poder usarla sin la librería. El bosque aleatorio y la SVM no tienen una ecuación así.
    """
    def ecuacion(self):
        
        self._revisar()
        if isinstance(self.estimador, _Ecuacion):
            b0, w = self.estimador.b0, self.estimador.w
        elif self.algoritmo == "regresion_logistica":
            sc, lr = self.estimador[0], self.estimador[-1]
            beta = lr.coef_[0]
            # se deshace la estandarización
            w = beta / sc.scale_
            b0 = float(lr.intercept_[0] - np.sum(beta * sc.mean_ / sc.scale_))
        else:
            raise ValueError("Solo la regresión logística tiene ecuación, el bosque aleatorio y la SVM no")
        return {"intercepto": float(b0), "coeficientes": dict(zip(VARIABLES, np.asarray(w).tolist())), "umbral": self.umbral,
                "formula": "p = 1 / (1 + exp(-(intercepto + suma(coeficiente_i * variable_i))))"}

# ----------------- guardar y cargar
    def guardar(self, ruta):
        self._revisar()
        joblib.dump(self, ruta)

    @staticmethod
    def cargar(ruta):
        return joblib.load(ruta)


# ----------------- datos y modelos de la tesis
def _archivo(nombre):
    f = resources.files("lahares_fuego").joinpath("datos", nombre)
    if not f.is_file():
        raise FileNotFoundError(f"No se encontró {nombre}. Estos datos se generan al correr el paso 10 del notebook "
                                "lahares_fuego.ipynb, por lo que hay que correrlo antes de usar los datos de la tesis")
    return f

"""Los hiperparámetros, umbrales, métricas y la ecuación que se obtuvieron en la tesis."""
def info_tesis():
    return json.loads(_archivo("modelos_tesis.json").read_text(encoding="utf-8"))

"""
El conjunto de datos de la tesis, con la fecha, la etiqueta y, las 13 variables y el conjunto al que pertenece cada día.
conjunto puede ser 'entrenamiento' (2019-2023), 'prueba' (2024 a sep-2025), 'operativo' (oct-2025 a sep-2026) o 'todo'.
"""
def datos_tesis(conjunto="todo"):
    with _archivo("conjunto_tesis.csv").open("r", encoding="utf-8") as f:
        d = pd.read_csv(f, parse_dates=["fecha"], float_precision="round_trip")
    return d if conjunto == "todo" else d[d.conjunto == conjunto].reset_index(drop=True)

"""
Devuelve el modelo de la tesis listo para predecir.
La regresión logística se arma directo con la ecuación de la tesis, por lo que no se entrena.
El bosque aleatorio y la SVM se vuelven a entrenar con los datos de 2019 a 2023 y los hiperparámetros de la tesis,
lo cual tarda unos segundos. Se hizo así debido a que un modelo guardado solo abre bien con la misma versión
de scikit-learn, y de esta forma funciona en cualquier computadora. Con las versiones de la tesis da el mismo modelo.
"""
def cargar_modelo(algoritmo="bosque_aleatorio"):
    t = info_tesis()
    m = ModeloLahares(algoritmo, hiperparametros=t["modelos"][algoritmo]["hiperparametros"])
    if algoritmo == "regresion_logistica":
        ec = t["ecuacion_regresion_logistica"]
        m.estimador = _Ecuacion(ec["intercepto"], [ec["coeficientes"][v] for v in VARIABLES])
        m.umbral = t["modelos"][algoritmo]["umbral"]
        m.info = {"origen": "ecuación de la tesis", **t["modelos"][algoritmo]}
        return m
    m.entrenar(incluir_datos=True, buscar_hiperparametros=False)
    m.info["umbral_tesis"] = t["modelos"][algoritmo]["umbral"]
    return m


