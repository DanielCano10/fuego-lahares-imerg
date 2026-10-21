# fuego-lahares-imerg
Código y datos para el trabajo de graduación **"Uso de modelos de clasificación supervisada para estimar la ocurrencia de lahares secundarios en el Volcán de Fuego, Guatemala, a partir de precipitación acumulada estimada por GPM/IMERG** — Daniel Alexander Cano Pérez, Ingeniería en Ciencias y Sistemas, Universidad de San Carlos de Guatemala.

El modelo estima, para cada día, la probabilidad de que ocurra un lahar secundario en el Volcán de Fuego usando solo la lluvia estimada por satélite (NASA GPM/IMERG), que es gratuita y cubre todo el volcán.

## Resultados principales

Modelos comparados: regresión logística, bosque aleatorio y máquina de vectores de soporte. Entrenados con 2019–2023.
Modelo elegido: bosque aleatorio. Resultados obtenidos con Python 3.10.7 y las versiones de `requirements.txt`.

## Estructura
```
└── data/
   ├── raw/imerg/          lluvia diaria de NASA Giovanni (Final y Late)
   ├── raw/eventos/        catálogos de lahares por fuente (GVP, CONRED, X, sísmico, INSIVUMEH)
   └── procesado/          tabla diaria de lahares (la etiqueta), pluviómetro y días excluidos
```