"""
lahares_fuego: probabilidad diaria de lahares secundarios en el Volcán de Fuego (Guatemala)
a partir de lluvia GPM/IMERG diaria.

Para uso rápido:
    import lahares_fuego as lf
    lluvia = lf.leer_lluvia("descarga_giovanni.csv")
    #Este es el bosque aleatorio o random forest de la tesis
    modelo = lf.cargar_modelo()                 
    modelo.predecir(lluvia)

Entrenar o ajustar con datos propios:
    m = lf.ModeloLahares("bosque_aleatorio").entrenar(lluvia, etiquetas, incluir_datos=True)
    m.evaluar(lluvia_prueba, etiquetas_prueba)
    m.guardar("mi_modelo.joblib")

Es el resultado de investigación y no es un sistema de alerta oficial.
"""
__version__ = "1.0.0"

from .variables import VARIABLES, calcular_variables, leer_giovanni, leer_lluvia
from .modelo import (ALGORITMOS, ModeloLahares, cargar_modelo, datos_tesis, info_tesis, metricas,
                     umbral_por_sensibilidad, unir)

__all__ = ["VARIABLES", "ALGORITMOS", "leer_lluvia", "leer_giovanni", "calcular_variables", "ModeloLahares",
           "cargar_modelo", "datos_tesis", "info_tesis", "metricas", "umbral_por_sensibilidad", "unir"]
