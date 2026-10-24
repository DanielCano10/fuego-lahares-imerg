"""
Estos son los comandos para usar la librería desde la terminal, sin escribir código en Python:
  lahares-fuego predecir --lluvia descarga.csv [--algoritmo bosque_aleatorio | --modelo mi_modelo.joblib] [--salida pred.csv]
  lahares-fuego entrenar --lluvia lluvia.csv --etiquetas etiquetas.csv --salida mi_modelo.joblib [--algoritmo ...] [--incluir-datos]
  lahares-fuego evaluar  --lluvia lluvia.csv --etiquetas etiquetas.csv [--modelo mi_modelo.joblib]
  lahares-fuego ecuacion
"""
import argparse
import json
import pandas as pd
from . import ALGORITMOS, ModeloLahares, cargar_modelo, info_tesis


def _modelo(a):
    return ModeloLahares.cargar(a.modelo) if getattr(a, "modelo", None) else cargar_modelo(a.algoritmo)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="lahares-fuego", description="Probabilidad de lahares secundarios en el Volcán de Fuego a partir de la lluvia de IMERG.")
    sub = ap.add_subparsers(dest="accion", required=True)
    p = sub.add_parser("predecir", help="calcula la probabilidad y la alerta de cada día")
    p.add_argument("--lluvia", required=True); p.add_argument("--algoritmo", default="bosque_aleatorio", choices=ALGORITMOS)
    p.add_argument("--modelo"); p.add_argument("--umbral", type=float); p.add_argument("--salida")
    e = sub.add_parser("entrenar", help="entrena o ajusta un modelo con datos propios")
    e.add_argument("--lluvia", required=True); e.add_argument("--etiquetas", required=True, help="CSV con columnas fecha y y")
    e.add_argument("--algoritmo", default="bosque_aleatorio", choices=ALGORITMOS)
    e.add_argument("--incluir-datos", action="store_true", help="le agrega los datos de entrenamiento de la tesis (2019-2023)")
    e.add_argument("--salida", required=True)
    v = sub.add_parser("evaluar", help="compara el modelo contra etiquetas que ya se conocen")
    v.add_argument("--lluvia", required=True); v.add_argument("--etiquetas", required=True)
    v.add_argument("--algoritmo", default="bosque_aleatorio", choices=ALGORITMOS); v.add_argument("--modelo")
    sub.add_parser("ecuacion", help="muestra la ecuación de la regresión logística de la tesis")
    a = ap.parse_args(argv)

    if a.accion == "predecir":
        r = _modelo(a).predecir(a.lluvia, a.umbral)
        if a.salida:
            r.to_csv(a.salida, index=False); print(f"{len(r)} días en {a.salida}; {int(r.alerta.sum())} con alerta.")
        else:
            print(r.tail(15).to_string(index=False))
    elif a.accion == "entrenar":
        m = ModeloLahares(a.algoritmo).entrenar(a.lluvia, pd.read_csv(a.etiquetas), incluir_datos=a.incluir_datos)
        m.guardar(a.salida); print(m, json.dumps(m.info, indent=1, ensure_ascii=False, default=str))
    elif a.accion == "evaluar":
        print(json.dumps(_modelo(a).evaluar(a.lluvia, pd.read_csv(a.etiquetas)), indent=1))
    elif a.accion == "ecuacion":
        ec = info_tesis()["ecuacion_regresion_logistica"]
        print("p = 1 / (1 + exp(-z))\nz =", f"{ec['intercepto']:.6f}")
        for k, w in ec["coeficientes"].items():
            print(f"    {'+' if w >= 0 else '-'} {abs(w):.6f} * {k}")
        print(f"alerta si p >= {info_tesis()['modelos']['regresion_logistica']['umbral']:.4f}")


if __name__ == "__main__":
    main()
