# Ecuación de la regresión logística

Probabilidad de lahar secundario en el Volcán de Fuego para el día local D, con lluvia IMERG diaria de la celda -90.95, 14.45, -90.85, 14.55.

    p = 1 / (1 + exp(-z))
    z = -1.288432
        + 0.057914 * lluvia_mm
        + 0.016179 * acum_2d
        - 0.002080 * acum_3d
        + 0.006463 * acum_5d
        + 0.009930 * acum_7d
        + 0.000433 * acum_14d
        + 0.000324 * acum_30d
        - 0.013918 * max_diaria_7d
        - 0.012921 * lluvia_ayer
        - 0.216535 * dias_secos_previos
        - 0.000357 * api_k09
        - 0.460311 * mes_sin
        - 0.759554 * mes_cos

Hay alerta si p >= 0.4839 (umbral que detecta al menos el 80 % de los lahares en la validación cruzada).

Las variables se calculan con `lahares_fuego.calcular_variables`:

| Variable | Definición |
|---|---|
| lluvia_mm | lluvia del día UTC D (mm) |
| lluvia_ayer | lluvia del día UTC D-1 |
| acum_Nd | suma de los últimos N días, incluido D (N = 2, 3, 5, 7, 14, 30) |
| max_diaria_7d | máximo diario de los últimos 7 días |
| dias_secos_previos | días seguidos con menos de 1 mm antes de D |
| api_k09 | API(t) = 0.9 API(t-1) + P(t), evaluado en D-1 |
| mes_sin, mes_cos | sen(2π·mes/12), cos(2π·mes/12) |

Los coeficientes no deben interpretarse uno por uno, porque las ventanas de lluvia están muy correlacionadas.
Entrenado con 2019-2023; versiones: {'python': '3.10.7', 'scikit-learn': '1.7.2', 'pandas': '2.3.3', 'numpy': '2.2.6'}.