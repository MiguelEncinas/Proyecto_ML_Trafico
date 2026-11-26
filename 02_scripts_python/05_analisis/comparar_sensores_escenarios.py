
from pathlib import Path
from collections import defaultdict
import xml.etree.ElementTree as ET
import csv

carpeta_proyecto = Path(__file__).resolve().parents[2]

carpeta = (
    carpeta_proyecto
    / "04_resultados"
    / "01_simulaciones_originales"
)

carpeta_pruebas = (
    carpeta_proyecto
    / "04_resultados"
    / "pruebas"
)

carpeta_pruebas.mkdir(parents=True, exist_ok=True)
escenarios = ["baja", "media", "alta"]

variables = [
    "meanOccupancy",
    "meanSpeed",
    "maxJamLengthInMeters",
    "meanTimeLoss"
]

resultados = []

def promedio(valores):
    return sum(valores) / len(valores) if valores else None

def formato(valor):
    return f"{valor:.2f}" if valor is not None else "N/D"

for escenario in escenarios:

    archivo = carpeta / f"{escenario}_salidas_sensores.xml"

    if not archivo.exists():
        raise FileNotFoundError(archivo.name)

    datos = defaultdict(lambda: defaultdict(list))

    for evento, elemento in ET.iterparse(
        archivo, events=("end",)
    ):
        if elemento.tag != "interval":
            continue

        sensor = elemento.get("id")

        if sensor is None:
            elemento.clear()
            continue

        for variable in variables:
            valor = elemento.get(variable)

            if valor is None:
                continue

            numero = float(valor)

            # SUMO puede usar valores negativos
            # para indicadores no disponibles.
            if numero >= 0:
                datos[sensor][variable].append(numero)

        elemento.clear()

    for sensor in sorted(datos):

        registro = {
            "escenario": escenario,
            "sensor": sensor,
            "ocupacion_media": promedio(
                datos[sensor]["meanOccupancy"]
            ),
            "velocidad_media_m_s": promedio(
                datos[sensor]["meanSpeed"]
            ),
            "cola_maxima_m": max(
                datos[sensor]["maxJamLengthInMeters"],
                default=None
            ),
            "tiempo_perdido_medio_s": promedio(
                datos[sensor]["meanTimeLoss"]
            )
        }

        resultados.append(registro)

print("\nCOMPARACION DE SENSORES E2")
print("=" * 70)

for escenario in escenarios:

    print(f"\nESCENARIO: {escenario.upper()}")
    print("-" * 70)

    for fila in resultados:
        if fila["escenario"] != escenario:
            continue

        print(
            f'{fila["sensor"]}: '
            f'Ocup={formato(fila["ocupacion_media"])}% | '
            f'Vel={formato(fila["velocidad_media_m_s"])} m/s | '
            f'ColaMax={formato(fila["cola_maxima_m"])} m'
        )

salida = carpeta_pruebas / "comparacion_sensores_escenarios_PRUEBA.csv"

with salida.open(
    "w", newline="", encoding="utf-8-sig"
) as archivo:

    campos = [
        "escenario",
        "sensor",
        "ocupacion_media",
        "velocidad_media_m_s",
        "cola_maxima_m",
        "tiempo_perdido_medio_s"
    ]

    escritor = csv.DictWriter(
        archivo, fieldnames=campos
    )
    escritor.writeheader()
    escritor.writerows(resultados)

print("\nARCHIVO GENERADO:", salida.name)
print("Filas generadas:", len(resultados))
print("COMPARACION FINALIZADA")
