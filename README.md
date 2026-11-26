# Proyecto de Machine Learning para la Simulación de Tráfico

## Descripción
Proyecto académico para el análisis del tráfico vehicular mediante SUMO y Python, basado en una red vial del entorno de las avenidas Javier Prado y Aviación, Lima, Perú.

## Objetivo
Simular diferentes condiciones de tráfico, recopilar datos mediante sensores virtuales y preparar una base estructurada para futuros modelos de Machine Learning.

## Herramientas
- Python
- SUMO (Simulation of Urban MObility)
- TraCI
- CSV y XML
- Git y GitHub

## Estructura del proyecto
- `01_simulacion_sumo/`: red vial, escenarios y configuración.
- `02_scripts_python/`: generación, auditoría, ejecución, procesamiento y análisis.
- `03_datos/`: datos originales, procesados y base de Machine Learning.
- `04_resultados/`: resultados históricos, repeticiones, extracciones y análisis.
- `05_modelos_ml/`: carpeta destinada a futuros modelos.
- `06_documentacion/`: documentación académica y verificaciones.

## Escenarios de simulación
Se consideran ocho escenarios diferenciados: baja demanda, demanda media, alta demanda, punta en Javier Prado, punta en Aviación, punta en túneles y dos escenarios asimétricos.

Cada escenario cuenta con tres semillas (42, 43 y 44), para un total de 24 simulaciones históricas.

## Datos para Machine Learning
La base principal se encuentra en `03_datos/03_base_ml/base_ampliada_ML.csv`.

Contiene 2880 registros y 35 columnas, obtenidos a partir de 10 sensores y 24 simulaciones, con intervalos de cinco minutos.

## Configuración de SUMO
El archivo principal es `01_simulacion_sumo/configuracion/simulacion.sumocfg`.

Desde la raíz del proyecto, se puede ejecutar con:

```powershell
sumo -c "01_simulacion_sumo/configuracion/simulacion.sumocfg"
```

Esta configuración utiliza rutas relativas y puede requerir SUMO instalado y disponible en el PATH.

## Estado del proyecto
Se ha organizado la estructura del proyecto, conservado los resultados históricos y preparado la base de Machine Learning. La configuración reorganizada de SUMO superó una prueba de carga inicial.

El entrenamiento y evaluación de modelos de Machine Learning corresponde a una fase posterior.

## Control de versiones
El archivo `.gitignore` excluye respaldos y resultados temporales sin eliminarlos de la computadora.

## Documentación
Los documentos académicos y registros de revisión están en `06_documentacion/`.
