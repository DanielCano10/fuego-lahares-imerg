"""
En este archivo se lee la lluvia diaria de IMERG y se calculan las 13 variables que usa el modelo.
Se usa lo mismo para entrenar y para predecir, así las variables siempre se calculan igual.
"""
import io
from pathlib import Path
import numpy as np
import pandas as pd

VENTANAS = [2, 3, 5, 7, 14, 30]
VARIABLES = (["lluvia_mm"] + [f"acum_{v}d" for v in VENTANAS] +
             ["max_diaria_7d", "lluvia_ayer", "dias_secos_previos", "api_k09", "mes_sin", "mes_cos"])

"""
    Lee el CSV que se descarga de NASA Giovanni con el servicio Time Series, Area-Averaged.
    Ese archivo trae primero varias líneas de información de la consulta y después las columnas time y el valor de lluvia.
"""
def leer_giovanni(ruta):
    lineas = Path(ruta).read_text(encoding="utf-8-sig", errors="replace").splitlines()
    inicio = next(i for i, l in enumerate(lineas) if l.lower().startswith("time,"))
    df = pd.read_csv(io.StringIO("\n".join(lineas[inicio:])))
    col = [c for c in df.columns[1:] if "precip" in c.lower()][0]
    return pd.DataFrame({"fecha_utc": pd.to_datetime(df[df.columns[0]]).dt.normalize(),
                         "lluvia_mm": pd.to_numeric(df[col], errors="coerce")})
"""
Recibe la lluvia de tres formas: el CSV de Giovanni, un CSV propio con columnas fecha y lluvia_mm, o un DataFrame.
Devuelve el calendario completo con las columnas fecha_utc y lluvia_mm, por lo que si falta algún día queda vacío
y no se inventa ningún valor.
"""
def leer_lluvia(origen):
    if isinstance(origen, pd.DataFrame):
        df = origen.copy()
    else:
        texto = Path(origen).read_text(encoding="utf-8-sig", errors="replace")
        if "\ntime," in texto.lower():
            df = leer_giovanni(origen)
        else:
            df = pd.read_csv(origen)
    fecha = next((c for c in ("fecha_utc", "fecha", "time", "date") if c in df.columns), df.columns[0])
    valor = "lluvia_mm" if "lluvia_mm" in df.columns else df.columns[1]
    s = pd.DataFrame({"fecha_utc": pd.to_datetime(df[fecha]).dt.normalize(),
                      "lluvia_mm": pd.to_numeric(df[valor], errors="coerce")})
    s.loc[s.lluvia_mm < 0, "lluvia_mm"] = np.nan                 # Giovanni pone -9999.9 cuando no hay dato
    s = s.drop_duplicates("fecha_utc").set_index("fecha_utc").sort_index()
    calendario = pd.date_range(s.index.min(), s.index.max(), freq="D")
    return s.reindex(calendario).rename_axis("fecha_utc").reset_index()

"""
Calcula las 13 variables para cada día UTC D. Todas usan solo la lluvia de ese día o de días anteriores,
es decir, nunca se usa lluvia del futuro.
Los primeros 30 días quedan sin valor, ya que todavía no tienen historia para el acumulado de 30 días.
"""
def calcular_variables(lluvia):
    d = lluvia.copy().sort_values("fecha_utc").set_index("fecha_utc")
    p = d["lluvia_mm"]
    for v in VENTANAS:
        # acumulado de v días, contando el día D
        d[f"acum_{v}d"] = p.rolling(v, min_periods=v).sum()
    # lo más que llovió en un día en la última semana
    d["max_diaria_7d"] = p.rolling(7, min_periods=7).max()
    d["lluvia_ayer"] = p.shift(1)
    seco = (p < 1).astype(int)
    d["dias_secos_previos"] = seco.groupby((seco == 0).cumsum()).cumsum().shift(1)
    api, a = [], 0.0
    # índice de precipitación antecedente, API(t) = 0.9 API(t-1) + P(t)
    for x in p.fillna(0).values:
        a = 0.9 * a + x
        api.append(a)
    # se toma el del día anterior
    d["api_k09"] = pd.Series(api, index=d.index).shift(1)
    d["mes_sin"] = np.sin(2 * np.pi * d.index.month / 12)
    d["mes_cos"] = np.cos(2 * np.pi * d.index.month / 12)
    return d.reset_index()

