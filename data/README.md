# Datos: fuentes, licencias y columnas

El **código** de este repositorio tiene licencia **MIT** (archivo `LICENSE`).
Los **datos derivados** que construí (tabla diaria, catálogos procesados) se publican bajo **CC BY 4.0**: se pueden usar citando este trabajo.
Los datos de terceros conservan las condiciones de su fuente original, que se detallan abajo.

| Archivo | Fuente | Condiciones |
|---|---|---|
| `data/raw/imerg/*IMERGDF*.csv` | NASA GES DISC, IMERG Final V07 diario (Huffman et al., 2023a, doi:10.5067/GPM/IMERGDF/DAY/07), descargado con NASA Giovanni | Datos públicos de la NASA; citar el conjunto de datos |
| `data/raw/imerg/*IMERGDL*.csv` | NASA GES DISC, IMERG Late V07 diario (Huffman et al., 2023b, doi:10.5067/GPM/IMERGDL/DAY/07) | Igual que el anterior |
| `data/raw/eventos/catalogo_gvp_lahares_fuego.csv` | Extracción propia de los boletines BGVN y reportes semanales del Global Volcanism Program, Smithsonian Institution (volcán 342090). Cada fila trae la URL del reporte | Citar al Global Volcanism Program |
| `data/raw/eventos/catalogo_conred_fuego.csv` | Clasificación propia de publicaciones de CONRED (conred.gob.gt) | Información pública; cada fila trae la URL |
| `data/raw/eventos/x_por_dia.csv` | Boletines publicados por las cuentas oficiales de INSIVUMEH y CONRED en X | Información pública institucional |
| `data/raw/eventos/catalogo_sismico_*.csv` | Bejar Lopez et al. (2025), *Lahar seismic monitoring dataset for Volcán de Fuego*, Mendeley Data, doi:10.17632/7dg667fkrd.1 | **CC BY 4.0**, citar a los autores |
| `data/raw/eventos/befgo_insivumeh_eventos.csv`, `data/procesado/befgo_laip_por_dia.csv`, `dias_eruptivos_excluir.csv`, `pluviometro_fuego_bvd.csv`, columna `ocurrencia_insivumeh_laip` | Extracción propia de los boletines BEFGO y BVD del INSIVUMEH, entregados por la Ley de Acceso a la Información Pública, resolución UIP-INSIVUMEH-2026-9-561 (solicitud UIP-546-2026) | Información pública (Decreto 57-2008). Es una **derivación no oficial**: la fuente oficial es el INSIVUMEH |

Los PDF originales de los boletines **no** se incluyen en este repositorio. Quien los necesite puede pedirlos al INSIVUMEH citando la resolución anterior.

## `data/procesado/tabla_diaria_lahares_fuego.csv` (una fila por día local, 2019-01-01 a 2026-09-19)

| Columna | Descripción |
|---|---|
| `fecha` | Día local de Guatemala (UTC−6) |
| `anio`, `mes` | Año y mes |
| `ocurrencia_union` | **Etiqueta usada**: 1 si cualquier fuente reporta lahar secundario ese día |
| `ocurrencia_recomendada` | 1 si lo reporta una fuente documental (GVP, CONRED ajustado, redes) |
| `ocurrencia_gvp` | 1 si lo reporta el Global Volcanism Program |
| `ocurrencia_conred_pub` / `ocurrencia_conred_ajust` | CONRED con la fecha de publicación / movida un día atrás |
| `ocurrencia_x`, `ocurrencia_insivumeh` | Boletines encontrados en X / boletines BEFGO recolectados de redes |
| `ocurrencia_sismica` | 1 si el catálogo sísmico de Bejar Lopez et al. (2025) registra lahar (solo ago-2018 a nov-2022) |
| `ocurrencia_insivumeh_laip` | 1 si hay boletín BEFGO de lahar secundario en el archivo entregado por INSIVUMEH |
| `n_boletines_laip`, `primera_hora_laip`, `barrancas_laip` | Cantidad de boletines, primera hora local y barrancas de ese día |
| `dia_eruptivo_excluir` | 1 si el lahar aparece en un boletín de erupción (posible lahar primario); el día no se usa |
| `confiabilidad_negativo` | `alta`, `media` o `baja`: qué tan seguro es que un 0 signifique "no hubo lahar" |
| `fuente`, `barrancas`, `url_gvp`, `titulo_conred`, ... | Trazabilidad de cada fuente |

## `data/procesado/pluviometro_fuego_bvd.csv`

| Columna | Descripción |
|---|---|
| `fecha_lluvia` | Día al que corresponde la lluvia (= `fecha_boletin` − 1) |
| `fecha_boletin` | Fecha del Boletín Vulcanológico Diario (publicado a las 07:00) |
| `lluvia_mm` | Precipitación pluvial reportada para el Volcán de Fuego |
| `fuente` | `pdftotext` (texto del PDF) u `ocr` (reconocimiento de caracteres) |
| `revisar` | 1 si el valor de OCR es dudoso; no se usa en las comparaciones |

**Qué archivos usa el notebook:** los dos CSV de `raw/imerg/`, `procesado/tabla_diaria_lahares_fuego.csv` (la etiqueta ya une todas las fuentes y trae los días eruptivos) y `procesado/pluviometro_fuego_bvd.csv`. Los catálogos de `raw/eventos/` y los otros dos de `procesado/` son las fuentes con las que se armó la tabla diaria; se dejan para que se pueda revisar de dónde sale cada lahar.
