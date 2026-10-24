"""Pruebas de la librería. Correr con:  python -m pytest tests"""
import numpy as np
import pandas as pd
import lahares_fuego as lf


def lluvia_falsa(dias=90):
    fechas = pd.date_range("2025-05-01", periods=dias, freq="D")
    return pd.DataFrame({"fecha": fechas, "lluvia_mm": (np.arange(dias) * 7) % 23})


def test_variables_sin_futuro():
    X = lf.calcular_variables(lf.leer_lluvia(lluvia_falsa()))
    f = X.iloc[40]
    assert f.acum_3d == X.lluvia_mm.iloc[38:41].sum()          # incluye el día D y los dos anteriores
    assert f.lluvia_ayer == X.lluvia_mm.iloc[39]
    assert set(lf.VARIABLES) <= set(X.columns)


def test_datos_tesis_incluidos():
    d = lf.datos_tesis()
    assert set(d.conjunto) == {"entrenamiento", "prueba", "operativo"}
    assert len(lf.datos_tesis("entrenamiento")) > 1000


def test_ecuacion_de_la_tesis():
    m = lf.cargar_modelo("regresion_logistica")
    r = m.predecir(lluvia_falsa())
    assert len(r) == 90 - 29 and r.probabilidad.between(0, 1).all()
    assert m.ecuacion()["coeficientes"].keys() == set(lf.VARIABLES)


def test_entrenar_guardar_cargar(tmp_path):
    d = lf.datos_tesis("entrenamiento")
    m = lf.ModeloLahares("regresion_logistica", hiperparametros={"logisticregression__C": 0.1}).entrenar(datos=d)
    assert 0 < m.umbral < 1 and m.evaluar(datos=lf.datos_tesis("prueba"))["roc_auc"] > 0.7
    m.guardar(tmp_path / "m.joblib")
    assert lf.ModeloLahares.cargar(tmp_path / "m.joblib").umbral == m.umbral
