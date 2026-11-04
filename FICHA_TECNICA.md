# Ficha técnica del modelo

Ficha técnica (model card, Mitchell et al., 2019) del modelo de ocurrencia de lahares secundarios en el Volcán de Fuego, Guatemala.

## Detalles del modelo

- **Autor:** Daniel Alexander Cano Pérez, Escuela de Ciencias y Sistemas, Facultad de Ingeniería, Universidad de San Carlos de Guatemala.
- **Versión:** 1.0.0 (2026).
- **Tipo de modelo:** clasificación binaria supervisada por día. Se compararon tres modelos, y el elegido fue un bosque aleatorio de 300 árboles, con profundidad máxima de 8 y mínimo 20 observaciones por hoja. También se publican la regresión logística (como ecuación) y la máquina de vectores de soporte.
- **Salida:** probabilidad de que ocurra al menos un lahar secundario en el volcán ese día, y una alerta cuando la probabilidad llega al umbral de 0.468.
- **Licencia:** código MIT y datos derivados CC BY 4.0.

## Uso previsto

- Investigación sobre la relación entre la lluvia y los lahares secundarios del Volcán de Fuego.
- Base para comparar con otros modelos o para mejorarlo con más datos.
- Apoyo complementario para identificar días de mayor probabilidad de lahar, siempre junto a la información oficial.

## Usos no adecuados

- **No es un sistema de alerta oficial y no ha sido validado por ninguna institución, por lo que no debe usarse como fundamento para decisiones de evacuación.** Las alertas oficiales son las del INSIVUMEH y la CONRED.
- No sirve para otros volcanes ni para otra zona, ya que se entrenó con la lluvia de una sola celda de IMERG sobre la cumbre del Volcán de Fuego.
- No sirve con lluvia de pluviómetros ni de otros productos satelitales, ya que aprendió con el sesgo propio de IMERG, que registra cerca de la mitad de la lluvia que mide el pluviómetro del volcán.
- No indica en qué barranca va a ocurrir el lahar ni de qué tamaño será.

## Datos de entrenamiento y evaluación

- **Lluvia:** GPM IMERG versión 07 diario, corrida Final para entrenar y probar, corrida Late para la evaluación de 2026. Celda de 0.1° (−90.95, 14.45, −90.85, 14.55), descargada de NASA Giovanni.
- **Etiqueta:** unión de seis fuentes de lahares, que son el Global Volcanism Program, CONRED, los boletines BEFGO publicados, publicaciones en X, el catálogo sísmico de Bejar Lopez et al. (2025) y el archivo de boletines del INSIVUMEH entregado por la Ley de Acceso a la Información Pública.
- **Entrenamiento:** 2019 a 2023, con 1,822 días y 301 con lahar.
- **Prueba:** enero de 2024 a septiembre de 2025, con 379 días y 89 con lahar.
- **Evaluación operativa:** octubre de 2025 a septiembre de 2026, con 156 días y 32 con lahar.

## Variables de entrada

13 variables que se calculan a partir de la lluvia diaria: la lluvia del día y del día anterior, los acumulados de 2, 3, 5, 7, 14 y 30 días, el máximo diario de 7 días, los días secos previos, el índice de precipitación antecedente y el seno y coseno del mes. Se necesitan por lo menos 30 días de lluvia antes de la fecha que se quiere estimar.

## Desempeño del bosque aleatorio

| Conjunto | PR-AUC (azar) | ROC-AUC | Sensibilidad | Precisión |
|---|---|---|---|---|
| Prueba 2024 a sep-2025 | 0.529 (0.235) | 0.833 | 0.820 | 0.487 |
| Operativa oct-2025 a sep-2026 | 0.762 (0.205) | 0.903 | 0.750 | 0.522 |

Con el umbral de 0.468, en la prueba detectó 73 de 89 lahares y dio 77 falsas alarmas en 290 días sin lahar.

## Limitaciones

- La mayor parte de la información está en la lluvia del mismo día. En la prueba, ordenar los días solo por esa lluvia dio una PR-AUC de 0.542, parecida a la del modelo.
- La mayoría de los lahares no detectados ocurrieron en días en que el satélite casi no registró lluvia.
- La etiqueta de 2024 y 2025 depende de un archivo de boletines incompleto, por lo que algunas falsas alarmas pueden ser lahares no registrados.
- La resolución diaria no permite usar la intensidad de la lluvia en intervalos cortos, y la lluvia después de las 18:00 hora local queda en el día siguiente.
- Los resultados del bosque aleatorio cambian un poco con otra versión de scikit-learn. Los valores de esta ficha se obtuvieron con Python 3.10.7, scikit-learn 1.7.2, pandas 2.3.3 y numpy 2.2.6.
- Si la NASA cambia la versión de IMERG, el modelo se debe volver a entrenar.

## Cómo citarlo

Ver `CITATION.cff`.
